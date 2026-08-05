import pytest

from gl_verse.models import Series


def test_series_stores_personal_catalog_data() -> None:
    series = Series(
        title="GAP",
        country="Tailandia",
        release_year=2022,
        watched=True,
        personal_rating=10,
    )

    assert series.title == "GAP"
    assert series.watched is True
    assert series.personal_rating == 10


def test_series_rejects_rating_outside_zero_to_ten() -> None:
    with pytest.raises(ValueError, match="entre 0 y 10"):
        Series(
            title="Serie de prueba",
            country="Tailandia",
            release_year=2026,
            personal_rating=11,
        )
