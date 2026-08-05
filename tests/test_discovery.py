from gl_verse.discovery import (
    ContentWarning,
    DramaLevel,
    EndingType,
    SeriesContentWarning,
    SeriesTag,
    Tag,
    TagCategory,
    ViewingGuide,
    WarningSeverity,
)


def test_series_can_be_tagged_by_genre_and_trope() -> None:
    romance = Tag(id="romance", name="Romance", category=TagCategory.GENRE)
    enemies_to_lovers = Tag(
        id="enemies-to-lovers",
        name="Enemies to lovers",
        category=TagCategory.TROPE,
    )

    assert SeriesTag(series_id="example-series", tag_id=romance.id).tag_id == "romance"
    assert (
        SeriesTag(series_id="example-series", tag_id=enemies_to_lovers.id).tag_id
        == "enemies-to-lovers"
    )


def test_zero_drama_with_happy_ending_is_a_first_class_filter() -> None:
    guide = ViewingGuide(
        series_id="comfort-series",
        drama_level=DramaLevel.ZERO_DRAMA,
        ending_type=EndingType.HAPPY_EVER_AFTER,
    )

    assert guide.is_zero_drama_with_happy_ending is True


def test_zero_drama_with_open_ending_does_not_pass_comfort_filter() -> None:
    guide = ViewingGuide(
        series_id="open-ending-series",
        drama_level=DramaLevel.ZERO_DRAMA,
        ending_type=EndingType.OPEN,
    )

    assert guide.is_zero_drama_with_happy_ending is False


def test_series_can_include_a_content_warning() -> None:
    warning = ContentWarning(
        id="homophobia",
        name="Homofobia",
        description="Incluye situaciones o lenguaje homófobo.",
    )
    relationship = SeriesContentWarning(
        series_id="example-series",
        warning_id=warning.id,
        severity=WarningSeverity.MEDIUM,
    )

    assert relationship.warning_id == "homophobia"
    assert relationship.severity is WarningSeverity.MEDIUM
