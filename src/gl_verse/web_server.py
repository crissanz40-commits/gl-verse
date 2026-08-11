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
from urllib.parse import unquote, urlparse

from gl_verse.catalog_api import catalog_payload
from gl_verse.catalog_review import ReviewStatus, UnknownSeriesError, set_review_status
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

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        parts = path.split("/")
        if len(parts) == 5 and parts[1:3] == ["api", "series"] and parts[4] == "review-status":
            self._update_review_status(unquote(parts[3]))
            return
        if path.startswith("/api/"):
            self._send_json({"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND)
            return
        self._send_json({"error": "Método no permitido"}, HTTPStatus.METHOD_NOT_ALLOWED)

    def _update_review_status(self, series_id: str) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length < 1 or content_length > 4096:
                raise ValueError
            payload = json.loads(self.rfile.read(content_length))
            if not isinstance(payload, dict) or set(payload) != {"status"}:
                raise ValueError
            status = ReviewStatus(payload["status"])
        except (ValueError, TypeError, json.JSONDecodeError):
            self._send_json(
                {"error": "Estado de revisión no válido"},
                HTTPStatus.BAD_REQUEST,
            )
            return

        try:
            with closing(connect_database(self.database_path)) as connection:
                review = set_review_status(connection, series_id, status)
        except UnknownSeriesError:
            self._send_json({"error": "Serie no encontrada"}, HTTPStatus.NOT_FOUND)
            return
        except sqlite3.Error:
            self._send_json(
                {"error": "No se pudo guardar la revisión"},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return

        self._send_json(
            {
                "seriesId": review.series_id,
                "status": review.status.value,
                "reviewedAt": review.reviewed_at,
            }
        )

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
