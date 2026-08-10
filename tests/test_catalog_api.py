import json
import threading
from urllib.request import urlopen

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
