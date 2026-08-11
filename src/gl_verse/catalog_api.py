"""Lecturas del catálogo preparadas para la API web."""

from __future__ import annotations

import hashlib
import sqlite3
from typing import Any

from gl_verse.database import initialize_database

_PALETTES = (
    ("#63325a", "#d76f9c"),
    ("#203b70", "#7761ae"),
    ("#a14b3e", "#e99568"),
    ("#285a69", "#6eb6ad"),
    ("#4b6d5c", "#b2c991"),
    ("#693344", "#c96d78"),
)


def catalog_payload(connection: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    """Construye una representación completa y objetiva del catálogo."""
    initialize_database(connection)
    actresses = _actresses(connection)
    pairs = _acting_pairs(connection)
    pairings = _series_pairings(connection)
    platforms = _platforms(connection)
    companies = _companies(connection)
    collections = _collections(connection)
    tags = _tags(connection)
    warnings = _content_warnings(connection)
    series = _series(
        connection,
        _availability_by_series(connection),
        _companies_by_series(connection),
        _collections_by_series(connection),
        _seasons_by_series(connection),
        _tags_by_series(connection),
        _warnings_by_series(connection),
        _viewing_guides_by_series(connection),
    )
    return {
        "series": series,
        "actresses": actresses,
        "actingPairs": pairs,
        "seriesPairings": pairings,
        "platforms": platforms,
        "companies": companies,
        "collections": collections,
        "tags": tags,
        "contentWarnings": warnings,
    }


def _actresses(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT DISTINCT p.id, p.name, p.stage_name, p.image_url, p.image_source_url
        FROM people AS p
        JOIN credits AS credit ON credit.person_id = p.id AND credit.role = 'cast'
        ORDER BY COALESCE(p.stage_name, p.name) COLLATE NOCASE
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "stageName": row["stage_name"] or row["name"],
            "initials": _initials(row["stage_name"] or row["name"]),
            "colors": _colors(row["id"]),
            "imageUrl": row["image_url"],
            "imageSourceUrl": row["image_source_url"],
        }
        for row in rows
    ]


def _acting_pairs(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT id, name, first_person_id, second_person_id, image_url, image_source_url
        FROM acting_pairs
        ORDER BY name COLLATE NOCASE
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "actressIds": [row["first_person_id"], row["second_person_id"]],
            "initials": _initials(row["name"]),
            "colors": _colors(row["id"]),
            "imageUrl": row["image_url"],
            "imageSourceUrl": row["image_source_url"],
        }
        for row in rows
    ]


def _series_pairings(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT pairing.id, pairing.series_id, pairing.acting_pair_id,
               first_character.name AS first_character,
               second_character.name AS second_character,
               pairing.role
        FROM series_pairings AS pairing
        JOIN characters AS first_character ON first_character.id = pairing.first_character_id
        JOIN characters AS second_character ON second_character.id = pairing.second_character_id
        ORDER BY pairing.series_id, pairing.role, pairing.id
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "seriesId": row["series_id"],
            "pairId": row["acting_pair_id"],
            "characters": [row["first_character"], row["second_character"]],
            "role": row["role"],
        }
        for row in rows
    ]


def _platforms(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, name, website_url FROM platforms ORDER BY name COLLATE NOCASE"
    ).fetchall()
    return [
        {"id": row["id"], "name": row["name"], "websiteUrl": row["website_url"]}
        for row in rows
    ]


def _companies(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, name, country, website_url FROM companies ORDER BY name COLLATE NOCASE"
    ).fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "country": row["country"],
            "websiteUrl": row["website_url"],
        }
        for row in rows
    ]


def _collections(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, title, kind, description FROM collections ORDER BY title COLLATE NOCASE"
    ).fetchall()
    entries = connection.execute(
        """
        SELECT collection_id, series_id, position
        FROM collection_entries
        ORDER BY collection_id, position
        """
    ).fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        grouped.setdefault(entry["collection_id"], []).append(
            {"seriesId": entry["series_id"], "position": entry["position"]}
        )
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "kind": row["kind"],
            "description": row["description"],
            "entries": grouped.get(row["id"], []),
        }
        for row in rows
    ]


def _tags(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, name, category FROM tags ORDER BY category, name COLLATE NOCASE"
    ).fetchall()
    return [dict(row) for row in rows]


