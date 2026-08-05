"""Metadatos para descubrir y elegir series GL."""

from dataclasses import dataclass
from enum import Enum


class TagCategory(str, Enum):
    """Categoría de una etiqueta descriptiva."""

    GENRE = "genre"
    TROPE = "trope"
    THEME = "theme"
    TONE = "tone"


class DramaLevel(str, Enum):
    """Intensidad dramática general de una serie."""

    ZERO_DRAMA = "zero_drama"
    LIGHT = "light"
    MODERATE = "moderate"
    HIGH = "high"


class EndingType(str, Enum):
    """Resultado emocional del final de la pareja principal."""

    HAPPY_EVER_AFTER = "happy_ever_after"
    HAPPY_FOR_NOW = "happy_for_now"
    BITTERSWEET = "bittersweet"
    OPEN = "open"
    SAD = "sad"
    TRAGIC = "tragic"
    UNKNOWN = "unknown"


class WarningSeverity(str, Enum):
    """Intensidad orientativa de una advertencia de contenido."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} no puede estar vacío")


@dataclass(frozen=True, slots=True)
class Tag:
    """Representa un género, tropo, tema o tono reutilizable."""

    id: str
    name: str
    category: TagCategory

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.name, "El nombre")


@dataclass(frozen=True, slots=True)
class SeriesTag:
    """Asocia una etiqueta descriptiva con una serie."""

    series_id: str
    tag_id: str

    def __post_init__(self) -> None:
        _require_text(self.series_id, "El identificador de la serie")
        _require_text(self.tag_id, "El identificador de la etiqueta")


@dataclass(frozen=True, slots=True)
class ContentWarning:
    """Describe contenido potencialmente sensible."""

    id: str
    name: str
    description: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.name, "El nombre")


@dataclass(frozen=True, slots=True)
class SeriesContentWarning:
    """Asocia una advertencia y su intensidad con una serie."""

    series_id: str
    warning_id: str
    severity: WarningSeverity

    def __post_init__(self) -> None:
        _require_text(self.series_id, "El identificador de la serie")
        _require_text(self.warning_id, "El identificador de la advertencia")


@dataclass(frozen=True, slots=True)
class ViewingGuide:
    """Resume el drama y el final sin mezclarlo con opiniones personales."""

    series_id: str
    drama_level: DramaLevel
    ending_type: EndingType
    ending_note: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.series_id, "El identificador de la serie")

    @property
    def is_zero_drama_with_happy_ending(self) -> bool:
        """Indica si cumple el filtro de confort más estricto."""
        happy_endings = {
            EndingType.HAPPY_EVER_AFTER,
            EndingType.HAPPY_FOR_NOW,
        }
        return self.drama_level is DramaLevel.ZERO_DRAMA and self.ending_type in happy_endings
