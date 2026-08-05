import sqlite3

import pytest

from gl_verse.database import (
    SCHEMA_VERSION,
    connect_database,
    get_schema_version,
    initialize_database,
)
from gl_verse.models import Series, SeriesStatus
from gl_verse.repositories import SeriesAlreadyExistsError, SeriesRepository


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    database.execute("DELETE FROM series")
    database.commit()
    yield database
    database.close()


def test_database_uses_current_schema_version(connection: sqlite3.Connection) -> None:
    assert get_schema_version(connection) == SCHEMA_VERSION


def test_series_can_be_saved_and_recovered(connection: sqlite3.Connection) -> None:
    repository = SeriesRepository(connection)
    expected = Series(
        id="gap-test",
        title="GAP",
        original_title="ทฤษฎีสีชมพู",
        country="Tailandia",
        release_year=2022,
        status=SeriesStatus.COMPLETED,
        synopsis="Sam y Mon descubren que su relación puede cambiar sus vidas.",
    )

    repository.add(expected)

    assert repository.get("gap-test") == expected


def test_unknown_series_returns_none(connection: sqlite3.Connection) -> None:
    repository = SeriesRepository(connection)

    assert repository.get("unknown") is None


def test_series_are_listed_alphabetically(connection: sqlite3.Connection) -> None:
    repository = SeriesRepository(connection)
    repository.add(
        Series(
            id="gap-test",
            title="GAP",
            country="Tailandia",
            release_year=2022,
            status=SeriesStatus.COMPLETED,
        )
    )
    repository.add(
        Series(
            id="blank-test",
            title="Blank",
            country="Tailandia",
            release_year=2024,
            status=SeriesStatus.COMPLETED,
        )
    )

    assert [series.title for series in repository.list_all()] == ["Blank", "GAP"]


def test_duplicate_series_id_is_rejected(connection: sqlite3.Connection) -> None:
    repository = SeriesRepository(connection)
    series = Series(
        id="gap-test",
        title="GAP",
        country="Tailandia",
        release_year=2022,
        status=SeriesStatus.COMPLETED,
    )
    repository.add(series)

    with pytest.raises(SeriesAlreadyExistsError, match="gap-test"):
        repository.add(series)
