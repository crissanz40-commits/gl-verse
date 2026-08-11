import json
import threading
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

import pytest

from gl_verse.admin_auth import GoogleIdentity, GoogleOIDCConfig, upsert_google_user
from gl_verse.admin_catalog import admin_series_payload, update_series
from gl_verse.database import connect_database, initialize_database
from gl_verse.web_server import create_web_server


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    yield database
    database.close()


class FakeGoogleClient:
    def __init__(self, identity: GoogleIdentity) -> None:
        self.config = GoogleOIDCConfig("client-id", frozenset())
        self.identity = identity

    def verify(self, credential: str, nonce: str) -> GoogleIdentity:
        assert (credential, bool(nonce)) == ("valid-token", True)
        return self.identity


def login_with_google(opener, base_url: str) -> dict:
    with opener.open(f"{base_url}/api/auth/google/start?next=/admin") as response:
        config = json.load(response)
    login = Request(
        f"{base_url}/api/auth/google",
        data=json.dumps(
            {"credential": "valid-token", "loginCsrf": config["loginCsrf"]}
        ).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with opener.open(login) as response:
        result = json.load(response)
    assert result["nextPath"] == "/admin"
    with opener.open(f"{base_url}/api/auth/session") as response:
        return json.load(response)


def test_google_user_roles_bootstrap_admin_and_keep_existing_admin(connection) -> None:
    identity = GoogleIdentity("google-123", "Cris@Example.com", "Cris", None)
    user = upsert_google_user(connection, identity, frozenset({"cris@example.com"}))
    second_login = upsert_google_user(connection, identity, frozenset())
    viewer = upsert_google_user(
        connection, GoogleIdentity("google-456", "viewer@example.com"), frozenset()
    )
    assert (user.role, second_login.role, viewer.role) == ("admin", "admin", "viewer")
    assert connection.execute("SELECT COUNT(*) FROM app_users").fetchone()[0] == 2


def test_admin_edit_records_google_subject_in_audit(connection) -> None:
    user = upsert_google_user(
        connection,
        GoogleIdentity("google-123", "cris@example.com"),
        frozenset({"cris@example.com"}),
    )
    result = update_series(
        connection,
        user.subject,
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
    audit = connection.execute("SELECT actor_sub, changes_json FROM admin_audit_log").fetchone()
    assert result["reviewStatus"] == "pending"
    assert audit["actor_sub"] == "google-123"
    assert json.loads(audit["changes_json"])["synopsis"].startswith("Sinopsis")


@pytest.mark.parametrize(
    ("email", "admin_emails", "expected_status"),
    [
        ("cris@example.com", frozenset({"cris@example.com"}), 200),
        ("viewer@example.com", frozenset({"cris@example.com"}), 403),
    ],
)
def test_google_login_enforces_admin_role(tmp_path, email, admin_emails, expected_status) -> None:
    server = create_web_server(
        tmp_path / "catalog.db",
        port=0,
        web_root=tmp_path,
        oidc_client=FakeGoogleClient(GoogleIdentity(f"sub-{email}", email)),
        admin_emails=admin_emails,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    try:
        with pytest.raises(HTTPError) as unauthorized:
            urlopen(f"{base_url}/api/admin/series")
        session = login_with_google(opener, base_url)
        try:
            with opener.open(f"{base_url}/api/admin/series") as response:
                status = response.status
        except HTTPError as error:
            status = error.code
        if expected_status == 200:
            request = Request(
                f"{base_url}/api/admin/series/gap-2022/review-status",
                data=json.dumps({"status": "approved"}).encode(),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            with pytest.raises(HTTPError) as no_csrf:
                opener.open(request)
            assert no_csrf.value.code == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    assert unauthorized.value.code == 401
    assert session["user"]["role"] == ("admin" if expected_status == 200 else "viewer")
    assert status == expected_status


def test_session_reports_google_configuration(tmp_path) -> None:
    server = create_web_server(tmp_path / "catalog.db", port=0, web_root=tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/auth/session") as response:
            payload = json.load(response)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    assert payload == {"authenticated": False, "googleConfigured": False}


def test_google_login_rejects_mismatched_csrf(tmp_path) -> None:
    server = create_web_server(
        tmp_path / "catalog.db",
        port=0,
        web_root=tmp_path,
        oidc_client=FakeGoogleClient(GoogleIdentity("sub-cris", "cris@example.com")),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    try:
        with opener.open(f"{base_url}/api/auth/google/start"):
            pass
        request = Request(
            f"{base_url}/api/auth/google",
            data=json.dumps(
                {"credential": "valid-token", "loginCsrf": "attacker-state"}
            ).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as rejected:
            opener.open(request)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    assert rejected.value.code == 400


def test_admin_payload_contains_editable_fields(connection) -> None:
    gap = next(item for item in admin_series_payload(connection) if item["id"] == "gap-2022")
    assert gap["title"] == "GAP: The Series"
    assert gap["reviewStatus"] == "pending"


def test_version_eleven_upgrades_to_google_roles_without_losing_reviews() -> None:
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
    assert connection.execute("SELECT COUNT(*) FROM app_users").fetchone()[0] == 0
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    connection.close()
