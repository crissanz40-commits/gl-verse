"""Fuentes y trazabilidad de los datos de GL Verse."""

from dataclasses import dataclass
from datetime import date
from enum import Enum


class SourceType(str, Enum):
    """Tipo de fuente consultada."""

    OFFICIAL = "official"
    PLATFORM = "platform"
    PRESS = "press"
    INTERVIEW = "interview"
    DATABASE = "database"
    COMMUNITY = "community"


class EntityType(str, Enum):
    """Entidad sobre la que una fuente aporta información."""

    SERIES = "series"
    PERSON = "person"
    CHARACTER = "character"
    ACTING_PAIR = "acting_pair"
    CHARACTER_PAIRING = "character_pairing"
    COMPANY = "company"
    PLATFORM = "platform"
    AVAILABILITY = "availability"
    COLLECTION = "collection"
    SEASON = "season"
    EPISODE = "episode"
    VIEWING_GUIDE = "viewing_guide"


class VerificationStatus(str, Enum):
    """Grado de comprobación de un dato."""

    VERIFIED = "verified"
    CORROBORATED = "corroborated"
    UNVERIFIED = "unverified"
    CONFLICTING = "conflicting"


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} no puede estar vacío")


def _validate_url(value: str) -> None:
    if not value.startswith(("https://", "http://")):
        raise ValueError("La URL de la fuente debe comenzar por http:// o https://")


@dataclass(frozen=True, slots=True)
class Source:
    """Representa una página, publicación o recurso consultado."""

    id: str
    title: str
    url: str
    source_type: SourceType
    publisher: str | None = None
    published_on: date | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.title, "El título")
        _validate_url(self.url)


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    """Indica qué fuente respalda un campo concreto y cuándo se revisó."""

    source_id: str
    entity_type: EntityType
    entity_id: str
    field_name: str
    checked_on: date
    status: VerificationStatus
    note: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.source_id, "El identificador de la fuente")
        _require_text(self.entity_id, "El identificador de la entidad")
        _require_text(self.field_name, "El nombre del campo")

    def needs_review(self, as_of: date, max_age_days: int = 180) -> bool:
        """Indica si el dato lleva demasiado tiempo sin comprobarse."""
        if max_age_days < 1:
            raise ValueError("La antigüedad máxima debe ser mayor que cero")

        return (as_of - self.checked_on).days > max_age_days
