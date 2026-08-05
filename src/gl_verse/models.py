"""Entidades principales del universo GL."""

from dataclasses import dataclass
from enum import Enum


class SeriesStatus(str, Enum):
    """Estado de publicación de una serie."""

    ANNOUNCED = "announced"
    AIRING = "airing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CreditRole(str, Enum):
    """Función profesional de una persona en una serie."""

    CAST = "cast"
    DIRECTOR = "director"
    WRITER = "writer"
    PRODUCER = "producer"


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} no puede estar vacío")


@dataclass(frozen=True, slots=True)
class Series:
    """Representa la información objetiva de una serie GL."""

    id: str
    title: str
    country: str
    release_year: int
    original_title: str | None = None
    status: SeriesStatus = SeriesStatus.ANNOUNCED
    synopsis: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.title, "El título")
        _require_text(self.country, "El país")

        if self.release_year < 1900:
            raise ValueError("El año de estreno debe ser igual o posterior a 1900")


@dataclass(frozen=True, slots=True)
class Person:
    """Representa a una profesional relacionada con una producción GL."""

    id: str
    name: str
    stage_name: str | None = None
    nationality: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.name, "El nombre")


@dataclass(frozen=True, slots=True)
class Character:
    """Representa un personaje perteneciente a una serie."""

    id: str
    name: str
    series_id: str

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.name, "El nombre")
        _require_text(self.series_id, "El identificador de la serie")


@dataclass(frozen=True, slots=True)
class Credit:
    """Relaciona una persona con su función y personaje en una serie."""

    series_id: str
    person_id: str
    role: CreditRole
    character_id: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.series_id, "El identificador de la serie")
        _require_text(self.person_id, "El identificador de la persona")

        if self.character_id is not None:
            _require_text(self.character_id, "El identificador del personaje")

        if self.character_id is not None and self.role is not CreditRole.CAST:
            raise ValueError("Solo un crédito de reparto puede estar asociado a un personaje")
