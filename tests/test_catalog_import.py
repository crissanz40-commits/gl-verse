import json
import sqlite3

import pytest

from gl_verse.app import main
from gl_verse.catalog_import import (
    CatalogConflictError,
    CatalogImportError,
    import_catalog,
    parse_catalog,
)
from gl_verse.database import (
    SCHEMA_VERSION,
    connect_database,
    get_schema_version,
    initialize_database,
)


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    yield database
    database.close()


@pytest.fixture
def catalog_data():
    return {
        "format_version": 1,
        "series": [
            {
                "id": "sample-series-2026",
                "title": "Sample Series",
                "country": "Tailandia",
                "release_year": 2026,
                "release_date": "2026-03-09",
                "status": "announced",
                "synopsis": "Una ficha utilizada para probar el importador.",
                "cover_image_url": "https://images.example/sample.jpg",
                "cover_image_source_url": "https://example.com/sample",
            }
        ],
        "people": [
            {"id": "sample-one", "name": "Sample One", "stage_name": "One"},
            {"id": "sample-two", "name": "Sample Two", "stage_name": "Two"},
        ],
        "characters": [
            {"id": "one-sample", "name": "One", "series_id": "sample-series-2026"},
            {"id": "two-sample", "name": "Two", "series_id": "sample-series-2026"},
        ],
        "credits": [
            {
                "series_id": "sample-series-2026",
                "person_id": "sample-one",
                "role": "cast",
                "character_id": "one-sample",
                "cast_importance": "lead",
            },
            {
                "series_id": "sample-series-2026",
                "person_id": "sample-two",
                "role": "cast",
                "character_id": "two-sample",
                "cast_importance": "lead",
            },
        ],
        "acting_pairs": [
            {
                "id": "sample-pair",
                "name": "SamplePair",
                "person_ids": ["sample-one", "sample-two"],
            }
        ],
        "series_pairings": [
            {
                "id": "one-two-sample",
                "series_id": "sample-series-2026",
                "acting_pair_id": "sample-pair",
                "character_ids": ["one-sample", "two-sample"],
                "role": "main",
            }
        ],
        "platforms": [
            {
                "id": "sample-stream",
                "name": "Sample Stream",
                "website_url": "https://stream.example",
            }
        ],
        "availability": [
            {
                "series_id": "sample-series-2026",
                "platform_id": "sample-stream",
                "territory": "ES",
                "access_model": "subscription",
                "official_url": "https://stream.example/sample-series",
                "subtitle_languages": ["es", "en"],
            }
        ],
        "sources": [
            {
                "id": "sample-official",
                "title": "Sample Series official page",
                "url": "https://example.com/sample",
                "source_type": "official",
                "publisher": "Example Studio",
            }
        ],
        "provenance": [
            {
                "source_id": "sample-official",
                "entity_type": "series",
                "entity_id": "sample-series-2026",
                "field_name": "title",
                "checked_on": "2026-08-10",
                "status": "verified",
            },
            {
                "source_id": "sample-official",
                "entity_type": "platform",
                "entity_id": "sample-stream",
                "field_name": "name",
                "checked_on": "2026-08-10",
                "status": "verified",
            },
            {
                "source_id": "sample-official",
                "entity_type": "availability",
                "entity_id": "sample-series-2026:sample-stream:ES",
                "field_name": "official_url",
                "checked_on": "2026-08-10",
                "status": "verified",
            },
        ],
    }


def test_imports_a_complete_catalog_with_provenance(connection, catalog_data) -> None:
    summary = import_catalog(connection, parse_catalog(catalog_data))

    assert summary.inserted == {
        "series": 1,
        "people": 2,
        "characters": 2,
        "credits": 2,
        "acting_pairs": 1,
        "series_pairings": 1,
        "platforms": 1,
        "availability": 1,
        "sources": 1,
        "provenance": 3,
    }
    assert (
        connection.execute("SELECT title FROM series WHERE id = 'sample-series-2026'").fetchone()[0]
        == "Sample Series"
    )
    assert (
        connection.execute(
            "SELECT release_date FROM series WHERE id = 'sample-series-2026'"
        ).fetchone()[0]
        == "2026-03-09"
    )
    assert (
        connection.execute(
            "SELECT status FROM provenance_records WHERE entity_id = 'sample-series-2026'"
        ).fetchone()[0]
        == "verified"
    )


def test_version_five_upgrades_without_losing_the_catalog() -> None:
    database = connect_database(":memory:")
    initialize_database(database, target_version=5)
    series_before = database.execute("SELECT COUNT(*) FROM series").fetchone()[0]

    initialize_database(database)

    assert get_schema_version(database) == SCHEMA_VERSION
    assert database.execute("SELECT COUNT(*) FROM series").fetchone()[0] == series_before
    assert (
        database.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'catalog_sources'"
        ).fetchone()[0]
        == 1
    )
    database.close()


