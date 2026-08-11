import json
import threading
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

import pytest

from gl_verse.admin_auth import AdminUserError, authenticate, create_admin
from gl_verse.admin_catalog import admin_series_payload, update_series
from gl_verse.database import connect_database, initialize_database
from gl_verse.web_server import create_web_server


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    yield database
    database.close()


def test_admin_password_is_hashed_and_authenticates(connection) -> None:
    create_admin(connection, "cris", "una-frase-segura-2026")

    stored = connection.execute(
        "SELECT password_hash FROM admin_users WHERE username = 'cris'"
    ).fetchone()[0]

    assert "una-frase-segura-2026" not in stored
    assert stored.startswith("pbkdf2_sha256$600000$")
    assert authenticate(connection, "cris", "una-frase-segura-2026")
    assert not authenticate(connection, "cris", "incorrecta-segura")
    assert not authenticate(connection, "missing", "incorrecta-segura")


def test_admin_password_policy_and_duplicate_user(connection) -> None:
    with pytest.raises(AdminUserError, match="12 caracteres"):
        create_admin(connection, "cris", "corta")
    create_admin(connection, "cris", "una-frase-segura-2026")
    with pytest.raises(AdminUserError, match="Ya existe"):
        create_admin(connection, "cris", "otra-frase-segura")


def test_admin_edit_records_source_audit_and_reopens_review(connection) -> None:
    create_admin(connection, "cris", "una-frase-segura-2026")
    connection.execute(
        "INSERT INTO series_review_status VALUES (?, ?, ?)",
        ("gap-2022", "approved", "2026-08-11T10:00:00Z"),
    )

    result = update_series(
        connection,
        "cris",
        "gap-2022",
        {"synopsis": "Sinopsis corregida y contrastada."},
        {
            "title": "Ficha oficial de GAP",
            "url": "https://example.com/gap",
            "sourceType": "official",
            "verificationStatus": "verified",
            "publisher": "IDOLFACTORY",
        },
    )

    assert result["synopsis"] == "Sinopsis corregida y contrastada."
    assert result["reviewStatus"] == "pending"
    assert connection.execute("SELECT COUNT(*) FROM catalog_sources").fetchone()[0] == 1
    assert connection.execute(
        "SELECT COUNT(*) FROM provenance_records WHERE entity_id = 'gap-2022' AND field_name = 'synopsis'"
    ).fetchone()[0] == 1
    audit = connection.execute(
        "SELECT username, changes_json, source_id FROM admin_audit_log"
    ).fetchone()
    assert audit["username"] == "cris"
    assert json.loads(audit["changes_json"]) == {
        "synopsis": "Sinopsis corregida y contrastada."
    }
    assert audit["source_id"] is not None


def test_admin_api_requires_login_and_csrf(tmp_path) -> None:
    database_path = tmp_path / "catalog.db"
    connection = connect_database(database_path)
    create_admin(connection, "cris", "una-frase-segura-2026")
    connection.close()
    server = create_web_server(database_path, port=0, web_root=tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    opener = build_opener(HTTPCookieProcessor(CookieJar()))

    try:
        with pytest.raises(HTTPError) as unauthorized:
            urlopen(f"{base_url}/api/admin/series")
        login = Request(
            f"{base_url}/api/admin/login",
            data=json.dumps(
                {"username": "cris", "password": "una-frase-segura-2026"}
            ).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with opener.open(login) as response:
            session = json.load(response)
        with opener.open(f"{base_url}/api/admin/series") as response:
            payload = json.load(response)
        no_csrf = Request(
            f"{base_url}/api/admin/series/gap-2022/review-status",
            data=json.dumps({"status": "approved"}).encode(),
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with pytest.raises(HTTPError) as forbidden:
            opener.open(no_csrf)
        review = Request(
            f"{base_url}/api/admin/series/gap-2022/review-status",
            data=json.dumps({"status": "approved"}).encode(),
            headers={
                "Content-Type": "application/json",
                "X-GL-Verse-CSRF": session["csrfToken"],
            },
            method="PUT",
        )
        with opener.open(review) as response:
            approved = json.load(response)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    assert unauthorized.value.code == 401
    assert forbidden.value.code == 403
    assert len(payload["series"]) == 6
    assert approved["status"] == "approved"


def test_admin_payload_contains_editable_fields(connection) -> None:
    gap = next(item for item in admin_series_payload(connection) if item["id"] == "gap-2022")

    assert gap["title"] == "GAP: The Series"
    assert gap["originalTitle"]
    assert gap["reviewStatus"] == "pending"


def test_version_eleven_upgrades_without_losing_reviews() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection, target_version=11)
    connection.execute(
        "INSERT INTO series_review_status VALUES (?, ?, ?)",
        ("gap-2022", "approved", "2026-08-11T10:00:00Z"),
    )

    initialize_database(connection)

    assert connection.execute(
        "SELECT status FROM series_review_status WHERE series_id = 'gap-2022'"
    ).fetchone()[0] == "approved"
    assert connection.execute("SELECT COUNT(*) FROM admin_users").fetchone()[0] == 0
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    connection.close()
