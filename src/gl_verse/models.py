"""Modelos principales del catálogo."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Series:
    """Representa una serie GL dentro del catálogo personal."""

    title: str
    country: str
    release_year: int
    watched: bool = False
    personal_rating: float | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("El título no puede estar vacío")

        if self.release_year < 1900:
            raise ValueError("El año de estreno debe ser igual o posterior a 1900")

        if self.personal_rating is not None and not 0 <= self.personal_rating <= 10:
            raise ValueError("La nota personal debe estar entre 0 y 10")
