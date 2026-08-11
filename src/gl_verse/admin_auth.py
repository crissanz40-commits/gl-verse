"""Autenticación local para el backoffice de GL Verse."""

from __future__ import annotations

import base64
import hashlib
import secrets
import sqlite3
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from gl_verse.database import initialize_database

PBKDF2_ITERATIONS = 600_000
SESSION_TTL = timedelta(hours=8)
_DUMMY_HASH = "pbkdf2_sha256$600000$MDAwMDAwMDAwMDAwMDAwMA==$" + (
    "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
)


class AdminUserError(ValueError):
    """Indica que un administrador no puede crearse."""


def _now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _timestamp(value: datetime | None = None) -> str:
    return (value or _now()).isoformat().replace("+00:00", "Z")


def hash_password(password: str) -> str:
    """Genera un hash PBKDF2-HMAC-SHA256 con sal aleatoria."""

    if len(password) < 12:
        raise AdminUserError("La contraseña debe tener al menos 12 caracteres")
    if len(password) > 1024:
        raise AdminUserError("La contraseña es demasiado larga")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return "$".join(
        (
            "pbkdf2_sha256",
            str(PBKDF2_ITERATIONS),
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(digest).decode("ascii"),
        )
    )


def verify_password(password: str, encoded: str) -> bool:
    """Compara una contraseña sin filtrar diferencias temporales del digest."""

    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password[:1024].encode("utf-8"),
            base64.b64decode(salt, validate=True),
            int(iterations),
        )
        return secrets.compare_digest(digest, base64.b64decode(expected, validate=True))
    except (ValueError, TypeError):
        return False


def create_admin(connection: sqlite3.Connection, username: str, password: str) -> None:
    """Crea un administrador local; nunca guarda la contraseña en claro."""

    initialize_database(connection)
    username = username.strip()
    if not username or len(username) > 80:
        raise AdminUserError("El usuario debe tener entre 1 y 80 caracteres")
    try:
        connection.execute(
            "INSERT INTO admin_users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, hash_password(password), _timestamp()),
        )
        connection.commit()
    except sqlite3.IntegrityError as error:
        raise AdminUserError(f"Ya existe el administrador {username!r}") from error


def authenticate(connection: sqlite3.Connection, username: str, password: str) -> bool:
    """Valida credenciales usando también un hash ficticio para usuarios inexistentes."""

    initialize_database(connection)
    row = connection.execute(
        "SELECT password_hash FROM admin_users WHERE username = ?", (username.strip(),)
    ).fetchone()
    return verify_password(password, row["password_hash"] if row else _DUMMY_HASH) and row is not None


@dataclass(frozen=True, slots=True)
class AdminSession:
    username: str
    csrf_token: str
    expires_at: datetime


class AdminSessionStore:
    """Sesiones efímeras ligadas al proceso local."""

    def __init__(self) -> None:
        self._sessions: dict[str, AdminSession] = {}
        self._lock = threading.Lock()

    def create(self, username: str) -> tuple[str, AdminSession]:
        token = secrets.token_urlsafe(32)
        session = AdminSession(username, secrets.token_urlsafe(24), _now() + SESSION_TTL)
        with self._lock:
            self._sessions[token] = session
        return token, session

    def get(self, token: str | None) -> AdminSession | None:
        if not token:
            return None
        now = _now()
        with self._lock:
            session = self._sessions.get(token)
            if session is None or session.expires_at <= now:
                self._sessions.pop(token, None)
                return None
            return session

    def revoke(self, token: str | None) -> None:
        if token:
            with self._lock:
                self._sessions.pop(token, None)
