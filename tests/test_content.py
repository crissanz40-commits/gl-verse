from datetime import date

import pytest

from gl_verse.content import (
    CollectionEntry,
    CollectionKind,
    Episode,
    EpisodeKind,
    Season,
    SeriesCollection,
)


def test_anthology_can_group_independent_series_in_order() -> None:
    collection = SeriesCollection(
        id="four-elements",
        title="Four Elements",
        kind=CollectionKind.ANTHOLOGY,
    )
    entry = CollectionEntry(
        collection_id=collection.id,
        series_id="four-elements-earth",
        position=1,
    )

    assert entry.collection_id == "four-elements"
    assert entry.series_id == "four-elements-earth"


def test_episode_belongs_to_a_season() -> None:
    season = Season(
        id="gap-2022-season-1",
        series_id="gap-2022",
        number=1,
        release_year=2022,
    )
    episode = Episode(
        id="gap-2022-s01e01",
        season_id=season.id,
        number=1,
        title="Episode 1",
        air_date=date(2022, 11, 19),
        duration_minutes=55,
    )

    assert episode.season_id == "gap-2022-season-1"
    assert episode.kind is EpisodeKind.REGULAR


def test_special_episode_is_distinguishable_from_regular_episodes() -> None:
    episode = Episode(
        id="gap-2022-special-1",
        season_id="gap-2022-season-1",
        number=1,
        kind=EpisodeKind.SPECIAL,
    )

    assert episode.kind is EpisodeKind.SPECIAL


@pytest.mark.parametrize(
    ("factory", "expected_message"),
    [
        (
            lambda: CollectionEntry(
                collection_id="four-elements",
                series_id="four-elements-earth",
                position=0,
            ),
            "posición",
        ),
        (
            lambda: Season(id="invalid", series_id="gap-2022", number=0),
            "temporada",
        ),
        (
            lambda: Episode(id="invalid", season_id="gap-season-1", number=0),
            "episodio",
        ),
    ],
)
def test_narrative_positions_must_be_positive(factory, expected_message: str) -> None:
    with pytest.raises(ValueError, match=expected_message):
        factory()
