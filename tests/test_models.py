import pytest

from gl_verse.models import Character, Credit, CreditRole, Person, Series, SeriesStatus


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
