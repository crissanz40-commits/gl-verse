"""Servidor HTTP para la API, el frontal y el backoffice."""

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
from urllib.parse import parse_qs, unquote, urlparse

from gl_verse.admin_auth import (
    AppSession,
    AppSessionStore,
    GoogleAuthError,
    GoogleAuthFlowStore,
    GoogleOIDCClient,
    GoogleOIDCConfig,
    upsert_google_user,
)
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
    """Expone el catálogo, OAuth y los recursos estáticos."""

    database_path: Path
    session_store: AppSessionStore
    flow_store: GoogleAuthFlowStore
    oidc_client: GoogleOIDCClient | None
    admin_emails: frozenset[str]

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/admin":
            self._redirect("/admin.html")
        elif path == "/api/health":
            self._send_json({"status": "ok"})
        elif path == "/api/catalog":
            self._send_catalog()
        elif path == "/api/auth/session":
            self._send_session()
        elif path == "/api/auth/google/start":
            self._start_google(parse_qs(parsed.query))
        elif path == "/api/admin/series":
            if self._require_admin():
                self._send_admin_series()
        elif path.startswith("/api/"):
            self._send_json({"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND)
        else:
            super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/auth/google":
            self._finish_google()
            return
        if path == "/api/auth/logout":
            session = self._require_session(require_csrf=True)
            if session:
                self.session_store.revoke(self._session_token())
                self._send_json(
                    {"status": "ok"},
                    headers={"Set-Cookie": self._expired_cookie("glv_session")},
                )
            return
        if path.startswith("/api/"):
            self._send_json({"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND)
        else:
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
        else:
            self._send_json({"error": "Método no permitido"}, HTTPStatus.METHOD_NOT_ALLOWED)

    def _start_google(self, query: dict[str, list[str]]) -> None:
        if self.oidc_client is None:
            self._send_json(
                {"error": "El acceso con Google todavía no está configurado"},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        requested_next = query.get("next", ["/"])[0]
        next_path = "/admin" if requested_next.startswith("/admin") else "/"
        state, flow = self.flow_store.create(next_path)
        self._send_json(
            {
                "clientId": self.oidc_client.config.client_id,
                "nonce": flow.nonce,
                "loginCsrf": state,
            },
            headers={"Set-Cookie": self._cookie("glv_login_csrf", state, 600)},
        )

    def _finish_google(self) -> None:
        if self.oidc_client is None:
            self._send_json({"error": "Google no está configurado"}, HTTPStatus.SERVICE_UNAVAILABLE)
            return
        try:
            form_navigation = self.headers.get("Content-Type", "").startswith(
                "application/x-www-form-urlencoded"
            )
            payload = self._read_form() if form_navigation else self._read_json()
            if not isinstance(payload, dict) or set(payload) != {"credential", "loginCsrf"}:
                raise ValueError
            credential = payload["credential"]
            state = payload["loginCsrf"]
            if not isinstance(credential, str) or not isinstance(state, str):
                raise TypeError
        except (ValueError, TypeError, json.JSONDecodeError):
            self._send_json({"error": "Respuesta de Google no válida"}, HTTPStatus.BAD_REQUEST)
            return
        cookie_state = self._cookie_value("glv_login_csrf")
        if not state or not cookie_state or not secrets.compare_digest(state, cookie_state):
            self._send_json({"error": "Protección CSRF de Google no válida"}, HTTPStatus.BAD_REQUEST)
            return
        flow = self.flow_store.consume(state)
        if flow is None:
            self._send_json({"error": "Inicio de sesión cancelado o caducado"}, HTTPStatus.BAD_REQUEST)
            return
        try:
            identity = self.oidc_client.verify(credential, flow.nonce)
            with closing(connect_database(self.database_path)) as connection:
                user = upsert_google_user(connection, identity, self.admin_emails)
        except GoogleAuthError as error:
            self._send_json({"error": str(error)}, HTTPStatus.UNAUTHORIZED)
            return
        except sqlite3.Error:
            self._send_json({"error": "No se pudo registrar la cuenta"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        token, _ = self.session_store.create(user)
        headers = {"Set-Cookie": self._cookie("glv_session", token, 28800)}
        if form_navigation:
            destination = "/admin.html" if user.role == "admin" else "/"
            self._send_auth_complete(destination, headers=headers)
        else:
            self._send_json(
                {"status": "ok", "nextPath": flow.next_path},
                headers=headers,
            )

    def _send_session(self) -> None:
        session_token = self._session_token()
        session = self.session_store.get(session_token)
        if session is None:
            self._send_json(
                {"authenticated": False, "googleConfigured": self.oidc_client is not None}
            )
            return
        user = session.user
        self._send_json(
            {
                "authenticated": True,
                "googleConfigured": True,
                "user": {
                    "email": user.email,
                    "name": user.display_name,
                    "pictureUrl": user.picture_url,
                    "role": user.role,
                },
                "csrfToken": session.csrf_token,
            }
        )

    def _admin_update_series(self, session: AppSession, series_id: str) -> None:
        try:
            payload = self._read_json()
            if not isinstance(payload, dict) or set(payload) != {"fields", "source"}:
                raise AdminCatalogError("La edición no tiene el formato esperado")
            with closing(connect_database(self.database_path)) as connection:
                result = update_series(
                    connection, session.user.subject, series_id, payload["fields"], payload["source"]
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

    def _admin_update_review(self, session: AppSession, series_id: str) -> None:
        try:
            payload = self._read_json()
            if not isinstance(payload, dict) or set(payload) != {"status"}:
                raise ValueError
            status = ReviewStatus(payload["status"])
            with closing(connect_database(self.database_path)) as connection:
                result = set_review(connection, session.user.subject, series_id, status)
        except UnknownSeriesError:
            self._send_json({"error": "Serie no encontrada"}, HTTPStatus.NOT_FOUND)
            return
        except (ValueError, TypeError, json.JSONDecodeError):
            self._send_json({"error": "Estado de revisión no válido"}, HTTPStatus.BAD_REQUEST)
            return
        except sqlite3.Error:
            self._send_json({"error": "No se pudo guardar la revisión"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self._send_json(result)

    def _send_catalog(self) -> None:
        try:
            with closing(connect_database(self.database_path)) as connection:
                payload = catalog_payload(connection)
        except sqlite3.Error:
            self._send_json({"error": "No se pudo consultar el catálogo"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self._send_json(payload)

    def _send_admin_series(self) -> None:
        try:
            with closing(connect_database(self.database_path)) as connection:
                payload = admin_series_payload(connection)
        except sqlite3.Error:
            self._send_json({"error": "No se pudo consultar el backoffice"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self._send_json({"series": payload})

    def _read_json(self) -> Any:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length < 1 or content_length > 65536:
            raise ValueError("Cuerpo JSON no válido")
        return json.loads(self.rfile.read(content_length))

    def _read_form(self) -> dict[str, str]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length < 1 or content_length > 65536:
            raise ValueError("Formulario no válido")
        values = parse_qs(self.rfile.read(content_length).decode("utf-8"), strict_parsing=True)
        return {key: items[0] for key, items in values.items() if len(items) == 1}

    def _session_token(self) -> str | None:
        return self._cookie_value("glv_session")

    def _cookie_value(self, name: str) -> str | None:
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        morsel = cookie.get(name)
        return morsel.value if morsel else None

    def _require_session(self, *, require_csrf: bool = False) -> AppSession | None:
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

    def _require_admin(self, *, require_csrf: bool = False) -> AppSession | None:
        session = self._require_session(require_csrf=require_csrf)
        if session is not None and session.user.role != "admin":
            self._send_json({"error": "Se requiere el rol admin"}, HTTPStatus.FORBIDDEN)
            return None
        return session

    def _cookie(self, name: str, value: str, max_age: int) -> str:
        secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
        return f"{name}={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}{secure}"

    def _expired_cookie(self, name: str) -> str:
        return f"{name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"

    def _redirect(self, location: str, *, headers: dict[str, str] | None = None) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()

    def _send_auth_complete(self, destination: str, *, headers: dict[str, str]) -> None:
        body = (
            "<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">"
            f"<meta http-equiv=\"refresh\" content=\"1; url={destination}\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>Acceso completado · GL Verse</title></head>"
            "<body><main><h1>Acceso completado</h1>"
            f"<p>Entrando en GL Verse… <a href=\"{destination}\">Continuar</a></p>"
            "</main></body></html>"
        ).encode()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK, *, headers: dict[str, str] | None = None) -> None:
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
        static_path = urlparse(self.path).path
        if static_path in {"/", "/admin", "/admin.html", "/index.html"} or static_path.endswith(
            (".js", ".css")
        ):
            self.send_header("Cache-Control", "no-cache, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://accounts.google.com/gsi/client; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://accounts.google.com/gsi/style; "
            "font-src https://fonts.gstatic.com; img-src 'self' https: data:; "
            "connect-src 'self' https://accounts.google.com/gsi/; frame-src https://accounts.google.com/gsi/; "
            "frame-ancestors 'none'; base-uri 'self'",
        )
        super().end_headers()


def create_web_server(
    database_path: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    web_root: str | Path = DEFAULT_WEB_ROOT,
    oidc_client: GoogleOIDCClient | None = None,
    admin_emails: frozenset[str] | None = None,
) -> ThreadingHTTPServer:
    """Crea el servidor sin bloquear para facilitar su uso y sus pruebas."""

    config = GoogleOIDCConfig.from_environment() if oidc_client is None else oidc_client.config
    configured_client = oidc_client or (GoogleOIDCClient(config) if config else None)

    class ConfiguredCatalogRequestHandler(CatalogRequestHandler):
        pass

    ConfiguredCatalogRequestHandler.database_path = Path(database_path)
    ConfiguredCatalogRequestHandler.session_store = AppSessionStore()
    ConfiguredCatalogRequestHandler.flow_store = GoogleAuthFlowStore()
    ConfiguredCatalogRequestHandler.oidc_client = configured_client
    ConfiguredCatalogRequestHandler.admin_emails = admin_emails if admin_emails is not None else (config.admin_emails if config else frozenset())
    handler = partial(ConfiguredCatalogRequestHandler, directory=str(web_root))
    return ThreadingHTTPServer((host, port), handler)


def serve_web(database_path: str | Path, *, host: str = "127.0.0.1", port: int = 8000) -> None:
    server = create_web_server(database_path, host=host, port=port)
    print(f"GL Verse disponible en http://{host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
