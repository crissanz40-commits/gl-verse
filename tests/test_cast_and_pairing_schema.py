import sqlite3

import pytest

from gl_verse.database import connect_database, get_schema_version, initialize_database


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    yield database
    database.close()


def _insert_person(
    connection: sqlite3.Connection,
    person_id: str,
    name: str,
) -> None:
    connection.execute(
        """
        INSERT INTO people (
            id, name, stage_name, nationality, image_url, image_source_url
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            person_id,
            name,
            name,
            "Tailandesa",
            f"https://images.example/{person_id}.jpg",
            f"https://example.com/{person_id}",
        ),
    )


def _insert_character_and_credit(
    connection: sqlite3.Connection,
    series_id: str,
    person_id: str,
    character_id: str,
    importance: str = "lead",
) -> None:
    connection.execute(
        "INSERT INTO characters (id, name, series_id) VALUES (?, ?, ?)",
        (character_id, character_id, series_id),
    )
    connection.execute(
        """
        INSERT INTO credits (
            series_id, person_id, role, character_id, cast_importance
        )
        VALUES (?, ?, 'cast', ?, ?)
        """,
        (series_id, person_id, character_id, importance),
    )


def _insert_series(connection: sqlite3.Connection, series_id: str, title: str) -> None:
    connection.execute(
        """
        INSERT INTO series (id, title, country, release_year, status)
        VALUES (?, ?, 'Tailandia', 2026, 'completed')
        """,
        (series_id, title),
    )


def _insert_acting_pair(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        INSERT INTO acting_pairs (
            id, name, first_person_id, second_person_id, active_since,
            image_url, image_source_url
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "freenbecky",
            "FreenBecky",
            "freen-sarocha",
            "becky-armstrong",
            2022,
            "https://images.example/freenbecky.jpg",
            "https://example.com/freenbecky",
        ),
    )


def test_version_three_upgrades_without_losing_gap() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection, target_version=3)

    initialize_database(connection)

    assert get_schema_version(connection) == 4
    gap = connection.execute(
        "SELECT title, cover_image_url FROM series WHERE id = 'gap-2022'"
    ).fetchone()
    assert dict(gap) == {"title": "GAP: The Series", "cover_image_url": None}
    connection.close()


def test_series_and_actress_images_require_a_source(
    connection: sqlite3.Connection,
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO series (
                id, title, country, release_year, status, cover_image_url
            )
            VALUES ('invalid-image', 'Invalid', 'Tailandia', 2026, 'announced', ?)
            """,
            ("https://images.example/invalid.jpg",),
        )

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO people (id, name, image_url) VALUES (?, ?, ?)",
            ("invalid-person", "Invalid", "https://images.example/invalid.jpg"),
        )


def test_actress_can_work_in_a_series_without_a_pair(
    connection: sqlite3.Connection,
) -> None:
    _insert_person(connection, "cize-apichaya", "Cize")
    _insert_series(connection, "solo-series", "Solo Series")
    _insert_character_and_credit(
        connection,
        "solo-series",
        "cize-apichaya",
        "solo-character",
        importance="supporting",
    )

    credit = connection.execute(
        """
        SELECT cast_importance
        FROM credits
        WHERE series_id = 'solo-series' AND person_id = 'cize-apichaya'
        """
    ).fetchone()
    pairings = connection.execute(
        "SELECT COUNT(*) FROM series_pairings WHERE series_id = 'solo-series'"
    ).fetchone()[0]

    assert credit["cast_importance"] == "supporting"
    assert pairings == 0


def test_pair_history_is_derived_from_its_series_pairings(
    connection: sqlite3.Connection,
) -> None:
    _insert_person(connection, "freen-sarocha", "Freen")
    _insert_person(connection, "becky-armstrong", "Becky")
    _insert_acting_pair(connection)

    _insert_character_and_credit(connection, "gap-2022", "freen-sarocha", "sam-gap")
    _insert_character_and_credit(connection, "gap-2022", "becky-armstrong", "mon-gap")
    connection.execute(
        """
        INSERT INTO series_pairings (
            id, series_id, acting_pair_id, first_character_id,
            second_character_id, role
        )
        VALUES ('sam-mon-gap', 'gap-2022', 'freenbecky', 'sam-gap', 'mon-gap', 'main')
        """
    )

    _insert_series(connection, "second-series", "Second Series")
    _insert_character_and_credit(
        connection,
        "second-series",
        "freen-sarocha",
        "first-character",
    )
    _insert_character_and_credit(
        connection,
        "second-series",
        "becky-armstrong",
        "second-character",
    )
    connection.execute(
        """
        INSERT INTO series_pairings (
            id, series_id, acting_pair_id, first_character_id,
            second_character_id, role
        )
        VALUES (
            'second-pairing', 'second-series', 'freenbecky',
            'first-character', 'second-character', 'supporting'
        )
        """
    )

    history = connection.execute(
        """
        SELECT series.title, series_pairings.role
        FROM series_pairings
        JOIN series ON series.id = series_pairings.series_id
        WHERE series_pairings.acting_pair_id = 'freenbecky'
        ORDER BY series.release_year, series.title
        """
    ).fetchall()

    assert [dict(row) for row in history] == [
        {"title": "GAP: The Series", "role": "main"},
        {"title": "Second Series", "role": "supporting"},
    ]


def test_same_actresses_cannot_create_a_duplicate_pair(
    connection: sqlite3.Connection,
) -> None:
    _insert_person(connection, "freen-sarocha", "Freen")
    _insert_person(connection, "becky-armstrong", "Becky")
    _insert_acting_pair(connection)

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO acting_pairs (
                id, name, first_person_id, second_person_id
            )
            VALUES (?, ?, ?, ?)
            """,
            ("beckyfreen", "BeckyFreen", "becky-armstrong", "freen-sarocha"),
        )


def test_series_pairing_must_match_the_actual_cast(
    connection: sqlite3.Connection,
) -> None:
    _insert_person(connection, "freen-sarocha", "Freen")
    _insert_person(connection, "becky-armstrong", "Becky")
    _insert_acting_pair(connection)
    _insert_character_and_credit(connection, "gap-2022", "freen-sarocha", "sam-gap")
    connection.execute(
        "INSERT INTO characters (id, name, series_id) VALUES (?, ?, ?)",
        ("unknown-gap", "Unknown", "gap-2022"),
    )

    with pytest.raises(sqlite3.IntegrityError, match="reparto"):
        connection.execute(
            """
            INSERT INTO series_pairings (
                id, series_id, acting_pair_id, first_character_id,
                second_character_id, role
            )
            VALUES (
                'invalid-pairing', 'gap-2022', 'freenbecky',
                'sam-gap', 'unknown-gap', 'main'
            )
            """
        )
