"""Carga transaccional de catálogos JSON en SQLite."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from gl_verse.database import initialize_database
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
from gl_verse.provenance import (
    EntityType,
    ProvenanceRecord,
    Source,
    SourceType,
    VerificationStatus,
)

FORMAT_VERSION = 1


class CatalogImportError(ValueError):
    """Indica que un catálogo no puede validarse o importarse."""


class CatalogConflictError(CatalogImportError):
    """Indica que una carga contradice datos ya guardados."""


@dataclass(frozen=True, slots=True)
class CatalogDocument:
    """Datos validados que pueden incorporarse al catálogo."""

    series: tuple[Series, ...] = ()
    people: tuple[Person, ...] = ()
    characters: tuple[Character, ...] = ()
    credits: tuple[Credit, ...] = ()
    acting_pairs: tuple[ActingPair, ...] = ()
    series_pairings: tuple[SeriesPairing, ...] = ()
    sources: tuple[Source, ...] = ()
    provenance: tuple[ProvenanceRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class ImportSummary:
    """Resultado cuantificado de una importación."""

    inserted: dict[str, int]
    updated: dict[str, int]
    unchanged: dict[str, int]
    dry_run: bool = False

    @property
    def inserted_total(self) -> int:
        return sum(self.inserted.values())

    @property
    def updated_total(self) -> int:
        return sum(self.updated.values())

    @property
    def unchanged_total(self) -> int:
        return sum(self.unchanged.values())


def load_catalog(path: str | Path) -> CatalogDocument:
    """Lee y valida un documento JSON de catálogo."""
    catalog_path = Path(path)
    try:
        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        raise CatalogImportError(f"No se puede leer {catalog_path}: {error}") from error
    except json.JSONDecodeError as error:
        raise CatalogImportError(
            f"JSON no válido en {catalog_path}, línea {error.lineno}, columna {error.colno}"
        ) from error

    return parse_catalog(raw)


def parse_catalog(raw: Any) -> CatalogDocument:
    """Convierte una estructura JSON en entidades de dominio validadas."""
    root = _mapping(raw, "el documento")
    _fields(
        root,
        required={"format_version"},
        optional={
            "series",
            "people",
            "characters",
            "credits",
            "acting_pairs",
            "series_pairings",
            "sources",
            "provenance",
        },
        context="el documento",
    )
    if (
        not isinstance(root["format_version"], int)
        or isinstance(root["format_version"], bool)
        or root["format_version"] != FORMAT_VERSION
    ):
        raise CatalogImportError(
            f"format_version debe ser {FORMAT_VERSION}, no {root['format_version']!r}"
        )

    try:
        document = CatalogDocument(
            series=tuple(_parse_series(item, index) for index, item in _items(root, "series")),
            people=tuple(_parse_person(item, index) for index, item in _items(root, "people")),
            characters=tuple(
                _parse_character(item, index) for index, item in _items(root, "characters")
            ),
            credits=tuple(_parse_credit(item, index) for index, item in _items(root, "credits")),
            acting_pairs=tuple(
                _parse_acting_pair(item, index) for index, item in _items(root, "acting_pairs")
            ),
            series_pairings=tuple(
                _parse_series_pairing(item, index)
                for index, item in _items(root, "series_pairings")
            ),
            sources=tuple(_parse_source(item, index) for index, item in _items(root, "sources")),
            provenance=tuple(
                _parse_provenance(item, index) for index, item in _items(root, "provenance")
            ),
        )
    except (AttributeError, TypeError, ValueError) as error:
        if isinstance(error, CatalogImportError):
            raise
        raise CatalogImportError(str(error)) from error

    _reject_document_duplicates(document)
    return document


def import_catalog(
    connection: sqlite3.Connection,
    document: CatalogDocument,
    *,
    dry_run: bool = False,
) -> ImportSummary:
    """Importa un catálogo completo de forma atómica e idempotente."""
    if connection.in_transaction:
        raise CatalogImportError("La conexión tiene una transacción activa")

    initialize_database(connection)
    inserted = {name: 0 for name in _SECTION_NAMES}
    updated = {name: 0 for name in _SECTION_NAMES}
    unchanged = {name: 0 for name in _SECTION_NAMES}

    connection.execute("BEGIN IMMEDIATE")
    try:
        _reject_database_duplicates(connection, document)
        _validate_references(connection, document)
        _import_sources(connection, document.sources, inserted, unchanged)
        _import_series(connection, document.series, inserted, updated, unchanged)
        _import_people(connection, document.people, inserted, unchanged)
        _import_characters(connection, document.characters, inserted, unchanged)
        _import_credits(connection, document.credits, inserted, unchanged)
        _import_acting_pairs(connection, document.acting_pairs, inserted, unchanged)
        _import_series_pairings(connection, document.series_pairings, inserted, unchanged)
        _import_provenance(connection, document.provenance, inserted, unchanged)
        if dry_run:
            connection.rollback()
        else:
            connection.commit()
    except (CatalogImportError, sqlite3.Error) as error:
        connection.rollback()
        if isinstance(error, CatalogImportError):
            raise
        raise CatalogImportError(f"SQLite rechazó la importación: {error}") from error

    return ImportSummary(
        inserted=inserted,
        updated=updated,
        unchanged=unchanged,
        dry_run=dry_run,
    )


_SECTION_NAMES = (
    "series",
    "people",
    "characters",
    "credits",
    "acting_pairs",
    "series_pairings",
    "sources",
    "provenance",
)


def _items(root: dict[str, Any], name: str) -> enumerate[Any]:
    value = root.get(name, [])
    if not isinstance(value, list):
        raise CatalogImportError(f"{name} debe ser una lista")
    return enumerate(value)


def _mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CatalogImportError(f"{context} debe ser un objeto JSON")
    return value


def _fields(
    item: dict[str, Any],
    *,
    required: set[str],
    optional: set[str],
    context: str,
) -> None:
    missing = required - item.keys()
    unexpected = item.keys() - required - optional
    if missing:
        raise CatalogImportError(f"Faltan campos en {context}: {', '.join(sorted(missing))}")
    if unexpected:
        raise CatalogImportError(
            f"Campos desconocidos en {context}: {', '.join(sorted(unexpected))}"
        )


def _object(
    value: Any,
    section: str,
    index: int,
    required: set[str],
    optional: set[str],
) -> dict[str, Any]:
    context = f"{section}[{index}]"
    item = _mapping(value, context)
    _fields(item, required=required, optional=optional, context=context)
    return item


def _pair(value: Any, context: str) -> tuple[str, str]:
    if not isinstance(value, list) or len(value) != 2 or not all(isinstance(v, str) for v in value):
        raise CatalogImportError(f"{context} debe ser una lista de dos identificadores")
    return value[0], value[1]


def _optional_date(value: Any, context: str) -> date | None:
    if value is None:
        return None
    return _date(value, context)


def _date(value: Any, context: str) -> date:
    if not isinstance(value, str):
        raise CatalogImportError(f"{context} debe ser una fecha ISO YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise CatalogImportError(f"{context} debe ser una fecha ISO YYYY-MM-DD") from error


def _parse_series(value: Any, index: int) -> Series:
    item = _object(
        value,
        "series",
        index,
        {"id", "title", "country", "release_year", "status"},
        {
            "release_date",
            "original_title",
            "synopsis",
            "cover_image_url",
            "cover_image_source_url",
        },
    )
    return Series(
        id=item["id"],
        title=item["title"],
        country=item["country"],
        release_year=item["release_year"],
        release_date=_optional_date(item.get("release_date"), f"series[{index}].release_date"),
        original_title=item.get("original_title"),
        status=SeriesStatus(item["status"]),
        synopsis=item.get("synopsis"),
        cover_image_url=item.get("cover_image_url"),
        cover_image_source_url=item.get("cover_image_source_url"),
    )


def _parse_person(value: Any, index: int) -> Person:
    item = _object(
        value,
        "people",
        index,
        {"id", "name"},
        {"stage_name", "nationality", "image_url", "image_source_url"},
    )
    return Person(
        id=item["id"],
        name=item["name"],
        stage_name=item.get("stage_name"),
        nationality=item.get("nationality"),
        image_url=item.get("image_url"),
        image_source_url=item.get("image_source_url"),
    )


def _parse_character(value: Any, index: int) -> Character:
    item = _object(value, "characters", index, {"id", "name", "series_id"}, set())
    return Character(id=item["id"], name=item["name"], series_id=item["series_id"])


def _parse_credit(value: Any, index: int) -> Credit:
    item = _object(
        value,
        "credits",
        index,
        {"series_id", "person_id", "role"},
        {"character_id", "cast_importance"},
    )
    importance = item.get("cast_importance")
    return Credit(
        series_id=item["series_id"],
        person_id=item["person_id"],
        role=CreditRole(item["role"]),
        character_id=item.get("character_id"),
        cast_importance=CastImportance(importance) if importance is not None else None,
    )


def _parse_acting_pair(value: Any, index: int) -> ActingPair:
    item = _object(
        value,
        "acting_pairs",
        index,
        {"id", "name", "person_ids"},
        {"active_since", "image_url", "image_source_url"},
    )
    return ActingPair(
        id=item["id"],
        name=item["name"],
        person_ids=_pair(item["person_ids"], f"acting_pairs[{index}].person_ids"),
        active_since=item.get("active_since"),
        image_url=item.get("image_url"),
        image_source_url=item.get("image_source_url"),
    )


def _parse_series_pairing(value: Any, index: int) -> SeriesPairing:
    item = _object(
        value,
        "series_pairings",
        index,
        {"id", "series_id", "acting_pair_id", "character_ids", "role"},
        set(),
    )
    return SeriesPairing(
        id=item["id"],
        series_id=item["series_id"],
        acting_pair_id=item["acting_pair_id"],
        character_ids=_pair(item["character_ids"], f"series_pairings[{index}].character_ids"),
        role=PairingRole(item["role"]),
    )


def _parse_source(value: Any, index: int) -> Source:
    item = _object(
        value,
        "sources",
        index,
        {"id", "title", "url", "source_type"},
        {"publisher", "published_on"},
    )
    return Source(
        id=item["id"],
        title=item["title"],
        url=item["url"],
        source_type=SourceType(item["source_type"]),
        publisher=item.get("publisher"),
        published_on=_optional_date(item.get("published_on"), f"sources[{index}].published_on"),
    )


def _parse_provenance(value: Any, index: int) -> ProvenanceRecord:
    item = _object(
        value,
        "provenance",
        index,
        {"source_id", "entity_type", "entity_id", "field_name", "checked_on", "status"},
        {"note"},
    )
    return ProvenanceRecord(
        source_id=item["source_id"],
        entity_type=EntityType(item["entity_type"]),
        entity_id=item["entity_id"],
        field_name=item["field_name"],
        checked_on=_date(item["checked_on"], f"provenance[{index}].checked_on"),
        status=VerificationStatus(item["status"]),
        note=item.get("note"),
    )


def _reject_document_duplicates(document: CatalogDocument) -> None:
    for section, entities in (
        ("series", document.series),
        ("people", document.people),
        ("characters", document.characters),
        ("acting_pairs", document.acting_pairs),
        ("series_pairings", document.series_pairings),
        ("sources", document.sources),
    ):
        _unique((entity.id for entity in entities), f"identificador repetido en {section}")

    _unique(
        (
            (credit.series_id, credit.person_id, credit.role.value, credit.character_id)
            for credit in document.credits
        ),
        "crédito repetido",
    )
    _unique(
        (
            (record.source_id, record.entity_type.value, record.entity_id, record.field_name)
            for record in document.provenance
        ),
        "trazabilidad repetida",
    )


def _unique(values: Any, message: str) -> None:
    seen = set()
    for value in values:
        if value in seen:
            raise CatalogImportError(f"{message}: {value!r}")
        seen.add(value)


def _reject_database_duplicates(connection: sqlite3.Connection, document: CatalogDocument) -> None:
    for item in document.series:
        if connection.execute("SELECT 1 FROM series WHERE id = ?", (item.id,)).fetchone():
            continue
        aliases = [item.title]
        if item.original_title:
            aliases.append(item.original_title)
        placeholders = ", ".join("?" for _ in aliases)
        row = connection.execute(
            f"""
            SELECT id, title FROM series
            WHERE title COLLATE NOCASE IN ({placeholders})
               OR original_title COLLATE NOCASE IN ({placeholders})
            LIMIT 1
            """,
            (*aliases, *aliases),
        ).fetchone()
        if row:
            raise CatalogConflictError(
                f"Posible serie duplicada: {item.id!r} coincide con {row['id']!r} ({row['title']})"
            )

    for item in document.people:
        if connection.execute("SELECT 1 FROM people WHERE id = ?", (item.id,)).fetchone():
            continue
        row = connection.execute(
            """
            SELECT id, name FROM people
            WHERE name = ? COLLATE NOCASE
               OR (? IS NOT NULL AND stage_name = ? COLLATE NOCASE)
            LIMIT 1
            """,
            (item.name, item.stage_name, item.stage_name),
        ).fetchone()
        if row:
            raise CatalogConflictError(
                f"Posible persona duplicada: {item.id!r} coincide con {row['id']!r} ({row['name']})"
            )


def _validate_references(connection: sqlite3.Connection, document: CatalogDocument) -> None:
    available = {
        "series": _available_ids(connection, "series", (item.id for item in document.series)),
        "people": _available_ids(connection, "people", (item.id for item in document.people)),
        "characters": _available_ids(
            connection, "characters", (item.id for item in document.characters)
        ),
        "acting_pairs": _available_ids(
            connection, "acting_pairs", (item.id for item in document.acting_pairs)
        ),
        "series_pairings": _available_ids(
            connection, "series_pairings", (item.id for item in document.series_pairings)
        ),
        "sources": _available_ids(
            connection, "catalog_sources", (item.id for item in document.sources)
        ),
    }

    for item in document.characters:
        _require_reference(item.series_id, available["series"], f"personaje {item.id}", "serie")
    for item in document.credits:
        _require_reference(item.series_id, available["series"], "crédito", "serie")
        _require_reference(item.person_id, available["people"], "crédito", "persona")
        if item.character_id is not None:
            _require_reference(item.character_id, available["characters"], "crédito", "personaje")
    for item in document.acting_pairs:
        for person_id in item.person_ids:
            _require_reference(person_id, available["people"], f"pareja {item.id}", "persona")
    for item in document.series_pairings:
        _require_reference(item.series_id, available["series"], f"relación {item.id}", "serie")
        _require_reference(
            item.acting_pair_id, available["acting_pairs"], f"relación {item.id}", "pareja"
        )
        for character_id in item.character_ids:
            _require_reference(
                character_id, available["characters"], f"relación {item.id}", "personaje"
            )

    provenance_tables = {
        EntityType.SERIES: "series",
        EntityType.PERSON: "people",
        EntityType.CHARACTER: "characters",
        EntityType.ACTING_PAIR: "acting_pairs",
        EntityType.CHARACTER_PAIRING: "series_pairings",
    }
    for item in document.provenance:
        _require_reference(item.source_id, available["sources"], "trazabilidad", "fuente")
        section = provenance_tables.get(item.entity_type)
        if section is None:
            raise CatalogImportError(
                f"La trazabilidad de {item.entity_type.value!r} todavía no puede importarse"
            )
        _require_reference(item.entity_id, available[section], "trazabilidad", "entidad")


def _available_ids(connection: sqlite3.Connection, table: str, document_ids: Any) -> set[str]:
    stored = {row["id"] for row in connection.execute(f"SELECT id FROM {table}").fetchall()}
    return stored | set(document_ids)


def _require_reference(reference: str, available: set[str], context: str, target: str) -> None:
    if reference not in available:
        raise CatalogImportError(f"Referencia desconocida en {context}: {target} {reference!r}")


def _record_result(
    section: str, was_inserted: bool, inserted: dict[str, int], unchanged: dict[str, int]
) -> None:
    target = inserted if was_inserted else unchanged
    target[section] += 1


def _insert_or_compare(
    connection: sqlite3.Connection,
    *,
    table: str,
    section: str,
    key_columns: tuple[str, ...],
    columns: tuple[str, ...],
    values: tuple[Any, ...],
    inserted: dict[str, int],
    unchanged: dict[str, int],
    updated: dict[str, int] | None = None,
    enrichable_columns: tuple[str, ...] = (),
) -> None:
    value_by_column = dict(zip(columns, values, strict=True))
    where = " AND ".join(f"{column} = ?" for column in key_columns)
    key_values = tuple(value_by_column[column] for column in key_columns)
    row = connection.execute(
        f"SELECT {', '.join(columns)} FROM {table} WHERE {where}", key_values
    ).fetchone()
    if row is not None:
        merged = []
        changed_columns = []
        for column, incoming in zip(columns, values, strict=True):
            existing = row[column]
            if existing == incoming or (column in enrichable_columns and incoming is None):
                merged.append(existing)
                continue
            if column in enrichable_columns and existing is None:
                merged.append(incoming)
                changed_columns.append(column)
                continue

            key = ", ".join(f"{name}={value!r}" for name, value in zip(key_columns, key_values))
            raise CatalogConflictError(f"Conflicto en {table} ({key})")

        if changed_columns:
            assignments = ", ".join(f"{column} = ?" for column in changed_columns)
            merged_by_column = dict(zip(columns, merged, strict=True))
            connection.execute(
                f"UPDATE {table} SET {assignments} WHERE {where}",
                (*[merged_by_column[column] for column in changed_columns], *key_values),
            )
            if updated is None:
                raise RuntimeError("La importación no configuró el contador de actualizaciones")
            updated[section] += 1
            return

        _record_result(section, False, inserted, unchanged)
        return

    placeholders = ", ".join("?" for _ in columns)
    connection.execute(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", values
    )
    _record_result(section, True, inserted, unchanged)


def _import_series(connection, entities, inserted, updated, unchanged) -> None:
    columns = (
        "id",
        "title",
        "country",
        "release_year",
        "release_date",
        "original_title",
        "status",
        "synopsis",
        "cover_image_url",
        "cover_image_source_url",
    )
    for item in entities:
        release_date = item.release_date.isoformat() if item.release_date else None
        _insert_or_compare(
            connection,
            table="series",
            section="series",
            key_columns=("id",),
            columns=columns,
            values=(
                item.id,
                item.title,
                item.country,
                item.release_year,
                release_date,
                item.original_title,
                item.status.value,
                item.synopsis,
                item.cover_image_url,
                item.cover_image_source_url,
            ),
            inserted=inserted,
            unchanged=unchanged,
            updated=updated,
            enrichable_columns=(
                "release_date",
                "original_title",
                "synopsis",
                "cover_image_url",
                "cover_image_source_url",
            ),
        )


def _import_people(connection, entities, inserted, unchanged) -> None:
    columns = ("id", "name", "stage_name", "nationality", "image_url", "image_source_url")
    for item in entities:
        _insert_or_compare(
            connection,
            table="people",
            section="people",
            key_columns=("id",),
            columns=columns,
            values=(
                item.id,
                item.name,
                item.stage_name,
                item.nationality,
                item.image_url,
                item.image_source_url,
            ),
            inserted=inserted,
            unchanged=unchanged,
        )


def _import_characters(connection, entities, inserted, unchanged) -> None:
    columns = ("id", "name", "series_id")
    for item in entities:
        _insert_or_compare(
            connection,
            table="characters",
            section="characters",
            key_columns=("id",),
            columns=columns,
            values=(item.id, item.name, item.series_id),
            inserted=inserted,
            unchanged=unchanged,
        )


def _import_credits(connection, entities, inserted, unchanged) -> None:
    columns = ("series_id", "person_id", "role", "character_id", "cast_importance")
    for item in entities:
        values = (
            item.series_id,
            item.person_id,
            item.role.value,
            item.character_id,
            item.cast_importance.value if item.cast_importance else None,
        )
        if item.character_id is None:
            row = connection.execute(
                """
                SELECT series_id, person_id, role, character_id, cast_importance
                FROM credits
                WHERE series_id = ? AND person_id = ? AND role = ? AND character_id IS NULL
                """,
                values[:3],
            ).fetchone()
        else:
            row = connection.execute(
                """
                SELECT series_id, person_id, role, character_id, cast_importance
                FROM credits
                WHERE series_id = ? AND person_id = ? AND role = ? AND character_id = ?
                """,
                values[:4],
            ).fetchone()
        if row is not None:
            if tuple(row[column] for column in columns) != values:
                raise CatalogConflictError(
                    f"Conflicto en credits ({item.series_id!r}, {item.person_id!r})"
                )
            _record_result("credits", False, inserted, unchanged)
            continue
        connection.execute(
            """
            INSERT INTO credits (series_id, person_id, role, character_id, cast_importance)
            VALUES (?, ?, ?, ?, ?)
            """,
            values,
        )
        _record_result("credits", True, inserted, unchanged)


def _import_acting_pairs(connection, entities, inserted, unchanged) -> None:
    columns = (
        "id",
        "name",
        "first_person_id",
        "second_person_id",
        "active_since",
        "image_url",
        "image_source_url",
    )
    for item in entities:
        _insert_or_compare(
            connection,
            table="acting_pairs",
            section="acting_pairs",
            key_columns=("id",),
            columns=columns,
            values=(
                item.id,
                item.name,
                *item.person_ids,
                item.active_since,
                item.image_url,
                item.image_source_url,
            ),
            inserted=inserted,
            unchanged=unchanged,
        )


def _import_series_pairings(connection, entities, inserted, unchanged) -> None:
    columns = (
        "id",
        "series_id",
        "acting_pair_id",
        "first_character_id",
        "second_character_id",
        "role",
    )
    for item in entities:
        _insert_or_compare(
            connection,
            table="series_pairings",
            section="series_pairings",
            key_columns=("id",),
            columns=columns,
            values=(
                item.id,
                item.series_id,
                item.acting_pair_id,
                *item.character_ids,
                item.role.value,
            ),
            inserted=inserted,
            unchanged=unchanged,
        )


def _import_sources(connection, entities, inserted, unchanged) -> None:
    columns = ("id", "title", "url", "source_type", "publisher", "published_on")
    for item in entities:
        _insert_or_compare(
            connection,
            table="catalog_sources",
            section="sources",
            key_columns=("id",),
            columns=columns,
            values=(
                item.id,
                item.title,
                item.url,
                item.source_type.value,
                item.publisher,
                item.published_on.isoformat() if item.published_on else None,
            ),
            inserted=inserted,
            unchanged=unchanged,
        )


def _import_provenance(connection, entities, inserted, unchanged) -> None:
    columns = (
        "source_id",
        "entity_type",
        "entity_id",
        "field_name",
        "checked_on",
        "status",
        "note",
    )
    keys = ("source_id", "entity_type", "entity_id", "field_name")
    for item in entities:
        _insert_or_compare(
            connection,
            table="provenance_records",
            section="provenance",
            key_columns=keys,
            columns=columns,
            values=(
                item.source_id,
                item.entity_type.value,
                item.entity_id,
                item.field_name,
                item.checked_on.isoformat(),
                item.status.value,
                item.note,
            ),
            inserted=inserted,
            unchanged=unchanged,
        )
