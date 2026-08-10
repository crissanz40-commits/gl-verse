"""Servidor HTTP local para la API y el prototipo web."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from gl_verse.catalog_api import catalog_payload
from gl_verse.database import connect_database

DEFAULT_WEB_ROOT = Path(__file__).parents[2] / "web"


class CatalogRequestHandler(SimpleHTTPRequestHandler):
    """Expone el catálogo y sirve los recursos estáticos del frontal."""

    database_path: Path

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json({"status": "ok"})
            return
        if path == "/api/catalog":
            self._send_catalog()
            return
        if path.startswith("/api/"):
            self._send_json({"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND)
            return
        super().do_GET()

    def _send_catalog(self) -> None:
        try:
            with closing(connect_database(self.database_path)) as connection:
                payload = catalog_payload(connection)
        except sqlite3.Error:
            self._send_json(
                {"error": "No se pudo consultar el catálogo"},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return
        self._send_json(payload)

    def _send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def create_web_server(
    database_path: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    web_root: str | Path = DEFAULT_WEB_ROOT,
) -> ThreadingHTTPServer:
    """Crea el servidor sin bloquear para facilitar su uso y sus pruebas."""

    class ConfiguredCatalogRequestHandler(CatalogRequestHandler):
        pass

    ConfiguredCatalogRequestHandler.database_path = Path(database_path)
    handler = partial(ConfiguredCatalogRequestHandler, directory=str(web_root))
    return ThreadingHTTPServer((host, port), handler)


def serve_web(
    database_path: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """Sirve la aplicación hasta que el proceso recibe una interrupción."""
    server = create_web_server(database_path, host=host, port=port)
    print(f"GL Verse disponible en http://{host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
