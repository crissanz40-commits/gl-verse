import sqlite3

import pytest

from gl_verse.database import connect_database, get_schema_version, initialize_database
from gl_verse.models import SeriesStatus
from gl_verse.repositories import SeriesRepository


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    yield database
    database.close()


def test_gap_is_added_when_database_upgrades_from_version_one(
    connection: sqlite3.Connection,
) -> None:
    initialize_database(connection, target_version=1)
    repository = SeriesRepository(connection)

    assert get_schema_version(connection) == 1
    assert repository.get("gap-2022") is None

    initialize_database(connection)

    gap = repository.get("gap-2022")
    assert get_schema_version(connection) == 2
    assert gap is not None
    assert gap.title == "GAP: The Series"
    assert gap.original_title == "ทฤษฎีสีชมพู"
    assert gap.country == "Tailandia"
    assert gap.release_year == 2022
    assert gap.status is SeriesStatus.COMPLETED


def test_gap_migration_is_idempotent(connection: sqlite3.Connection) -> None:
    initialize_database(connection)
    initialize_database(connection)

    count = connection.execute(
        "SELECT COUNT(*) FROM series WHERE id = ?",
        ("gap-2022",),
    ).fetchone()[0]

    assert count == 1


def test_gap_migration_does_not_overwrite_an_existing_record(
    connection: sqlite3.Connection,
) -> None:
    initialize_database(connection, target_version=1)
    connection.execute(
        """
        INSERT INTO series (
            id, title, country, release_year, original_title, status, synopsis
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "gap-2022",
            "Mi ficha de GAP",
            "Tailandia",
            2022,
            "ทฤษฎีสีชมพู",
            "completed",
            None,
        ),
    )
    connection.commit()

    initialize_database(connection)

    title = connection.execute(
        "SELECT title FROM series WHERE id = ?",
        ("gap-2022",),
    ).fetchone()[0]
    assert title == "Mi ficha de GAP"
