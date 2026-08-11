"""Lista, progreso y valoraciones privadas de cada usuario."""

from __future__ import annotations

import sqlite3
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any

from gl_verse.database import initialize_database


class PersonalLibraryError(ValueError):
    """Indica que una entrada personal no cumple el contrato."""


class UnknownSeriesError(PersonalLibraryError):
    """Indica que la serie solicitada no existe."""


class ViewingStatus(str, Enum):
    WANT_TO_WATCH = "want_to_watch"
    WATCHING = "watching"
    WATCHED = "watched"
    PAUSED = "paused"
    DROPPED = "dropped"


_FIELDS = {
    "status",
    "episodesWatched",
    "rating",
    "review",
    "startedOn",
    "completedOn",
}


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _optional_date(value: Any, field: str) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise PersonalLibraryError(f"{field} debe ser una fecha")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise PersonalLibraryError(f"{field} no es una fecha válida") from error


def _validated_payload(payload: Any, total_episodes: int) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != _FIELDS:
        raise PersonalLibraryError("La entrada personal no tiene el formato esperado")
    try:
        status = ViewingStatus(payload["status"])
    except (TypeError, ValueError) as error:
        raise PersonalLibraryError("Estado de visionado no válido") from error

    episodes = payload["episodesWatched"]
    if isinstance(episodes, bool) or not isinstance(episodes, int) or not 0 <= episodes <= 9999:
        raise PersonalLibraryError("El progreso debe ser un número entre 0 y 9999")
    if total_episodes and episodes > total_episodes:
        raise PersonalLibraryError(
            f"El progreso no puede superar los {total_episodes} episodios registrados"
        )

    rating = payload["rating"]
    if rating is not None and (
        isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 10
    ):
        raise PersonalLibraryError("La puntuación debe ser un entero entre 1 y 10")

    review = payload["review"]
    if review is not None and not isinstance(review, str):
        raise PersonalLibraryError("La opinión debe ser texto")
    review = review.strip() if review else None
    if review and len(review) > 2000:
        raise PersonalLibraryError("La opinión no puede superar los 2000 caracteres")

    started_on = _optional_date(payload["startedOn"], "La fecha de inicio")
    completed_on = _optional_date(payload["completedOn"], "La fecha de finalización")
    if started_on and completed_on and completed_on < started_on:
        raise PersonalLibraryError("La fecha de finalización no puede ser anterior al inicio")

    return {
        "status": status.value,
        "episodes_watched": episodes,
        "rating": rating,
        "review_text": review,
        "started_on": started_on,
        "completed_on": completed_on,
    }


def list_entries(connection: sqlite3.Connection, user_sub: str) -> list[dict[str, Any]]:
    """Lista únicamente las entradas privadas del usuario autenticado."""
    initialize_database(connection)
    rows = connection.execute(
        """
        SELECT entry.series_id, series.title, series.cover_image_url,
               entry.status, entry.episodes_watched, entry.rating, entry.review_text,
               entry.started_on, entry.completed_on, entry.created_at, entry.updated_at,
               COUNT(episode.id) AS total_episodes
        FROM user_series_entries AS entry
        JOIN series ON series.id = entry.series_id
        LEFT JOIN seasons AS season ON season.series_id = series.id
        LEFT JOIN episodes AS episode ON episode.season_id = season.id
        WHERE entry.user_sub = ?
        GROUP BY entry.user_sub, entry.series_id
        ORDER BY entry.updated_at DESC, series.title COLLATE NOCASE
        """,
        (user_sub,),
    ).fetchall()
    return [_entry_payload(row) for row in rows]


def save_entry(
    connection: sqlite3.Connection,
    user_sub: str,
    series_id: str,
    payload: Any,
) -> dict[str, Any]:
    """Crea o sustituye una entrada perteneciente al usuario autenticado."""
    initialize_database(connection)
    series = connection.execute(
        """
        SELECT series.id, COUNT(episode.id) AS total_episodes
        FROM series
        LEFT JOIN seasons AS season ON season.series_id = series.id
        LEFT JOIN episodes AS episode ON episode.season_id = season.id
        WHERE series.id = ?
        GROUP BY series.id
        """,
        (series_id,),
    ).fetchone()
    if series is None:
        raise UnknownSeriesError("Serie no encontrada")
    values = _validated_payload(payload, series["total_episodes"])
    now = _timestamp()
    with connection:
        connection.execute(
            """
            INSERT INTO user_series_entries (
                user_sub, series_id, status, episodes_watched, rating, review_text,
                started_on, completed_on, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_sub, series_id) DO UPDATE SET
                status = excluded.status,
                episodes_watched = excluded.episodes_watched,
                rating = excluded.rating,
                review_text = excluded.review_text,
                started_on = excluded.started_on,
                completed_on = excluded.completed_on,
                updated_at = excluded.updated_at
            """,
            (
                user_sub,
                series_id,
                values["status"],
                values["episodes_watched"],
                values["rating"],
                values["review_text"],
                values["started_on"],
                values["completed_on"],
                now,
                now,
            ),
        )
    return next(item for item in list_entries(connection, user_sub) if item["seriesId"] == series_id)


def delete_entry(connection: sqlite3.Connection, user_sub: str, series_id: str) -> bool:
    """Borra una entrada del usuario sin poder afectar las de otras cuentas."""
    initialize_database(connection)
    with connection:
        cursor = connection.execute(
            "DELETE FROM user_series_entries WHERE user_sub = ? AND series_id = ?",
            (user_sub, series_id),
        )
    return cursor.rowcount > 0


def _entry_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "seriesId": row["series_id"],
        "title": row["title"],
        "coverImageUrl": row["cover_image_url"],
        "status": row["status"],
        "episodesWatched": row["episodes_watched"],
        "totalEpisodes": row["total_episodes"],
        "rating": row["rating"],
        "review": row["review_text"],
        "startedOn": row["started_on"],
        "completedOn": row["completed_on"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }
