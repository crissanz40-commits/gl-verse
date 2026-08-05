from datetime import date

import pytest

from gl_verse.provenance import (
    EntityType,
    ProvenanceRecord,
    Source,
    SourceType,
    VerificationStatus,
)


def test_source_can_verify_a_specific_series_field() -> None:
    source = Source(
        id="gap-official-playlist",
        title="GAP The Series - Official Playlist",
        url="https://www.youtube.com/playlist?list=gap-example",
        source_type=SourceType.OFFICIAL,
        publisher="Idol Factory",
    )
    record = ProvenanceRecord(
        source_id=source.id,
        entity_type=EntityType.SERIES,
        entity_id="gap-2022",
        field_name="episode_count",
        checked_on=date(2026, 8, 5),
        status=VerificationStatus.VERIFIED,
    )

    assert record.source_id == "gap-official-playlist"
    assert record.field_name == "episode_count"


def test_old_information_can_be_flagged_for_review() -> None:
    record = ProvenanceRecord(
        source_id="youtube-gap",
        entity_type=EntityType.AVAILABILITY,
        entity_id="gap-youtube-es",
        field_name="official_url",
        checked_on=date(2025, 1, 1),
        status=VerificationStatus.VERIFIED,
    )

    assert record.needs_review(as_of=date(2026, 8, 5), max_age_days=180) is True


def test_recent_information_does_not_need_review() -> None:
    record = ProvenanceRecord(
        source_id="youtube-gap",
        entity_type=EntityType.AVAILABILITY,
        entity_id="gap-youtube-es",
        field_name="official_url",
        checked_on=date(2026, 8, 1),
        status=VerificationStatus.VERIFIED,
    )

    assert record.needs_review(as_of=date(2026, 8, 5)) is False


def test_source_rejects_a_non_web_url() -> None:
    with pytest.raises(ValueError, match="http"):
        Source(
            id="invalid",
            title="Fuente no válida",
            url="youtube.com/example",
            source_type=SourceType.COMMUNITY,
        )
