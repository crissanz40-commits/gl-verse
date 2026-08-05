import pytest

from gl_verse.models import (
    ActingPair,
    Character,
    CharacterPairing,
    Credit,
    CreditRole,
    PairingPortrayal,
    PairingRole,
    Person,
    Series,
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
    )

    assert credit.person_id == "freen-sarocha"
    assert credit.character_id == "sam-gap"


def test_non_cast_credit_cannot_reference_a_character() -> None:
    with pytest.raises(ValueError, match="crédito de reparto"):
        Credit(
            series_id="gap-2022",
            person_id="director-example",
            role=CreditRole.DIRECTOR,
            character_id="sam-gap",
        )


def test_series_rejects_an_empty_identifier() -> None:
    with pytest.raises(ValueError, match="identificador"):
        Series(id="", title="GAP", country="Tailandia", release_year=2022)


def test_acting_pair_and_character_pairing_remain_separate_but_connected() -> None:
    acting_pair = ActingPair(
        id="freenbecky",
        name="FreenBecky",
        person_ids=("freen-sarocha", "becky-armstrong"),
        active_since=2022,
    )
    character_pairing = CharacterPairing(
        id="sam-mon-gap",
        series_id="gap-2022",
        character_ids=("sam-gap", "mon-gap"),
        role=PairingRole.MAIN,
    )
    portrayal = PairingPortrayal(
        acting_pair_id=acting_pair.id,
        character_pairing_id=character_pairing.id,
    )

    assert portrayal.acting_pair_id == "freenbecky"
    assert portrayal.character_pairing_id == "sam-mon-gap"


def test_a_pair_cannot_repeat_the_same_member() -> None:
    with pytest.raises(ValueError, match="distintos"):
        ActingPair(
            id="invalid-pair",
            name="Pareja no válida",
            person_ids=("same-person", "same-person"),
        )
