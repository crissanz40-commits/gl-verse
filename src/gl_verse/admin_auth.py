"""Identidad Google, roles y sesiones locales de GL Verse."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import sqlite3
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from gl_verse.database import initialize_database

GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
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
    client_secret: str
    redirect_uri: str
    admin_emails: frozenset[str]

    @classmethod
    def from_environment(cls) -> GoogleOIDCConfig | None:
        client_id = os.environ.get("GL_VERSE_GOOGLE_CLIENT_ID", "").strip()
        client_secret = os.environ.get("GL_VERSE_GOOGLE_CLIENT_SECRET", "").strip()
        if not client_id or not client_secret:
            return None
        redirect_uri = os.environ.get(
            "GL_VERSE_GOOGLE_REDIRECT_URI",
            "http://127.0.0.1:8000/api/auth/google/callback",
        ).strip()
        admin_emails = frozenset(
            email.strip().casefold()
            for email in os.environ.get("GL_VERSE_ADMIN_EMAILS", "").split(",")
            if email.strip()
        )
        return cls(client_id, client_secret, redirect_uri, admin_emails)


@dataclass(frozen=True, slots=True)
class GoogleIdentity:
    subject: str
    email: str
    display_name: str | None = None
    picture_url: str | None = None


class GoogleOIDCClient:
    """Construye el flujo Authorization Code y valida el ID token firmado."""

    def __init__(self, config: GoogleOIDCConfig) -> None:
        self.config = config

    def authorization_url(self, state: str, nonce: str, code_challenge: str) -> str:
        query = urlencode(
            {
                "client_id": self.config.client_id,
                "redirect_uri": self.config.redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "nonce": nonce,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "prompt": "select_account",
            }
        )
        return f"{GOOGLE_AUTHORIZATION_ENDPOINT}?{query}"

    def exchange_and_verify(self, code: str, code_verifier: str, nonce: str) -> GoogleIdentity:
        body = urlencode(
            {
                "code": code,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "redirect_uri": self.config.redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
            }
        ).encode("ascii")
        request = UrlRequest(
            GOOGLE_TOKEN_ENDPOINT,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                token_data = json.load(response)
        except (HTTPError, URLError, TimeoutError, ValueError) as error:
            raise GoogleAuthError("Google no pudo completar el intercambio de credenciales") from error
        id_token_value = token_data.get("id_token")
        if not isinstance(id_token_value, str):
            raise GoogleAuthError("Google no devolvió una identidad válida")
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import id_token

            claims = id_token.verify_oauth2_token(
                id_token_value,
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
    code_verifier: str
    next_path: str
    expires_at: datetime


class GoogleAuthFlowStore:
    def __init__(self) -> None:
        self._flows: dict[str, AuthFlow] = {}
        self._lock = threading.Lock()

    def create(self, next_path: str) -> tuple[str, AuthFlow, str]:
        state = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        flow = AuthFlow(secrets.token_urlsafe(32), verifier, next_path, _now() + FLOW_TTL)
        with self._lock:
            self._flows[state] = flow
        return state, flow, challenge

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
