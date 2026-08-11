"""Operaciones trazables del backoffice sobre fichas de series."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, date, datetime
from typing import Any

from gl_verse.catalog_review import ReviewStatus, UnknownSeriesError
from gl_verse.database import initialize_database
from gl_verse.models import Series, SeriesStatus
from gl_verse.provenance import Source, SourceType, VerificationStatus

_SERIES_FIELDS = {
    "title": "title",
    "originalTitle": "original_title",
    "country": "country",
    "releaseYear": "release_year",
    "releaseDate": "release_date",
    "status": "status",
    "synopsis": "synopsis",
    "coverImageUrl": "cover_image_url",
    "coverImageSourceUrl": "cover_image_source_url",
}
_GUIDE_FIELDS = {
    "dramaLevel": "drama_level",
    "endingType": "ending_type",
    "endingNote": "ending_note",
}
_DRAMA_LEVELS = {"zero_drama", "light", "moderate", "high"}
_ENDING_TYPES = {
    "happy_ever_after",
    "happy_for_now",
    "bittersweet",
    "open",
    "sad",
    "tragic",
    "unknown",
}


class AdminCatalogError(ValueError):
    """Indica una edición administrativa inválida."""


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def admin_series_payload(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Devuelve los campos editables de todas las fichas."""

    initialize_database(connection)
    rows = connection.execute(
        """
        SELECT series.*, guide.drama_level, guide.ending_type, guide.ending_note,
               COALESCE(review.status, 'pending') AS review_status, review.reviewed_at
        FROM series
        LEFT JOIN viewing_guides AS guide ON guide.series_id = series.id
        LEFT JOIN series_review_status AS review ON review.series_id = series.id
        ORDER BY series.title COLLATE NOCASE
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "originalTitle": row["original_title"],
            "country": row["country"],
            "releaseYear": row["release_year"],
            "releaseDate": row["release_date"],
            "status": row["status"],
            "synopsis": row["synopsis"],
            "coverImageUrl": row["cover_image_url"],
            "coverImageSourceUrl": row["cover_image_source_url"],
            "dramaLevel": row["drama_level"],
            "endingType": row["ending_type"],
            "endingNote": row["ending_note"],
            "reviewStatus": row["review_status"],
            "reviewedAt": row["reviewed_at"],
        }
        for row in rows
    ]


def update_series(
    connection: sqlite3.Connection,
    username: str,
    series_id: str,
    fields: Any,
    source_data: Any,
) -> dict[str, Any]:
    """Actualiza una ficha, registra fuente/procedencia y reabre su revisión."""

    initialize_database(connection)
    if not isinstance(fields, dict) or not fields:
        raise AdminCatalogError("Debe indicarse al menos un campo")
    unknown = set(fields) - (_SERIES_FIELDS.keys() | _GUIDE_FIELDS.keys())
    if unknown:
        raise AdminCatalogError(f"Campos no editables: {', '.join(sorted(unknown))}")
    if not isinstance(source_data, dict):
        raise AdminCatalogError("Los cambios objetivos requieren una fuente")

    row = connection.execute("SELECT * FROM series WHERE id = ?", (series_id,)).fetchone()
    if row is None:
        raise UnknownSeriesError(series_id)
    guide = connection.execute(
        "SELECT * FROM viewing_guides WHERE series_id = ?", (series_id,)
    ).fetchone()

    current = {public: row[column] for public, column in _SERIES_FIELDS.items()}
    current.update(
        {
            public: guide[column] if guide else None
            for public, column in _GUIDE_FIELDS.items()
        }
    )
    changes = {key: value for key, value in fields.items() if current.get(key) != value}
    if not changes:
        raise AdminCatalogError("La ficha ya contiene esos valores")

    merged = {**current, **changes}
    _validate_fields(series_id, merged, changes)
    source, verification = _parse_source(series_id, source_data)
    checked_on = datetime.now(UTC).date().isoformat()
    changed_at = _timestamp()

    with connection:
        connection.execute(
            """
            INSERT INTO catalog_sources (id, title, url, source_type, publisher, published_on)
            VALUES (?, ?, ?, ?, ?, NULL)
            """,
            (source.id, source.title, source.url, source.source_type.value, source.publisher),
        )
        series_changes = {k: v for k, v in changes.items() if k in _SERIES_FIELDS}
        if series_changes:
            assignments = ", ".join(f"{_SERIES_FIELDS[key]} = ?" for key in series_changes)
            connection.execute(
                f"UPDATE series SET {assignments} WHERE id = ?",
                (*series_changes.values(), series_id),
            )
        guide_changes = {k: v for k, v in changes.items() if k in _GUIDE_FIELDS}
        if guide_changes:
            if merged["dramaLevel"] is None and merged["endingType"] is None:
                connection.execute("DELETE FROM viewing_guides WHERE series_id = ?", (series_id,))
            else:
                connection.execute(
                    """
                    INSERT INTO viewing_guides (series_id, drama_level, ending_type, ending_note)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(series_id) DO UPDATE SET
                        drama_level = excluded.drama_level,
                        ending_type = excluded.ending_type,
                        ending_note = excluded.ending_note
                    """,
                    (
                        series_id,
                        merged["dramaLevel"],
                        merged["endingType"],
                        merged["endingNote"],
                    ),
                )
        for field_name in changes:
            entity_type = "viewing_guide" if field_name in _GUIDE_FIELDS else "series"
            connection.execute(
                """
                INSERT INTO provenance_records (
                    source_id, entity_type, entity_id, field_name, checked_on, status, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source.id,
                    entity_type,
                    series_id,
                    _GUIDE_FIELDS.get(field_name, _SERIES_FIELDS.get(field_name)),
                    checked_on,
                    verification.value,
                    "Cambio realizado desde el backoffice.",
                ),
            )
        connection.execute(
            """
            INSERT INTO series_review_status (series_id, status, reviewed_at)
            VALUES (?, 'pending', NULL)
            ON CONFLICT(series_id) DO UPDATE SET status = 'pending', reviewed_at = NULL
            """,
            (series_id,),
        )
        _audit(connection, username, series_id, changed_at, changes, source.id)
    return next(item for item in admin_series_payload(connection) if item["id"] == series_id)


