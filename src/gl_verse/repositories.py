"""Repositorios para guardar y consultar el dominio de GL Verse."""

import sqlite3
from datetime import date

from gl_verse.models import Series, SeriesStatus


class SeriesAlreadyExistsError(ValueError):
    """Indica que ya existe una serie con el mismo identificador."""


class SeriesRepository:
    """Persistencia SQLite para series."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, series: Series) -> None:
        """Guarda una serie nueva."""
        try:
            with self._connection:
                self._connection.execute(
                    """
                    INSERT INTO series (
                        id,
                        title,
                        country,
                        release_year,
                        release_date,
                        original_title,
                        status,
                        synopsis,
                        cover_image_url,
                        cover_image_source_url
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        series.id,
                        series.title,
                        series.country,
                        series.release_year,
                        series.release_date.isoformat() if series.release_date else None,
                        series.original_title,
                        series.status.value,
                        series.synopsis,
                        series.cover_image_url,
                        series.cover_image_source_url,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise SeriesAlreadyExistsError(
                f"Ya existe una serie con el identificador {series.id!r}"
            ) from error

    def get(self, series_id: str) -> Series | None:
        """Recupera una serie por su identificador."""
        row = self._connection.execute(
            """
            SELECT id, title, country, release_year, release_date, original_title, status, synopsis,
                   cover_image_url, cover_image_source_url
            FROM series
            WHERE id = ?
            """,
            (series_id,),
        ).fetchone()

        return self._to_series(row) if row is not None else None

    def list_all(self) -> list[Series]:
        """Devuelve todas las series ordenadas por título."""
        rows = self._connection.execute(
            """
            SELECT id, title, country, release_year, release_date, original_title, status, synopsis,
                   cover_image_url, cover_image_source_url
            FROM series
            ORDER BY title COLLATE NOCASE
            """
        ).fetchall()

        return [self._to_series(row) for row in rows]

    @staticmethod
    def _to_series(row: sqlite3.Row) -> Series:
        return Series(
            id=row["id"],
            title=row["title"],
            country=row["country"],
            release_year=row["release_year"],
            release_date=date.fromisoformat(row["release_date"]) if row["release_date"] else None,
            original_title=row["original_title"],
            status=SeriesStatus(row["status"]),
            synopsis=row["synopsis"],
            cover_image_url=row["cover_image_url"],
            cover_image_source_url=row["cover_image_source_url"],
        )
