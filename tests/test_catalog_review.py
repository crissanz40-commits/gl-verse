import sqlite3

import pytest

from gl_verse.catalog_review import ReviewStatus, UnknownSeriesError, set_review_status
from gl_verse.database import connect_database, initialize_database


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    yield database
    database.close()


def test_series_review_can_be_approved_and_reopened(connection: sqlite3.Connection) -> None:
    approved = set_review_status(connection, "gap-2022", ReviewStatus.APPROVED)

    assert approved.status is ReviewStatus.APPROVED
    assert approved.reviewed_at is not None
    assert tuple(
        connection.execute(
            "SELECT status, reviewed_at FROM series_review_status WHERE series_id = ?",
            ("gap-2022",),
        ).fetchone()
    ) == ("approved", approved.reviewed_at)

    pending = set_review_status(connection, "gap-2022", ReviewStatus.PENDING)

    assert pending.reviewed_at is None
    assert tuple(
        connection.execute(
            "SELECT status, reviewed_at FROM series_review_status WHERE series_id = ?",
            ("gap-2022",),
        ).fetchone()
    ) == ("pending", None)


def test_unknown_series_cannot_be_reviewed(connection: sqlite3.Connection) -> None:
    with pytest.raises(UnknownSeriesError, match="missing"):
        set_review_status(connection, "missing", ReviewStatus.APPROVED)


def test_review_status_constraints_are_enforced(connection: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO series_review_status VALUES (?, ?, ?)",
            ("gap-2022", "approved", None),
        )


def test_version_ten_upgrades_without_marking_series_as_reviewed() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection, target_version=10)
    series_before = connection.execute("SELECT COUNT(*) FROM series").fetchone()[0]

    initialize_database(connection)

    assert connection.execute("SELECT COUNT(*) FROM series").fetchone()[0] == series_before
    assert connection.execute("SELECT COUNT(*) FROM series_review_status").fetchone()[0] == 0
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    connection.close()
