"""Empresas, plataformas y disponibilidad de las series GL."""

from dataclasses import dataclass
from enum import Enum


class CompanyRole(str, Enum):
    """Función de una empresa en una serie."""

    PRODUCER = "producer"
    BROADCASTER = "broadcaster"
    DISTRIBUTOR = "distributor"


class AccessModel(str, Enum):
    """Modalidad de acceso a una serie dentro de una plataforma."""

    FREE = "free"
    SUBSCRIPTION = "subscription"
    RENTAL = "rental"
    PURCHASE = "purchase"


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} no puede estar vacío")


def _validate_url(value: str, field_name: str) -> None:
    if not value.startswith(("https://", "http://")):
        raise ValueError(f"{field_name} debe comenzar por http:// o https://")


@dataclass(frozen=True, slots=True)
class Company:
    """Representa una empresa relacionada con producciones GL."""

    id: str
    name: str
    country: str | None = None
    website_url: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.name, "El nombre")

        if self.website_url is not None:
            _validate_url(self.website_url, "La web de la empresa")


@dataclass(frozen=True, slots=True)
class SeriesCompany:
    """Relaciona una empresa con su función en una serie."""

    series_id: str
    company_id: str
    role: CompanyRole

    def __post_init__(self) -> None:
        _require_text(self.series_id, "El identificador de la serie")
        _require_text(self.company_id, "El identificador de la empresa")


@dataclass(frozen=True, slots=True)
class Platform:
    """Representa una plataforma en la que puede verse contenido GL."""

    id: str
    name: str
    website_url: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "El identificador")
        _require_text(self.name, "El nombre")

        if self.website_url is not None:
            _validate_url(self.website_url, "La web de la plataforma")


@dataclass(frozen=True, slots=True)
class Availability:
    """Indica dónde y cómo está disponible una serie en un territorio."""

    series_id: str
    platform_id: str
    territory: str
    access_model: AccessModel
    official_url: str
    subtitle_languages: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.series_id, "El identificador de la serie")
        _require_text(self.platform_id, "El identificador de la plataforma")
        _require_text(self.territory, "El territorio")
        _validate_url(self.official_url, "El enlace oficial")

        for language in self.subtitle_languages:
            _require_text(language, "El idioma de subtítulos")

        if len(set(self.subtitle_languages)) != len(self.subtitle_languages):
            raise ValueError("Los idiomas de subtítulos no pueden estar duplicados")
