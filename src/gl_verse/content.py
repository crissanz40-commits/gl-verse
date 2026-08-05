"""Estructura narrativa de las producciones GL."""

from dataclasses import dataclass
from datetime import date
from enum import Enum


class CollectionKind(str, Enum):
    """Tipo de agrupación entre varias series."""

    ANTHOLOGY = "anthology"
    FRANCHISE = "franchise"
    SHARED_UNIVERSE = "shared_universe"


class EpisodeKind(str, Enum):
    """Tipo de episodio."""

    REGULAR = "regular"
    SPECIAL = "special"


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} no puede estar vacío")


def _require_positive(value: int, field_name: str) -> None:
    if value < 1:
        raise ValueError(f"{field_name} debe ser mayor que cero")


@dataclass(frozen=True, slots=True)
class SeriesCollection:
    """Agrupa varias series dentro de una antología o universo común."""

    id: str
    title: str
    kind: CollectionKind
    description: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.title, "El título")


@dataclass(frozen=True, slots=True)
class CollectionEntry:
    """Coloca una serie dentro de una colección y establece su orden."""

    collection_id: str
    series_id: str
    position: int

    def __post_init__(self) -> None:
        _require_text(self.collection_id, "El identificador de la colección")
        _require_text(self.series_id, "El identificador de la serie")
        _require_positive(self.position, "La posición")


@dataclass(frozen=True, slots=True)
class Season:
    """Representa una temporada perteneciente a una serie."""

    id: str
    series_id: str
    number: int
    title: str | None = None
    release_year: int | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.series_id, "El identificador de la serie")
        _require_positive(self.number, "El número de temporada")

        if self.release_year is not None and self.release_year < 1900:
            raise ValueError("El año de estreno debe ser igual o posterior a 1900")


@dataclass(frozen=True, slots=True)
class Episode:
    """Representa un episodio perteneciente a una temporada."""

    id: str
    season_id: str
    number: int
    title: str | None = None
    kind: EpisodeKind = EpisodeKind.REGULAR
    air_date: date | None = None
    duration_minutes: int | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.season_id, "El identificador de la temporada")
        _require_positive(self.number, "El número de episodio")

        if self.duration_minutes is not None:
            _require_positive(self.duration_minutes, "La duración")
