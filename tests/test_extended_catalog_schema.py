import sqlite3

import pytest

from gl_verse.database import connect_database, initialize_database


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    yield database
    database.close()


def test_extended_catalog_tables_preserve_relationships(connection: sqlite3.Connection) -> None:
    connection.execute(
        "INSERT INTO companies (id, name) VALUES ('studio', 'Studio')"
    )
    connection.execute(
        """
        INSERT INTO series_companies (series_id, company_id, role)
        VALUES ('gap-2022', 'studio', 'producer')
        """
    )
    connection.execute(
        "INSERT INTO collections (id, title, kind) VALUES ('universe', 'Universe', 'franchise')"
    )
    connection.execute(
        "INSERT INTO collection_entries VALUES ('universe', 'gap-2022', 1)"
    )
    connection.execute(
        "INSERT INTO seasons (id, series_id, number) VALUES ('gap-s1', 'gap-2022', 1)"
    )
    connection.execute(
        """
        INSERT INTO episodes (id, season_id, number, kind)
        VALUES ('gap-e1', 'gap-s1', 1, 'regular')
        """
    )
    connection.execute(
        "INSERT INTO tags (id, name, category) VALUES ('romance', 'Romance', 'genre')"
    )
    connection.execute("INSERT INTO series_tags VALUES ('gap-2022', 'romance')")
    connection.execute(
        "INSERT INTO content_warnings (id, name) VALUES ('warning', 'Warning')"
    )
    connection.execute(
        "INSERT INTO series_content_warnings VALUES ('gap-2022', 'warning', 'low')"
    )
    connection.execute(
        """
        INSERT INTO viewing_guides (series_id, drama_level, ending_type)
        VALUES ('gap-2022', 'light', 'happy_ever_after')
        """
    )

    assert connection.execute("SELECT COUNT(*) FROM viewing_guides").fetchone()[0] == 1
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


@pytest.mark.parametrize(
    ("statement", "parameters"),
    [
        (
            "INSERT INTO viewing_guides VALUES (?, ?, ?, ?)",
            ("gap-2022", "extreme", "open", None),
        ),
        (
            "INSERT INTO viewing_guides VALUES (?, ?, ?, ?)",
            ("gap-2022", "light", "perfect", None),
        ),
        (
            "INSERT INTO seasons (id, series_id, number) VALUES (?, ?, ?)",
            ("invalid-season", "gap-2022", 0),
        ),
    ],
)
def test_extended_catalog_rejects_invalid_values(
    connection: sqlite3.Connection, statement: str, parameters: tuple[object, ...]
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(statement, parameters)


def test_version_nine_upgrades_without_losing_provenance() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection, target_version=9)
    connection.execute(
        """
        INSERT INTO catalog_sources (id, title, url, source_type)
        VALUES ('source', 'Source', 'https://example.com', 'official')
        """
    )
    connection.execute(
        """
        INSERT INTO provenance_records (
            source_id, entity_type, entity_id, field_name, checked_on, status
        ) VALUES ('source', 'series', 'gap-2022', 'title', '2026-08-11', 'verified')
        """
    )
    connection.commit()

    initialize_database(connection)

    assert connection.execute("SELECT COUNT(*) FROM provenance_records").fetchone()[0] == 1
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    connection.close()
