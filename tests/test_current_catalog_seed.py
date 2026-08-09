import pytest

from gl_verse.database import connect_database, get_schema_version, initialize_database


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    yield database
    database.close()


def test_version_four_upgrades_with_the_complete_current_catalog(connection) -> None:
    initialize_database(connection, target_version=4)

    assert connection.execute("SELECT COUNT(*) FROM series").fetchone()[0] == 1

    initialize_database(connection)

    assert get_schema_version(connection) == 6
    titles = connection.execute(
        "SELECT title FROM series ORDER BY title COLLATE NOCASE"
    ).fetchall()
    assert [row["title"] for row in titles] == [
        "23.5",
        "Affair",
        "GAP: The Series",
        "Pluto",
        "The Loyal Pin",
        "The Secret of Us",
    ]


def test_seed_connects_actresses_characters_and_artistic_pairs(connection) -> None:
    initialize_database(connection)

    counts = {
        table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("people", "characters", "credits", "acting_pairs", "series_pairings")
    }
    assert counts == {
        "people": 11,
        "characters": 13,
        "credits": 13,
        "acting_pairs": 5,
        "series_pairings": 6,
    }

    loyal_pin_cast = connection.execute(
        """
        SELECT people.stage_name, characters.name
        FROM credits
        JOIN people ON people.id = credits.person_id
        JOIN characters ON characters.id = credits.character_id
        WHERE credits.series_id = 'the-loyal-pin-2024'
        ORDER BY people.stage_name
        """
    ).fetchall()
    assert [dict(row) for row in loyal_pin_cast] == [
        {"stage_name": "Becky", "name": "Anin"},
        {"stage_name": "Freen", "name": "Pin"},
    ]


def test_ciize_is_supporting_cast_without_an_artistic_pair_in_23_5(connection) -> None:
    initialize_database(connection)

    ciize = connection.execute(
        """
        SELECT people.name, people.stage_name, credits.cast_importance, characters.name AS character
        FROM credits
        JOIN people ON people.id = credits.person_id
        JOIN characters ON characters.id = credits.character_id
        WHERE credits.series_id = '23-5-2024' AND people.id = 'ciize-rutricha'
        """
    ).fetchone()
    pairs = connection.execute(
        """
        SELECT COUNT(*)
        FROM acting_pairs
        WHERE first_person_id = 'ciize-rutricha' OR second_person_id = 'ciize-rutricha'
        """
    ).fetchone()[0]

    assert dict(ciize) == {
        "name": "Rutricha Phapakithi",
        "stage_name": "Ciize",
        "cast_importance": "supporting",
        "character": "Alpha",
    }
    assert pairs == 0


def test_freenbecky_history_includes_gap_and_the_loyal_pin(connection) -> None:
    initialize_database(connection)

    history = connection.execute(
        """
        SELECT series.title
        FROM series_pairings
        JOIN series ON series.id = series_pairings.series_id
        WHERE series_pairings.acting_pair_id = 'freenbecky'
        ORDER BY series.release_year, series.title
        """
    ).fetchall()

    assert [row["title"] for row in history] == ["GAP: The Series", "The Loyal Pin"]


def test_seed_is_safe_to_initialize_twice(connection) -> None:
    initialize_database(connection)
    expected = {
        table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("series", "people", "characters", "credits", "acting_pairs", "series_pairings")
    }

    initialize_database(connection)

    actual = {
        table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in expected
    }
    assert actual == expected


def test_seed_preserves_an_existing_series_record(connection) -> None:
    initialize_database(connection, target_version=4)
    connection.execute(
        """
        INSERT INTO series (id, title, country, release_year, status)
        VALUES ('pluto-2024', 'Mi ficha de Pluto', 'Tailandia', 2024, 'completed')
        """
    )
    connection.commit()

    initialize_database(connection)

    title = connection.execute(
        "SELECT title FROM series WHERE id = 'pluto-2024'"
    ).fetchone()["title"]
    assert title == "Mi ficha de Pluto"