def _content_warnings(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, name, description FROM content_warnings ORDER BY name COLLATE NOCASE"
    ).fetchall()
    return [dict(row) for row in rows]


def _companies_by_series(connection: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute(
        """
        SELECT relationship.series_id, company.id, company.name, company.country,
               company.website_url, relationship.role
        FROM series_companies AS relationship
        JOIN companies AS company ON company.id = relationship.company_id
        ORDER BY relationship.series_id, relationship.role, company.name COLLATE NOCASE
        """
    ).fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["series_id"], []).append(
            {
                "id": row["id"],
                "name": row["name"],
                "country": row["country"],
                "websiteUrl": row["website_url"],
                "role": row["role"],
            }
        )
    return grouped


def _collections_by_series(connection: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute(
        """
        SELECT entry.series_id, collection.id, collection.title, collection.kind,
               collection.description, entry.position
        FROM collection_entries AS entry
        JOIN collections AS collection ON collection.id = entry.collection_id
        ORDER BY entry.series_id, collection.title COLLATE NOCASE
        """
    ).fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["series_id"], []).append(
            {
                "id": row["id"],
                "title": row["title"],
                "kind": row["kind"],
                "description": row["description"],
                "position": row["position"],
            }
        )
    return grouped


def _seasons_by_series(connection: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    episode_rows = connection.execute(
        """
        SELECT id, season_id, number, title, kind, air_date, duration_minutes
        FROM episodes ORDER BY season_id, number, kind
        """
    ).fetchall()
    episodes: dict[str, list[dict[str, Any]]] = {}
    for row in episode_rows:
        episodes.setdefault(row["season_id"], []).append(
            {
                "id": row["id"],
                "number": row["number"],
                "title": row["title"],
                "kind": row["kind"],
                "airDate": row["air_date"],
                "durationMinutes": row["duration_minutes"],
            }
        )
    rows = connection.execute(
        """
        SELECT id, series_id, number, title, release_year
        FROM seasons ORDER BY series_id, number
        """
    ).fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["series_id"], []).append(
            {
                "id": row["id"],
                "number": row["number"],
                "title": row["title"],
                "releaseYear": row["release_year"],
                "episodes": episodes.get(row["id"], []),
            }
        )
    return grouped


def _tags_by_series(connection: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute(
        """
        SELECT relationship.series_id, tag.id, tag.name, tag.category
        FROM series_tags AS relationship
        JOIN tags AS tag ON tag.id = relationship.tag_id
        ORDER BY relationship.series_id, tag.category, tag.name COLLATE NOCASE
        """
    ).fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["series_id"], []).append(
            {"id": row["id"], "name": row["name"], "category": row["category"]}
        )
    return grouped


def _warnings_by_series(connection: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute(
        """
        SELECT relationship.series_id, warning.id, warning.name, warning.description,
               relationship.severity
        FROM series_content_warnings AS relationship
        JOIN content_warnings AS warning ON warning.id = relationship.warning_id
        ORDER BY relationship.series_id, warning.name COLLATE NOCASE
        """
    ).fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["series_id"], []).append(
            {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "severity": row["severity"],
            }
        )
    return grouped


def _viewing_guides_by_series(connection: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    rows = connection.execute(
        "SELECT series_id, drama_level, ending_type, ending_note FROM viewing_guides"
    ).fetchall()
    return {
        row["series_id"]: {
            "dramaLevel": row["drama_level"],
            "endingType": row["ending_type"],
            "endingNote": row["ending_note"],
        }
        for row in rows
    }


def _availability_by_series(
    connection: sqlite3.Connection,
) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute(
        """
        SELECT availability.series_id, availability.platform_id, platform.name AS platform_name,
               availability.territory, availability.access_model, availability.official_url,
               subtitle.language AS subtitle_language
        FROM availability
        JOIN platforms AS platform ON platform.id = availability.platform_id
        LEFT JOIN availability_subtitles AS subtitle
          ON subtitle.series_id = availability.series_id
         AND subtitle.platform_id = availability.platform_id
         AND subtitle.territory = availability.territory
        ORDER BY availability.series_id, platform.name COLLATE NOCASE,
                 availability.territory, subtitle.language COLLATE NOCASE
        """
    ).fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    entries: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["series_id"], row["platform_id"], row["territory"])
        entry = entries.get(key)
        if entry is None:
            entry = {
                "platformId": row["platform_id"],
                "platformName": row["platform_name"],
                "territory": row["territory"],
                "accessModel": row["access_model"],
                "officialUrl": row["official_url"],
                "subtitleLanguages": [],
            }
            entries[key] = entry
            grouped.setdefault(row["series_id"], []).append(entry)
        if row["subtitle_language"] is not None:
            entry["subtitleLanguages"].append(row["subtitle_language"])
    return grouped


