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
from gl_verse.database import connect_database, get_schema_version, initialize_database


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
            }
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
        "sources": 1,
        "provenance": 1,
    }
    assert connection.execute(
        "SELECT title FROM series WHERE id = 'sample-series-2026'"
    ).fetchone()[0] == "Sample Series"
    assert connection.execute(
        "SELECT status FROM provenance_records WHERE entity_id = 'sample-series-2026'"
    ).fetchone()[0] == "verified"


def test_version_five_upgrades_without_losing_the_catalog() -> None:
    database = connect_database(":memory:")
    initialize_database(database, target_version=5)
    series_before = database.execute("SELECT COUNT(*) FROM series").fetchone()[0]

    initialize_database(database)

    assert get_schema_version(database) == 6
    assert database.execute("SELECT COUNT(*) FROM series").fetchone()[0] == series_before
    assert database.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'catalog_sources'"
    ).fetchone()[0] == 1
    database.close()


def test_second_import_is_idempotent(connection, catalog_data) -> None:
    document = parse_catalog(catalog_data)
    import_catalog(connection, document)

    summary = import_catalog(connection, document)

    assert summary.inserted_total == 0
    assert summary.unchanged_total == 11


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

    assert connection.execute(
        "SELECT COUNT(*) FROM catalog_sources WHERE id = 'source-before-conflict'"
    ).fetchone()[0] == 0
    assert connection.execute(
        "SELECT title FROM series WHERE id = 'sample-series-2026'"
    ).fetchone()[0] == "Sample Series"


def test_dry_run_validates_but_does_not_save(connection, catalog_data) -> None:
    summary = import_catalog(connection, parse_catalog(catalog_data), dry_run=True)

    assert summary.dry_run is True
    assert summary.inserted_total == 11
    assert connection.execute(
        "SELECT COUNT(*) FROM series WHERE id = 'sample-series-2026'"
    ).fetchone()[0] == 0


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

    assert connection.execute(
        "SELECT COUNT(*) FROM catalog_sources WHERE id = 'sample-official'"
    ).fetchone()[0] == 0


def test_cli_imports_a_json_file(tmp_path, catalog_data, capsys) -> None:
    catalog_path = tmp_path / "catalog.json"
    database_path = tmp_path / "gl-verse.db"
    catalog_path.write_text(json.dumps(catalog_data), encoding="utf-8")

    result = main(
        ["importar-series", str(catalog_path), "--database", str(database_path)]
    )

    assert result == 0
    assert "Importación completada: 11 registros nuevos" in capsys.readouterr().out
    with sqlite3.connect(database_path) as database:
        assert database.execute(
            "SELECT COUNT(*) FROM series WHERE id = 'sample-series-2026'"
        ).fetchone()[0] == 1
