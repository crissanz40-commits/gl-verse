import pytest

from gl_verse.industry import (
    AccessModel,
    Availability,
    Company,
    CompanyRole,
    Platform,
    SeriesCompany,
)


def test_company_can_produce_a_series() -> None:
    company = Company(
        id="idol-factory",
        name="Idol Factory",
        country="Tailandia",
        website_url="https://www.idolfactoryofficial.com",
    )
    relationship = SeriesCompany(
        series_id="gap-2022",
        company_id=company.id,
        role=CompanyRole.PRODUCER,
    )

    assert relationship.company_id == "idol-factory"
    assert relationship.role is CompanyRole.PRODUCER


def test_series_can_be_available_for_free_in_spain() -> None:
    platform = Platform(
        id="youtube",
        name="YouTube",
        website_url="https://www.youtube.com",
    )
    availability = Availability(
        series_id="gap-2022",
        platform_id=platform.id,
        territory="ES",
        access_model=AccessModel.FREE,
        official_url="https://www.youtube.com/playlist?list=gap-example",
        subtitle_languages=("es", "en"),
    )

    assert availability.territory == "ES"
    assert "es" in availability.subtitle_languages


def test_availability_rejects_a_non_web_url() -> None:
    with pytest.raises(ValueError, match="http"):
        Availability(
            series_id="gap-2022",
            platform_id="youtube",
            territory="ES",
            access_model=AccessModel.FREE,
            official_url="youtube.com/gap",
        )


def test_availability_rejects_duplicate_subtitle_languages() -> None:
    with pytest.raises(ValueError, match="duplicados"):
        Availability(
            series_id="gap-2022",
            platform_id="youtube",
            territory="ES",
            access_model=AccessModel.FREE,
            official_url="https://www.youtube.com/gap",
            subtitle_languages=("es", "es"),
        )
