"""Conexión e inicialización de la base de datos SQLite."""

import sqlite3
from pathlib import Path

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS series (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    country TEXT NOT NULL,
    release_year INTEGER NOT NULL CHECK (release_year >= 1900),
    original_title TEXT,
    status TEXT NOT NULL CHECK (
        status IN ('announced', 'airing', 'completed', 'cancelled')
    ),
    synopsis TEXT
);

CREATE INDEX IF NOT EXISTS idx_series_title ON series(title);
CREATE INDEX IF NOT EXISTS idx_series_country ON series(country);
CREATE INDEX IF NOT EXISTS idx_series_release_year ON series(release_year);
"""


def connect_database(path: str | Path = "data/gl_verse.db") -> sqlite3.Connection:
    """Abre una conexión SQLite y activa la integridad referencial."""
    database_path = str(path)

    if database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    """Crea la versión inicial del esquema si todavía no existe."""
    connection.executescript(_SCHEMA)
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    connection.commit()


def get_schema_version(connection: sqlite3.Connection) -> int:
    """Devuelve la versión del esquema guardada por SQLite."""
    row = connection.execute("PRAGMA user_version").fetchone()
    return int(row[0])
