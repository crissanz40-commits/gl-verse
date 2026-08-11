"""Estado editorial de las fichas del catálogo."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from gl_verse.database import initialize_database


class ReviewStatus(str, Enum):
    """Estado de la revisión manual de una ficha."""

    PENDING = "pending"
    APPROVED = "approved"


class UnknownSeriesError(LookupError):
    """Indica que se intentó revisar una serie inexistente."""


@dataclass(frozen=True, slots=True)
class SeriesReview:
    """Resultado persistido de una revisión editorial."""

    series_id: str
    status: ReviewStatus
    reviewed_at: str | None


def set_review_status(
    connection: sqlite3.Connection,
    series_id: str,
    status: ReviewStatus,
) -> SeriesReview:
    """Guarda el estado y devuelve la revisión resultante."""

    initialize_database(connection)
    if connection.execute("SELECT 1 FROM series WHERE id = ?", (series_id,)).fetchone() is None:
        raise UnknownSeriesError(series_id)

    reviewed_at = (
        datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        if status is ReviewStatus.APPROVED
        else None
    )
    connection.execute(
        """
        INSERT INTO series_review_status (series_id, status, reviewed_at)
        VALUES (?, ?, ?)
        ON CONFLICT(series_id) DO UPDATE SET
            status = excluded.status,
            reviewed_at = excluded.reviewed_at
        """,
        (series_id, status.value, reviewed_at),
    )
    connection.commit()
    return SeriesReview(series_id, status, reviewed_at)
