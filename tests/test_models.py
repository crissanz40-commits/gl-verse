import pytest

from gl_verse.models import (
    ActingPair,
    CastImportance,
    Character,
    Credit,
    CreditRole,
    PairingRole,
    Person,
    Series,
    SeriesPairing,
    SeriesStatus,
)


def test_series_stores_objective_catalog_data() -> None:
    series = Series(
        id="gap-2022",
        title="GAP",
        original_title="ทฤษฎีสีชมพู",
        country="Tailandia",
        release_year=2022,
        status=SeriesStatus.COMPLETED,
        cover_image_url="https://images.example/gap.jpg",
        cover_image_source_url="https://example.com/gap",
    )

    assert series.title == "GAP"
    assert series.status is SeriesStatus.COMPLETED


def test_person_character_and_credit_form_a_cast_relationship() -> None:
    person = Person(id="freen-sarocha", name="Sarocha Chankimha", stage_name="Freen")
    character = Character(id="sam-gap", name="Sam", series_id="gap-2022")
    credit = Credit(
        series_id="gap-2022",
        person_id=person.id,
        role=CreditRole.CAST,
        character_id=character.id,
        cast_importance=CastImportance.LEAD,
    )

    assert credit.person_id == "freen-sarocha"
    assert credit.character_id == "sam-gap"
    assert credit.cast_importance is CastImportance.LEAD


def test_non_cast_credit_cannot_reference_a_character() -> None:
    with pytest.raises(ValueError, match="crédito de reparto"):
        Credit(
            series_id="gap-2022",
            person_id="director-example",
            role=CreditRole.DIRECTOR,
            character_id="sam-gap",
        )


def test_non_cast_credit_cannot_have_cast_importance() -> None:
    with pytest.raises(ValueError, match="importancia"):
        Credit(
            series_id="gap-2022",
            person_id="director-example",
            role=CreditRole.DIRECTOR,
            cast_importance=CastImportance.LEAD,
        )


def test_series_rejects_an_empty_identifier() -> None:
    with pytest.raises(ValueError, match="identificador"):
        Series(id="", title="GAP", country="Tailandia", release_year=2022)


def test_acting_pair_is_connected_to_its_work_in_a_series() -> None:
    acting_pair = ActingPair(
        id="freenbecky",
        name="FreenBecky",
        person_ids=("freen-sarocha", "becky-armstrong"),
        active_since=2022,
        image_url="https://images.example/freenbecky.jpg",
        image_source_url="https://example.com/freenbecky",
    )
    series_pairing = SeriesPairing(
        id="sam-mon-gap",
        series_id="gap-2022",
        acting_pair_id=acting_pair.id,
        character_ids=("sam-gap", "mon-gap"),
        role=PairingRole.MAIN,
    )

    assert series_pairing.acting_pair_id == "freenbecky"
    assert series_pairing.series_id == "gap-2022"


def test_character_pairing_does_not_require_an_acting_pair() -> None:
    series_pairing = SeriesPairing(
        id="mhom-ped-sawan-pairing",
        series_id="mhom-ped-sawan-2024",
        character_ids=("mhom-ped", "srinuan"),
        role=PairingRole.MAIN,
    )

    assert series_pairing.acting_pair_id is None


def test_a_pair_cannot_repeat_the_same_member() -> None:
    with pytest.raises(ValueError, match="distintos"):
        ActingPair(
            id="invalid-pair",
            name="Pareja no válida",
            person_ids=("same-person", "same-person"),
        )


def test_images_require_their_source() -> None:
    with pytest.raises(ValueError, match="imagen y su fuente"):
        Person(
            id="freen-sarocha",
            name="Sarocha Chankimha",
            image_url="https://images.example/freen.jpg",
        )