def set_review(
    connection: sqlite3.Connection,
    username: str,
    series_id: str,
    status: ReviewStatus,
) -> dict[str, Any]:
    """Aprueba o reabre una ficha y registra la acción administrativa."""

    initialize_database(connection)
    if connection.execute("SELECT 1 FROM series WHERE id = ?", (series_id,)).fetchone() is None:
        raise UnknownSeriesError(series_id)
    reviewed_at = _timestamp() if status is ReviewStatus.APPROVED else None
    with connection:
        connection.execute(
            """
            INSERT INTO series_review_status (series_id, status, reviewed_at)
            VALUES (?, ?, ?)
            ON CONFLICT(series_id) DO UPDATE SET
                status = excluded.status, reviewed_at = excluded.reviewed_at
            """,
            (series_id, status.value, reviewed_at),
        )
        _audit(
            connection,
            username,
            series_id,
            _timestamp(),
            {"reviewStatus": status.value},
            None,
        )
    return {"seriesId": series_id, "status": status.value, "reviewedAt": reviewed_at}


def _parse_source(series_id: str, value: dict[str, Any]) -> tuple[Source, VerificationStatus]:
    required = {"title", "url", "sourceType", "verificationStatus"}
    if not required <= value.keys() or set(value) - (required | {"publisher"}):
        raise AdminCatalogError("La fuente no tiene el formato esperado")
    try:
        source = Source(
            id=f"admin-{series_id}-{uuid.uuid4().hex}",
            title=value["title"],
            url=value["url"],
            source_type=SourceType(value["sourceType"]),
            publisher=value.get("publisher") or None,
        )
        verification = VerificationStatus(value["verificationStatus"])
    except (AttributeError, TypeError, ValueError) as error:
        raise AdminCatalogError(str(error)) from error
    return source, verification


def _validate_fields(series_id: str, values: dict[str, Any], changes: dict[str, Any]) -> None:
    try:
        Series(
            id=series_id,
            title=values["title"],
            original_title=values["originalTitle"],
            country=values["country"],
            release_year=int(values["releaseYear"]),
            release_date=(date.fromisoformat(values["releaseDate"]) if values["releaseDate"] else None),
            status=SeriesStatus(values["status"]),
            synopsis=values["synopsis"],
            cover_image_url=values["coverImageUrl"],
            cover_image_source_url=values["coverImageSourceUrl"],
        )
    except (TypeError, ValueError) as error:
        raise AdminCatalogError(str(error)) from error
    if changes.keys() & _GUIDE_FIELDS.keys():
        if values["dramaLevel"] is None and values["endingType"] is None:
            if values["endingNote"] is not None:
                raise AdminCatalogError("Una nota de final requiere guía de visionado")
            return
        if values["dramaLevel"] not in _DRAMA_LEVELS:
            raise AdminCatalogError("Nivel de drama no válido")
        if values["endingType"] not in _ENDING_TYPES:
            raise AdminCatalogError("Tipo de final no válido")


def _audit(
    connection: sqlite3.Connection,
    username: str,
    series_id: str,
    changed_at: str,
    changes: dict[str, Any],
    source_id: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO admin_audit_log (
            username, series_id, changed_at, changes_json, source_id
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (username, series_id, changed_at, json.dumps(changes, ensure_ascii=False), source_id),
    )
