import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from gl_verse.catalog_api import catalog_payload
from gl_verse.database import connect_database, initialize_database
from gl_verse.web_server import create_web_server


def test_catalog_payload_preserves_series_people_and_pairing_relationships() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection)

    payload = catalog_payload(connection)

    assert len(payload["series"]) == 6
    assert len(payload["actresses"]) == 11
    assert len(payload["actingPairs"]) == 5
    gap = next(item for item in payload["series"] if item["id"] == "gap-2022")
    assert gap["releaseDate"] == "2022-11-19"
    assert {credit["character"] for credit in gap["cast"]} == {"Sam", "Mon"}
    gap_pairing = next(item for item in payload["seriesPairings"] if item["seriesId"] == "gap-2022")
    assert gap_pairing["pairId"] == "freenbecky"
    assert set(gap_pairing["characters"]) == {"Sam", "Mon"}
    assert payload["platforms"] == []
    assert gap["availability"] == []
    assert gap["reviewStatus"] == "pending"
    assert gap["reviewedAt"] is None

    connection.close()


def test_catalog_payload_exposes_approved_review_status() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection)
    connection.execute(
        "INSERT INTO series_review_status VALUES (?, ?, ?)",
        ("gap-2022", "approved", "2026-08-11T10:00:00Z"),
    )

    payload = catalog_payload(connection)
    gap = next(item for item in payload["series"] if item["id"] == "gap-2022")

    assert gap["reviewStatus"] == "approved"
    assert gap["reviewedAt"] == "2026-08-11T10:00:00Z"
    connection.close()


def test_catalog_payload_exposes_availability_by_territory() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection)
    connection.execute(
        "INSERT INTO platforms (id, name, website_url) VALUES (?, ?, ?)",
        ("youtube", "YouTube", "https://www.youtube.com"),
    )
    connection.execute(
        """
        INSERT INTO availability (series_id, platform_id, territory, access_model, official_url)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("gap-2022", "youtube", "ES", "free", "https://www.youtube.com/example"),
    )
    connection.execute(
        """
        INSERT INTO availability_subtitles (series_id, platform_id, territory, language)
        VALUES (?, ?, ?, ?)
        """,
        ("gap-2022", "youtube", "ES", "es"),
    )
    connection.commit()

    payload = catalog_payload(connection)

    assert payload["platforms"] == [
        {"id": "youtube", "name": "YouTube", "websiteUrl": "https://www.youtube.com"}
    ]
    gap = next(item for item in payload["series"] if item["id"] == "gap-2022")
    assert gap["availability"] == [
        {
            "platformId": "youtube",
            "platformName": "YouTube",
            "territory": "ES",
            "accessModel": "free",
            "officialUrl": "https://www.youtube.com/example",
            "subtitleLanguages": ["es"],
        }
    ]
    connection.close()


def test_catalog_payload_exposes_character_pairing_without_acting_pair() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection)
    connection.execute(
        "UPDATE series_pairings SET acting_pair_id = NULL WHERE id = ?",
        ("sam-mon-gap",),
    )

    payload = catalog_payload(connection)

    gap_pairing = next(item for item in payload["seriesPairings"] if item["seriesId"] == "gap-2022")
    assert gap_pairing["pairId"] is None
    assert set(gap_pairing["characters"]) == {"Sam", "Mon"}
    connection.close()


def test_catalog_payload_exposes_extended_catalog() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection)
    connection.executescript(
        """
        INSERT INTO companies (id, name) VALUES ('studio', 'Studio');
        INSERT INTO series_companies VALUES ('gap-2022', 'studio', 'producer');
        INSERT INTO collections (id, title, kind) VALUES ('universe', 'Universe', 'franchise');
        INSERT INTO collection_entries VALUES ('universe', 'gap-2022', 1);
        INSERT INTO seasons (id, series_id, number) VALUES ('gap-s1', 'gap-2022', 1);
        INSERT INTO episodes (
            id, season_id, number, title, kind, air_date, duration_minutes
        ) VALUES ('gap-e1', 'gap-s1', 1, 'Episode 1', 'regular', '2022-11-19', 55);
        INSERT INTO tags (id, name, category) VALUES ('romance', 'Romance', 'genre');
        INSERT INTO series_tags VALUES ('gap-2022', 'romance');
        INSERT INTO content_warnings (id, name) VALUES ('warning', 'Warning');
        INSERT INTO series_content_warnings VALUES ('gap-2022', 'warning', 'low');
        INSERT INTO viewing_guides VALUES (
            'gap-2022', 'light', 'happy_ever_after', 'Verified note'
        );
        """
    )

    payload = catalog_payload(connection)
    gap = next(item for item in payload["series"] if item["id"] == "gap-2022")

    assert payload["companies"][0]["id"] == "studio"
    assert payload["collections"][0]["entries"] == [
        {"seriesId": "gap-2022", "position": 1}
    ]
    assert payload["tags"] == [{"id": "romance", "name": "Romance", "category": "genre"}]
    assert payload["contentWarnings"][0]["id"] == "warning"
    assert gap["companies"][0]["role"] == "producer"
    assert gap["collections"][0]["position"] == 1
    assert gap["seasons"][0]["episodes"][0]["durationMinutes"] == 55
    assert gap["tags"][0]["name"] == "Romance"
    assert gap["contentWarnings"][0]["severity"] == "low"
    assert gap["viewingGuide"] == {
        "dramaLevel": "light",
        "endingType": "happy_ever_after",
        "endingNote": "Verified note",
    }
    connection.close()


def test_web_server_serves_static_frontend_and_catalog_api(tmp_path) -> None:
    database_path = tmp_path / "catalog.db"
    web_root = tmp_path / "web"
    web_root.mkdir()
    (web_root / "index.html").write_text("<h1>GL Verse</h1>", encoding="utf-8")
    server = create_web_server(database_path, port=0, web_root=web_root)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        with urlopen(f"{base_url}/api/catalog") as response:
            payload = json.load(response)
        with urlopen(f"{base_url}/") as response:
            page = response.read().decode("utf-8")
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    assert len(payload["series"]) == 6
    assert page == "<h1>GL Verse</h1>"


def test_public_api_cannot_update_review_status(tmp_path) -> None:
    server = create_web_server(tmp_path / "catalog.db", port=0, web_root=tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/api/series/gap-2022/review-status",
            data=json.dumps({"status": "approved"}).encode(),
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with pytest.raises(HTTPError) as error:
            urlopen(request)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    assert error.value.code == 404
