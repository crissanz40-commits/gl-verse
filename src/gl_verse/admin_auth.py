"""Identidad Google, roles y sesiones locales de GL Verse."""

from __future__ import annotations

import os
import secrets
import sqlite3
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from gl_verse.database import initialize_database

SESSION_TTL = timedelta(hours=8)
FLOW_TTL = timedelta(minutes=10)


class GoogleAuthError(ValueError):
    """Indica que el inicio de sesión con Google no se pudo completar."""


def _now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _timestamp(value: datetime | None = None) -> str:
    return (value or _now()).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class GoogleOIDCConfig:
    client_id: str
    admin_emails: frozenset[str]

    @classmethod
    def from_environment(cls) -> GoogleOIDCConfig | None:
        client_id = os.environ.get("GL_VERSE_GOOGLE_CLIENT_ID", "").strip()
        if not client_id:
            return None
        admin_emails = frozenset(
            email.strip().casefold()
            for email in os.environ.get("GL_VERSE_ADMIN_EMAILS", "").split(",")
            if email.strip()
        )
        return cls(client_id, admin_emails)


@dataclass(frozen=True, slots=True)
class GoogleIdentity:
    subject: str
    email: str
    display_name: str | None = None
    picture_url: str | None = None


class GoogleOIDCClient:
    """Valida el ID token firmado que entrega Google Identity Services."""

    def __init__(self, config: GoogleOIDCConfig) -> None:
        self.config = config

    def verify(self, credential: str, nonce: str) -> GoogleIdentity:
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import id_token

            claims = id_token.verify_oauth2_token(
                credential,
                Request(),
                self.config.client_id,
            )
        except Exception as error:
            raise GoogleAuthError("El token de identidad de Google no es válido") from error
        if claims.get("nonce") != nonce:
            raise GoogleAuthError("El inicio de sesión de Google no coincide con la solicitud")
        if claims.get("email_verified") is not True:
            raise GoogleAuthError("Google no ha verificado este correo")
        subject, email = claims.get("sub"), claims.get("email")
        if not isinstance(subject, str) or not isinstance(email, str):
            raise GoogleAuthError("El token de Google no incluye la identidad esperada")
        return GoogleIdentity(subject, email, claims.get("name"), claims.get("picture"))


@dataclass(frozen=True, slots=True)
class AuthFlow:
    nonce: str
    next_path: str
    expires_at: datetime


class GoogleAuthFlowStore:
    def __init__(self) -> None:
        self._flows: dict[str, AuthFlow] = {}
        self._lock = threading.Lock()

    def create(self, next_path: str) -> tuple[str, AuthFlow]:
        state = secrets.token_urlsafe(32)
        flow = AuthFlow(secrets.token_urlsafe(32), next_path, _now() + FLOW_TTL)
        with self._lock:
            self._flows[state] = flow
        return state, flow

    def consume(self, state: str) -> AuthFlow | None:
        with self._lock:
            flow = self._flows.pop(state, None)
        return flow if flow and flow.expires_at > _now() else None


@dataclass(frozen=True, slots=True)
class AppUser:
    subject: str
    email: str
    display_name: str | None
    picture_url: str | None
    role: str


def upsert_google_user(
    connection: sqlite3.Connection,
    identity: GoogleIdentity,
    admin_emails: frozenset[str],
) -> AppUser:
    """Registra el acceso; solo la lista de bootstrap puede promocionar a admin."""

    initialize_database(connection)
    email = identity.email.strip().casefold()
    existing = connection.execute(
        "SELECT role FROM app_users WHERE google_sub = ?", (identity.subject,)
    ).fetchone()
    role = "admin" if email in admin_emails or (existing and existing["role"] == "admin") else "viewer"
    now = _timestamp()
    with connection:
        connection.execute(
            """
            INSERT INTO app_users (
                google_sub, email, display_name, picture_url, role, created_at, last_login_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(google_sub) DO UPDATE SET
                email = excluded.email,
                display_name = excluded.display_name,
                picture_url = excluded.picture_url,
                role = excluded.role,
                last_login_at = excluded.last_login_at
            """,
            (
                identity.subject,
                email,
                identity.display_name,
                identity.picture_url,
                role,
                now,
                now,
            ),
        )
    return AppUser(identity.subject, email, identity.display_name, identity.picture_url, role)


@dataclass(frozen=True, slots=True)
class AppSession:
    user: AppUser
    csrf_token: str
    expires_at: datetime


class AppSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, AppSession] = {}
        self._lock = threading.Lock()

    def create(self, user: AppUser) -> tuple[str, AppSession]:
        token = secrets.token_urlsafe(32)
        session = AppSession(user, secrets.token_urlsafe(24), _now() + SESSION_TTL)
        with self._lock:
            self._sessions[token] = session
        return token, session

    def get(self, token: str | None) -> AppSession | None:
        if not token:
            return None
        with self._lock:
            session = self._sessions.get(token)
            if session is None or session.expires_at <= _now():
                self._sessions.pop(token, None)
                return None
            return session

    def revoke(self, token: str | None) -> None:
        if token:
            with self._lock:
                self._sessions.pop(token, None)