def test_second_import_is_idempotent(connection, catalog_data) -> None:
    document = parse_catalog(catalog_data)
    import_catalog(connection, document)

    summary = import_catalog(connection, document)

    assert summary.inserted_total == 0
    assert summary.unchanged_total == 15


def test_legacy_import_without_release_date_remains_idempotent(connection, catalog_data) -> None:
    import_catalog(connection, parse_catalog(catalog_data))
    del catalog_data["series"][0]["release_date"]

    summary = import_catalog(connection, parse_catalog(catalog_data))

    assert summary.inserted_total == 0
    assert summary.unchanged_total == 15


def test_import_enriches_empty_optional_series_fields(connection, catalog_data) -> None:
    basic = {
        **catalog_data,
        "series": [
            {
                "id": "sample-series-2026",
                "title": "Sample Series",
                "country": "Tailandia",
                "release_year": 2026,
                "status": "announced",
            }
        ],
        "people": [],
        "characters": [],
        "credits": [],
        "acting_pairs": [],
        "series_pairings": [],
        "platforms": [],
        "availability": [],
        "sources": [],
        "provenance": [],
    }
    import_catalog(connection, parse_catalog(basic))

    summary = import_catalog(connection, parse_catalog(catalog_data))

    assert summary.updated == {
        "series": 1,
        "people": 0,
        "characters": 0,
        "credits": 0,
        "acting_pairs": 0,
        "series_pairings": 0,
        "platforms": 0,
        "availability": 0,
        "sources": 0,
        "provenance": 0,
    }
    row = connection.execute(
        "SELECT release_date, synopsis, cover_image_url FROM series WHERE id = ?",
        ("sample-series-2026",),
    ).fetchone()
    assert tuple(row) == (
        "2026-03-09",
        "Una ficha utilizada para probar el importador.",
        "https://images.example/sample.jpg",
    )

    repeated = import_catalog(connection, parse_catalog(catalog_data))
    assert repeated.updated_total == 0
    assert repeated.unchanged_total == 15


def test_import_rejects_overwriting_enriched_series_fields(connection, catalog_data) -> None:
    import_catalog(connection, parse_catalog(catalog_data))
    catalog_data["series"][0]["synopsis"] = "Una sinopsis contradictoria."

    with pytest.raises(CatalogConflictError, match="series"):
        import_catalog(connection, parse_catalog(catalog_data))


def test_import_enriches_empty_optional_person_and_pair_fields(connection, catalog_data) -> None:
    basic = {
        **catalog_data,
        "people": [
            {"id": person["id"], "name": person["name"]}
            for person in catalog_data["people"]
        ],
        "acting_pairs": [
            {
                "id": pair["id"],
                "name": pair["name"],
                "person_ids": pair["person_ids"],
            }
            for pair in catalog_data["acting_pairs"]
        ],
    }
    import_catalog(connection, parse_catalog(basic))
    catalog_data["people"][0].update(
        nationality="Tailandesa",
        image_url="https://images.example/one.jpg",
        image_source_url="https://example.com/one",
    )
    catalog_data["people"][1].update(
        nationality="Tailandesa",
        image_url="https://images.example/two.jpg",
        image_source_url="https://example.com/two",
    )
    catalog_data["acting_pairs"][0].update(
        active_since=2026,
        image_url="https://images.example/pair.jpg",
        image_source_url="https://example.com/pair",
    )

    summary = import_catalog(connection, parse_catalog(catalog_data))

    assert summary.updated["people"] == 2
    assert summary.updated["acting_pairs"] == 1
    assert summary.updated_total == 3
    person = connection.execute(
        "SELECT stage_name, nationality, image_url FROM people WHERE id = ?",
        ("sample-one",),
    ).fetchone()
    assert tuple(person) == (
        "One",
        "Tailandesa",
        "https://images.example/one.jpg",
    )
    pair = connection.execute(
        "SELECT active_since, image_url FROM acting_pairs WHERE id = ?",
        ("sample-pair",),
    ).fetchone()
    assert tuple(pair) == (2026, "https://images.example/pair.jpg")

    repeated = import_catalog(connection, parse_catalog(catalog_data))
    assert repeated.updated_total == 0
    assert repeated.unchanged_total == 15


