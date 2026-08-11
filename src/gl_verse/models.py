"""Entidades principales del universo GL."""

from dataclasses import dataclass
from datetime import date
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


class CastImportance(str, Enum):
    """Importancia de una actriz dentro del reparto de una serie."""

    LEAD = "lead"
    SUPPORTING = "supporting"
    GUEST = "guest"


class PairingRole(str, Enum):
    """Importancia de una pareja dentro de una serie."""

    MAIN = "main"
    SUPPORTING = "supporting"


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} no puede estar vacío")


def _require_distinct_pair(values: tuple[str, str], field_name: str) -> None:
    if len(values) != 2:
        raise ValueError(f"{field_name} debe contener exactamente dos elementos")

    for value in values:
        _require_text(value, field_name)

    if values[0] == values[1]:
        raise ValueError(f"{field_name} debe contener dos elementos distintos")


def _validate_image_reference(
    image_url: str | None,
    source_url: str | None,
    field_name: str,
) -> None:
    if (image_url is None) != (source_url is None):
        raise ValueError(f"{field_name} debe incluir la imagen y su fuente")

    for value in (image_url, source_url):
        if value is not None and not value.startswith(("https://", "http://")):
            raise ValueError(f"{field_name} debe usar URLs http:// o https://")


@dataclass(frozen=True, slots=True)
class Series:
    """Representa la información objetiva de una serie GL."""

    id: str
    title: str
    country: str
    release_year: int
    release_date: date | None = None
    original_title: str | None = None
    status: SeriesStatus = SeriesStatus.ANNOUNCED
    synopsis: str | None = None
    cover_image_url: str | None = None
    cover_image_source_url: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.title, "El título")
        _require_text(self.country, "El país")

        if self.release_year < 1900:
            raise ValueError("El año de estreno debe ser igual o posterior a 1900")

        if self.release_date is not None and self.release_date.year != self.release_year:
            raise ValueError("La fecha y el año de estreno deben coincidir")

        _validate_image_reference(
            self.cover_image_url,
            self.cover_image_source_url,
            "La portada",
        )


@dataclass(frozen=True, slots=True)
class Person:
    """Representa a una profesional relacionada con una producción GL."""

    id: str
    name: str
    stage_name: str | None = None
    nationality: str | None = None
    image_url: str | None = None
    image_source_url: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.name, "El nombre")
        _validate_image_reference(self.image_url, self.image_source_url, "La imagen")


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
    cast_importance: CastImportance | None = None

    def __post_init__(self) -> None:
        _require_text(self.series_id, "El identificador de la serie")
        _require_text(self.person_id, "El identificador de la persona")

        if self.character_id is not None:
            _require_text(self.character_id, "El identificador del personaje")

        if self.character_id is not None and self.role is not CreditRole.CAST:
            raise ValueError("Solo un crédito de reparto puede estar asociado a un personaje")

        if self.cast_importance is not None and self.role is not CreditRole.CAST:
            raise ValueError("Solo un crédito de reparto puede indicar importancia en el reparto")


@dataclass(frozen=True, slots=True)
class ActingPair:
    """Representa una pareja artística formada por dos personas reales."""

    id: str
    name: str
    person_ids: tuple[str, str]
    active_since: int | None = None
    image_url: str | None = None
    image_source_url: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.name, "El nombre")
        _require_distinct_pair(self.person_ids, "La pareja artística")

        if self.active_since is not None and self.active_since < 1900:
            raise ValueError("El año de inicio debe ser igual o posterior a 1900")

        _validate_image_reference(self.image_url, self.image_source_url, "La imagen")


@dataclass(frozen=True, slots=True)
class SeriesPairing:
    """Representa una pareja ficticia y su posible pareja artística."""

    id: str
    series_id: str
    character_ids: tuple[str, str]
    acting_pair_id: str | None = None
    role: PairingRole = PairingRole.MAIN

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.series_id, "El identificador de la serie")
        if self.acting_pair_id is not None:
            _require_text(self.acting_pair_id, "El identificador de la pareja artística")
        _require_distinct_pair(self.character_ids, "La pareja ficticia")
