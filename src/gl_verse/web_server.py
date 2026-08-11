"""Servidor HTTP local para la API, el frontal y el backoffice."""

from __future__ import annotations

import json
import secrets
import sqlite3
from contextlib import closing
from functools import partial
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from gl_verse.admin_auth import AdminSession, AdminSessionStore, authenticate
from gl_verse.admin_catalog import (
    AdminCatalogError,
    admin_series_payload,
    set_review,
    update_series,
)
from gl_verse.catalog_api import catalog_payload
from gl_verse.catalog_review import ReviewStatus, UnknownSeriesError
from gl_verse.database import connect_database

DEFAULT_WEB_ROOT = Path(__file__).parents[2] / "web"


class CatalogRequestHandler(SimpleHTTPRequestHandler):
    """Expone el catálogo y sirve los recursos estáticos del frontal."""

    database_path: Path
    session_store: AdminSessionStore

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/admin":
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/admin.html")
            self.end_headers()
            return
        if path == "/api/health":
            self._send_json({"status": "ok"})
            return
        if path == "/api/catalog":
            self._send_catalog()
            return
        if path == "/api/admin/session":
            session = self._require_admin()
            if session:
                self._send_json({"username": session.username, "csrfToken": session.csrf_token})
            return
        if path == "/api/admin/series":
            session = self._require_admin()
            if session:
                self._send_admin_series()
            return
        if path.startswith("/api/"):
            self._send_json({"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND)
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/admin/login":
            self._login()
            return
        if path == "/api/admin/logout":
            session = self._require_admin(require_csrf=True)
            if session:
                self.session_store.revoke(self._session_token())
                self._send_json(
                    {"status": "ok"},
                    headers={
                        "Set-Cookie": "glv_admin=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0"
                    },
                )
            return
        if path.startswith("/api/"):
            self._send_json({"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND)
            return
        self._send_json({"error": "Método no permitido"}, HTTPStatus.METHOD_NOT_ALLOWED)

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        parts = path.split("/")
        if len(parts) in {5, 6} and parts[1:4] == ["api", "admin", "series"]:
            session = self._require_admin(require_csrf=True)
            if session is None:
                return
            series_id = unquote(parts[4])
            if len(parts) == 6 and parts[5] == "review-status":
                self._admin_update_review(session, series_id)
                return
            if len(parts) == 5:
                self._admin_update_series(session, series_id)
                return
        if path.startswith("/api/"):
            self._send_json({"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND)
            return
        self._send_json({"error": "Método no permitido"}, HTTPStatus.METHOD_NOT_ALLOWED)

    def _login(self) -> None:
        if not self._is_loopback():
            self._send_json(
                {"error": "El backoffice solo admite conexiones locales"},
                HTTPStatus.FORBIDDEN,
            )
            return
        try:
            payload = self._read_json()
            if not isinstance(payload, dict) or set(payload) != {"username", "password"}:
                raise ValueError
            username, password = payload["username"], payload["password"]
            if not isinstance(username, str) or not isinstance(password, str):
                raise TypeError
        except (ValueError, TypeError, json.JSONDecodeError):
            self._send_json({"error": "Credenciales no válidas"}, HTTPStatus.BAD_REQUEST)
            return
        try:
            with closing(connect_database(self.database_path)) as connection:
                valid = authenticate(connection, username, password)
        except sqlite3.Error:
            self._send_json({"error": "No se pudo iniciar sesión"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        if not valid:
            self._send_json({"error": "Credenciales incorrectas"}, HTTPStatus.UNAUTHORIZED)
            return
        token, session = self.session_store.create(username.strip())
        self._send_json(
            {"username": session.username, "csrfToken": session.csrf_token},
            headers={
                "Set-Cookie": (
                    f"glv_admin={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=28800"
                )
            },
        )

    def _admin_update_series(self, session: AdminSession, series_id: str) -> None:
        try:
            payload = self._read_json()
            if not isinstance(payload, dict) or set(payload) != {"fields", "source"}:
                raise AdminCatalogError("La edición no tiene el formato esperado")
            with closing(connect_database(self.database_path)) as connection:
                result = update_series(
                    connection,
                    session.username,
                    series_id,
                    payload["fields"],
                    payload["source"],
                )
        except UnknownSeriesError:
            self._send_json({"error": "Serie no encontrada"}, HTTPStatus.NOT_FOUND)
            return
        except (AdminCatalogError, ValueError, TypeError, json.JSONDecodeError) as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        except sqlite3.Error:
            self._send_json({"error": "No se pudo guardar la ficha"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self._send_json(result)

    def _admin_update_review(self, session: AdminSession, series_id: str) -> None:
        try:
            payload = self._read_json()
            if not isinstance(payload, dict) or set(payload) != {"status"}:
                raise ValueError
            status = ReviewStatus(payload["status"])
            with closing(connect_database(self.database_path)) as connection:
                result = set_review(connection, session.username, series_id, status)
        except UnknownSeriesError:
            self._send_json({"error": "Serie no encontrada"}, HTTPStatus.NOT_FOUND)
            return
        except (ValueError, TypeError, json.JSONDecodeError):
            self._send_json({"error": "Estado de revisión no válido"}, HTTPStatus.BAD_REQUEST)
            return
        except sqlite3.Error:
            self._send_json(
                {"error": "No se pudo guardar la revisión"},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return
        self._send_json(result)

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

    def _send_admin_series(self) -> None:
        try:
            with closing(connect_database(self.database_path)) as connection:
                payload = admin_series_payload(connection)
        except sqlite3.Error:
            self._send_json(
                {"error": "No se pudo consultar el backoffice"},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return
        self._send_json({"series": payload})

    def _read_json(self) -> Any:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length < 1 or content_length > 65536:
            raise ValueError("Cuerpo JSON no válido")
        return json.loads(self.rfile.read(content_length))

    def _is_loopback(self) -> bool:
        return self.client_address[0] in {"127.0.0.1", "::1"}

    def _session_token(self) -> str | None:
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        morsel = cookie.get("glv_admin")
        return morsel.value if morsel else None

    def _require_admin(self, *, require_csrf: bool = False) -> AdminSession | None:
        if not self._is_loopback():
            self._send_json(
                {"error": "Acceso administrativo local únicamente"},
                HTTPStatus.FORBIDDEN,
            )
            return None
        session = self.session_store.get(self._session_token())
        if session is None:
            self._send_json({"error": "Autenticación requerida"}, HTTPStatus.UNAUTHORIZED)
            return None
        if require_csrf and not secrets.compare_digest(
            self.headers.get("X-GL-Verse-CSRF", ""), session.csrf_token
        ):
            self._send_json({"error": "Token CSRF no válido"}, HTTPStatus.FORBIDDEN)
            return None
        return session

    def _send_json(
        self,
        payload: Any,
        status: HTTPStatus = HTTPStatus.OK,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src https://fonts.gstatic.com; img-src 'self' https: data:; "
            "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'",
        )
        super().end_headers()


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
    ConfiguredCatalogRequestHandler.session_store = AdminSessionStore()
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