def _series(
    connection: sqlite3.Connection,
    availability_by_series: dict[str, list[dict[str, Any]]],
    companies_by_series: dict[str, list[dict[str, Any]]],
    collections_by_series: dict[str, list[dict[str, Any]]],
    seasons_by_series: dict[str, list[dict[str, Any]]],
    tags_by_series: dict[str, list[dict[str, Any]]],
    warnings_by_series: dict[str, list[dict[str, Any]]],
    viewing_guides_by_series: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT series.id, series.title, series.country, series.release_year,
               series.release_date, series.status, series.synopsis,
               series.cover_image_url, series.cover_image_source_url,
               COALESCE(review.status, 'pending') AS review_status,
               review.reviewed_at,
               COALESCE(
                   (
                       SELECT source.url
                       FROM provenance_records AS provenance
                       JOIN catalog_sources AS source ON source.id = provenance.source_id
                       WHERE provenance.entity_type = 'series'
                         AND provenance.entity_id = series.id
                         AND provenance.field_name IN ('release_date', 'release_year')
                       ORDER BY CASE provenance.status
                           WHEN 'verified' THEN 0
                           WHEN 'corroborated' THEN 1
                           ELSE 2
                       END
                       LIMIT 1
                   ),
                   series.cover_image_source_url
               ) AS release_date_source_url
        FROM series
        LEFT JOIN series_review_status AS review ON review.series_id = series.id
        ORDER BY COALESCE(series.release_date, printf('%04d-12-31', series.release_year)) DESC,
                 series.title COLLATE NOCASE
        """
    ).fetchall()

    credits_by_series: dict[str, list[dict[str, Any]]] = {}
    credits = connection.execute(
        """
        SELECT credit.series_id, credit.person_id, character.name AS character,
               credit.cast_importance
        FROM credits AS credit
        LEFT JOIN characters AS character ON character.id = credit.character_id
        WHERE credit.role = 'cast'
        ORDER BY credit.series_id,
                 CASE credit.cast_importance
                     WHEN 'lead' THEN 0 WHEN 'supporting' THEN 1 ELSE 2
                 END,
                 credit.id
        """
    ).fetchall()
    for credit in credits:
        credits_by_series.setdefault(credit["series_id"], []).append(
            {
                "actressId": credit["person_id"],
                "character": credit["character"] or "Personaje sin confirmar",
                "importance": credit["cast_importance"] or "supporting",
            }
        )

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "year": row["release_year"],
            "releaseDate": row["release_date"],
            "releaseDateSourceUrl": row["release_date_source_url"],
            "country": row["country"],
            "status": row["status"],
            "reviewStatus": row["review_status"],
            "reviewedAt": row["reviewed_at"],
            "initials": _initials(row["title"]),
            "colors": _colors(row["id"]),
            "coverImageUrl": row["cover_image_url"],
            "coverImageSourceUrl": row["cover_image_source_url"],
            "synopsis": row["synopsis"] or "Sinopsis pendiente de verificar.",
            "cast": credits_by_series.get(row["id"], []),
            "availability": availability_by_series.get(row["id"], []),
            "companies": companies_by_series.get(row["id"], []),
            "collections": collections_by_series.get(row["id"], []),
            "seasons": seasons_by_series.get(row["id"], []),
            "tags": tags_by_series.get(row["id"], []),
            "contentWarnings": warnings_by_series.get(row["id"], []),
            "viewingGuide": viewing_guides_by_series.get(row["id"]),
        }
        for row in rows
    ]


def _initials(value: str) -> str:
    words = [word for word in value.replace(":", " ").split() if word]
    return "".join(word[0].upper() for word in words[:2]) or "GL"


def _colors(identifier: str) -> list[str]:
    index = hashlib.sha256(identifier.encode("utf-8")).digest()[0] % len(_PALETTES)
    return list(_PALETTES[index])
