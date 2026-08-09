import sqlite3

import pytest

from gl_verse.database import connect_database, get_schema_version, initialize_database


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    database.execute("DELETE FROM series_pairings")
    database.execute("DELETE FROM credits")
    database.execute("DELETE FROM characters")
    database.execute("DELETE FROM acting_pairs")
    database.execute("DELETE FROM people")
    database.commit()
    yield database
    database.close()


def _insert_person(connection: sqlite3.Connection, person_id: str = "freen-sarocha") -> None:
    connection.execute(
        "INSERT INTO people (id, name, stage_name, nationality) VALUES (?, ?, ?, ?)",
        (person_id, "Sarocha Chankimha", "Freen", "Tailandesa"),
    )


def _insert_character(
    connection: sqlite3.Connection,
    character_id: str = "sam-gap",
    series_id: str = "gap-2022",
) -> None:
    connection.execute(
        "INSERT INTO characters (id, name, series_id) VALUES (?, ?, ?)",
        (character_id, "Sam", series_id),
    )


def test_version_two_database_upgrades_without_losing_gap() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection, target_version=2)

    initialize_database(connection)

    assert get_schema_version(connection) == 6
    assert connection.execute(
        "SELECT title FROM series WHERE id = ?",
        ("gap-2022",),
    ).fetchone()["title"] == "GAP: The Series"
    connection.close()


def test_cast_credit_connects_person_character_and_series(
    connection: sqlite3.Connection,
) -> None:
    _insert_person(connection)
    _insert_character(connection)

    connection.execute(
        """
        INSERT INTO credits (series_id, person_id, role, character_id)
        VALUES (?, ?, ?, ?)
        """,
        ("gap-2022", "freen-sarocha", "cast", "sam-gap"),
    )

    credit = connection.execute(
        "SELECT series_id, person_id, role, character_id FROM credits"
    ).fetchone()
    assert dict(credit) == {
        "series_id": "gap-2022",
        "person_id": "freen-sarocha",
        "role": "cast",
        "character_id": "sam-gap",
    }


def test_credit_rejects_an_unknown_person(connection: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO credits (series_id, person_id, role)
            VALUES (?, ?, ?)
            """,
            ("gap-2022", "unknown-person", "director"),
        )


def test_character_must_belong_to_credit_series(connection: sqlite3.Connection) -> None:
    _insert_person(connection)
    _insert_character(connection)
    connection.execute(
        """
        INSERT INTO series (id, title, country, release_year, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("another-series", "Otra serie", "Tailandia", 2024, "completed"),
    )

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO credits (series_id, person_id, role, character_id)
            VALUES (?, ?, ?, ?)
            """,
            ("another-series", "freen-sarocha", "cast", "sam-gap"),
        )


def test_non_cast_credit_cannot_reference_character(
    connection: sqlite3.Connection,
) -> None:
    _insert_person(connection)
    _insert_character(connection)

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO credits (series_id, person_id, role, character_id)
            VALUES (?, ?, ?, ?)
            """,
            ("gap-2022", "freen-sarocha", "director", "sam-gap"),
        )


def test_duplicate_credit_is_rejected(connection: sqlite3.Connection) -> None:
    _insert_person(connection)
    _insert_character(connection)
    values = ("gap-2022", "freen-sarocha", "cast", "sam-gap")
    statement = """
        INSERT INTO credits (series_id, person_id, role, character_id)
        VALUES (?, ?, ?, ?)
    """
    connection.execute(statement, values)

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(statement, values)
