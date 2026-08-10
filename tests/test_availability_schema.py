import sqlite3

import pytest

from gl_verse.database import connect_database, initialize_database


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    database.execute(
        "INSERT INTO platforms (id, name, website_url) VALUES (?, ?, ?)",
        ("youtube", "YouTube", "https://www.youtube.com"),
    )
    yield database
    database.close()


def test_availability_keeps_territories_and_subtitles_separate(connection) -> None:
    for territory, language in (("ES", "es"), ("US", "en")):
        connection.execute(
            """
            INSERT INTO availability (
                series_id, platform_id, territory, access_model, official_url
            ) VALUES (?, ?, ?, ?, ?)
            """,
            ("gap-2022", "youtube", territory, "free", f"https://example.com/{territory}"),
        )
        connection.execute(
            """
            INSERT INTO availability_subtitles (
                series_id, platform_id, territory, language
            ) VALUES (?, ?, ?, ?)
            """,
            ("gap-2022", "youtube", territory, language),
        )

    rows = connection.execute(
        """
        SELECT availability.territory, subtitle.language
        FROM availability
        JOIN availability_subtitles AS subtitle USING (series_id, platform_id, territory)
        ORDER BY availability.territory
        """
    ).fetchall()

    assert [tuple(row) for row in rows] == [("ES", "es"), ("US", "en")]


def test_availability_rejects_unknown_series_and_invalid_values(connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO availability (
                series_id, platform_id, territory, access_model, official_url
            ) VALUES ('unknown', 'youtube', 'ES', 'free', 'https://example.com/watch')
            """
        )

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO availability (
                series_id, platform_id, territory, access_model, official_url
            ) VALUES ('gap-2022', 'youtube', 'spain', 'free', 'https://example.com/watch')
            """
        )


def test_deleting_availability_removes_its_subtitles(connection) -> None:
    connection.execute(
        """
        INSERT INTO availability (series_id, platform_id, territory, access_model, official_url)
        VALUES ('gap-2022', 'youtube', 'GLOBAL', 'free', 'https://example.com/watch')
        """
    )
    connection.execute(
        """
        INSERT INTO availability_subtitles (series_id, platform_id, territory, language)
        VALUES ('gap-2022', 'youtube', 'GLOBAL', 'en')
        """
    )

    connection.execute(
        """
        DELETE FROM availability
        WHERE series_id = 'gap-2022' AND platform_id = 'youtube' AND territory = 'GLOBAL'
        """
    )

    assert connection.execute("SELECT COUNT(*) FROM availability_subtitles").fetchone()[0] == 0
