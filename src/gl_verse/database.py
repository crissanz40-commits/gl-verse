"""Conexión y migraciones de la base de datos SQLite."""

import sqlite3
from importlib import resources
from pathlib import Path

_MIGRATIONS = {
    1: "001_initial_schema.sql",
    2: "002_seed_gap.sql",
    3: "003_people_characters_credits.sql",
    4: "004_cast_images_and_series_pairings.sql",
    5: "005_seed_current_catalog.sql",
    6: "006_catalog_import_provenance.sql",
    7: "007_series_release_date.sql",
    8: "008_platforms_and_availability.sql",
    9: "009_character_pairings.sql",
    10: "010_extended_catalog.sql",
    11: "011_series_review_status.sql",
    12: "012_admin_backoffice.sql",
    13: "013_google_identity_roles.sql",
    14: "014_personal_series_library.sql",
}
SCHEMA_VERSION = max(_MIGRATIONS)


def connect_database(path: str | Path = "data/gl_verse.db") -> sqlite3.Connection:
    """Abre una conexión SQLite y activa la integridad referencial."""
    database_path = str(path)

    if database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(
    connection: sqlite3.Connection,
    target_version: int = SCHEMA_VERSION,
) -> None:
    """Aplica en orden las migraciones pendientes hasta la versión indicada."""
    current_version = get_schema_version(connection)

    if target_version < current_version:
        raise ValueError("No se puede migrar la base de datos a una versión anterior")

    if target_version > SCHEMA_VERSION:
        raise ValueError("La versión solicitada todavía no existe")

    for version in range(current_version + 1, target_version + 1):
        _apply_migration(connection, version)


def get_schema_version(connection: sqlite3.Connection) -> int:
    """Devuelve la versión del esquema guardada por SQLite."""
    row = connection.execute("PRAGMA user_version").fetchone()
    return int(row[0])


def _apply_migration(connection: sqlite3.Connection, version: int) -> None:
    migration_name = _MIGRATIONS[version]
    migration = (
        resources.files("gl_verse")
        .joinpath("migrations", migration_name)
        .read_text(encoding="utf-8")
    )
    script = f"""
    BEGIN IMMEDIATE;
    {migration}
    PRAGMA user_version = {version};
    COMMIT;
    """

    try:
        connection.executescript(script)
    except sqlite3.Error:
        if connection.in_transaction:
            connection.rollback()
        raise