def test_import_enriches_platform_and_availability_subtitles(connection, catalog_data) -> None:
    website_url = catalog_data["platforms"][0].pop("website_url")
    subtitle_languages = catalog_data["availability"][0].pop("subtitle_languages")
    import_catalog(connection, parse_catalog(catalog_data))
    catalog_data["platforms"][0]["website_url"] = website_url
    catalog_data["availability"][0]["subtitle_languages"] = subtitle_languages

    summary = import_catalog(connection, parse_catalog(catalog_data))

    assert summary.updated["platforms"] == 1
    assert summary.updated["availability"] == 1
    assert {
        row[0]
        for row in connection.execute(
            "SELECT language FROM availability_subtitles WHERE series_id = ?",
            ("sample-series-2026",),
        )
    } == {"es", "en"}


def test_import_rejects_conflicting_availability(connection, catalog_data) -> None:
    import_catalog(connection, parse_catalog(catalog_data))
    catalog_data["availability"][0]["official_url"] = "https://stream.example/another-page"

    with pytest.raises(CatalogConflictError, match="availability"):
        import_catalog(connection, parse_catalog(catalog_data))


@pytest.mark.parametrize(
    ("section", "field", "value", "table"),
    [
        ("people", "stage_name", "Another One", "people"),
        ("acting_pairs", "active_since", 2025, "acting_pairs"),
    ],
)
def test_import_rejects_overwriting_enriched_person_and_pair_fields(
    connection, catalog_data, section, field, value, table
) -> None:
    catalog_data["acting_pairs"][0]["active_since"] = 2026
    import_catalog(connection, parse_catalog(catalog_data))
    catalog_data[section][0][field] = value

    with pytest.raises(CatalogConflictError, match=table):
        import_catalog(connection, parse_catalog(catalog_data))


def test_conflict_rolls_back_the_whole_import(connection, catalog_data) -> None:
    document = parse_catalog(catalog_data)
    import_catalog(connection, document)
    conflicting = {**catalog_data, "series": [{**catalog_data["series"][0], "title": "Changed"}]}
    conflicting["sources"] = [
        {
            "id": "source-before-conflict",
            "title": "Another source",
            "url": "https://example.com/another-source",
            "source_type": "press",
        }
    ]
    conflicting["provenance"] = []

    with pytest.raises(CatalogConflictError, match="series"):
        import_catalog(connection, parse_catalog(conflicting))

    assert (
        connection.execute(
            "SELECT COUNT(*) FROM catalog_sources WHERE id = 'source-before-conflict'"
        ).fetchone()[0]
        == 0
    )
    assert (
        connection.execute("SELECT title FROM series WHERE id = 'sample-series-2026'").fetchone()[0]
        == "Sample Series"
    )


def test_dry_run_validates_but_does_not_save(connection, catalog_data) -> None:
    summary = import_catalog(connection, parse_catalog(catalog_data), dry_run=True)

    assert summary.dry_run is True
    assert summary.inserted_total == 15
    assert (
        connection.execute(
            "SELECT COUNT(*) FROM series WHERE id = 'sample-series-2026'"
        ).fetchone()[0]
        == 0
    )


def test_rejects_possible_duplicate_series_with_another_id(connection, catalog_data) -> None:
    catalog_data["series"][0]["title"] = "Pluto"

    with pytest.raises(CatalogConflictError, match="Posible serie duplicada"):
        import_catalog(connection, parse_catalog(catalog_data))


def test_rejects_unknown_fields_and_invalid_dates(catalog_data) -> None:
    catalog_data["series"][0]["titel"] = "Typo"
    with pytest.raises(CatalogImportError, match="Campos desconocidos"):
        parse_catalog(catalog_data)

    del catalog_data["series"][0]["titel"]
    catalog_data["provenance"][0]["checked_on"] = "10/08/2026"
    with pytest.raises(CatalogImportError, match="YYYY-MM-DD"):
        parse_catalog(catalog_data)


def test_rejects_unknown_relations_before_writing(connection, catalog_data) -> None:
    catalog_data["credits"][0]["person_id"] = "missing-person"

    with pytest.raises(CatalogImportError, match="missing-person"):
        import_catalog(connection, parse_catalog(catalog_data))

    assert (
        connection.execute(
            "SELECT COUNT(*) FROM catalog_sources WHERE id = 'sample-official'"
        ).fetchone()[0]
        == 0
    )


def test_cli_imports_a_json_file(tmp_path, catalog_data, capsys) -> None:
    catalog_path = tmp_path / "catalog.json"
    database_path = tmp_path / "gl-verse.db"
    catalog_path.write_text(json.dumps(catalog_data), encoding="utf-8")

    result = main(["importar-series", str(catalog_path), "--database", str(database_path)])

    assert result == 0
    assert "Importación completada: 15 registros nuevos" in capsys.readouterr().out
    with sqlite3.connect(database_path) as database:
        assert (
            database.execute(
                "SELECT COUNT(*) FROM series WHERE id = 'sample-series-2026'"
            ).fetchone()[0]
            == 1
        )
