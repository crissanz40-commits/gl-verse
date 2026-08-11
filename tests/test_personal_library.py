import json
import threading
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

import pytest

from gl_verse.admin_auth import GoogleIdentity, GoogleOIDCConfig, upsert_google_user
from gl_verse.database import connect_database, initialize_database
from gl_verse.personal_library import (
    PersonalLibraryError,
    delete_entry,
    list_entries,
    save_entry,
)
from gl_verse.web_server import create_web_server


def entry_payload(**changes):
    payload = {
        "status": "watching",
        "episodesWatched": 3,
        "rating": 8,
        "review": "Una historia muy disfrutable.",
        "startedOn": "2026-08-01",
        "completedOn": None,
    }
    payload.update(changes)
    return payload


@pytest.fixture
def connection():
    database = connect_database(":memory:")
    initialize_database(database)
    yield database
    database.close()


def add_user(connection, subject: str, email: str):
    return upsert_google_user(
        connection,
        GoogleIdentity(subject, email, email.split("@")[0]),
        frozenset(),
    )


def add_gap_episodes(connection, count: int = 12) -> None:
    connection.execute(
        "INSERT INTO seasons (id, series_id, number) VALUES ('gap-season-1-test', 'gap-2022', 1)"
    )
    connection.executemany(
        """
        INSERT INTO episodes (id, season_id, number, kind)
        VALUES (?, 'gap-season-1-test', ?, 'regular')
        """,
        [(f"gap-episode-{number}-test", number) for number in range(1, count + 1)],
    )


def test_personal_entries_are_isolated_by_google_subject(connection) -> None:
    first = add_user(connection, "sub-first", "first@example.com")
    second = add_user(connection, "sub-second", "second@example.com")

    save_entry(connection, first.subject, "gap-2022", entry_payload(rating=9))
    save_entry(
        connection,
        second.subject,
        "gap-2022",
        entry_payload(status="want_to_watch", episodesWatched=0, rating=None),
    )

    assert list_entries(connection, first.subject)[0]["rating"] == 9
    assert list_entries(connection, second.subject)[0]["status"] == "want_to_watch"
    assert delete_entry(connection, first.subject, "gap-2022") is True
    assert list_entries(connection, first.subject) == []
    assert len(list_entries(connection, second.subject)) == 1


def test_personal_entry_can_be_edited_without_replacing_created_at(connection) -> None:
    user = add_user(connection, "sub-user", "user@example.com")
    add_gap_episodes(connection)
    created = save_entry(connection, user.subject, "gap-2022", entry_payload())
    updated = save_entry(
        connection,
        user.subject,
        "gap-2022",
        entry_payload(
            status="watched",
            episodesWatched=12,
            rating=10,
            completedOn="2026-08-10",
        ),
    )

    assert updated["createdAt"] == created["createdAt"]
    assert updated["status"] == "watched"
    assert updated["episodesWatched"] == 12
    assert updated["totalEpisodes"] == 12


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"rating": 11}, "puntuación"),
        ({"episodesWatched": 13}, "12 episodios"),
        ({"completedOn": "2026-07-01"}, "anterior"),
        ({"review": "x" * 2001}, "2000"),
    ],
)
def test_personal_entry_validation(connection, changes, message) -> None:
    user = add_user(connection, "sub-user", "user@example.com")
    add_gap_episodes(connection)

    with pytest.raises(PersonalLibraryError, match=message):
        save_entry(connection, user.subject, "gap-2022", entry_payload(**changes))


def test_version_thirteen_adds_empty_personal_library() -> None:
    connection = connect_database(":memory:")
    initialize_database(connection, target_version=13)
    initialize_database(connection)

    assert connection.execute("SELECT COUNT(*) FROM user_series_entries").fetchone()[0] == 0
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    connection.close()


class FakeGoogleClient:
    def __init__(self) -> None:
        self.config = GoogleOIDCConfig("client-id", frozenset())
        self.identity = GoogleIdentity("sub-viewer", "viewer@example.com")

    def verify(self, credential: str, nonce: str) -> GoogleIdentity:
        assert credential == "valid-token"
        assert nonce
        return self.identity


def login(opener, base_url: str) -> tuple[str, str]:
    with opener.open(f"{base_url}/api/auth/google/start") as response:
        config = json.load(response)
    request = Request(
        f"{base_url}/api/auth/google",
        data=json.dumps(
            {"credential": "valid-token", "loginCsrf": config["loginCsrf"]}
        ).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with opener.open(request) as response:
        token = json.load(response)["sessionToken"]
    session_request = Request(
        f"{base_url}/api/auth/session",
        headers={"Authorization": f"Bearer {token}"},
    )
    with opener.open(session_request) as response:
        csrf = json.load(response)["csrfToken"]
    return token, csrf


def api_request(base_url, path, token, *, method="GET", csrf=None, payload=None):
    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    if csrf:
        headers["X-GL-Verse-CSRF"] = csrf
    return Request(f"{base_url}{path}", data=data, headers=headers, method=method)


def test_personal_library_api_allows_viewers_and_prevents_cross_account_access(tmp_path) -> None:
    client = FakeGoogleClient()
    server = create_web_server(
        tmp_path / "catalog.db",
        port=0,
        web_root=tmp_path,
        oidc_client=client,
        admin_emails=frozenset({"admin@example.com"}),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    first_opener = build_opener(HTTPCookieProcessor(CookieJar()))
    second_opener = build_opener(HTTPCookieProcessor(CookieJar()))
    try:
        first_token, first_csrf = login(first_opener, base_url)
        save = api_request(
            base_url,
            "/api/me/library/gap-2022",
            first_token,
            method="PUT",
            csrf=first_csrf,
            payload=entry_payload(rating=9),
        )
        with first_opener.open(save) as response:
            assert json.load(response)["rating"] == 9

        client.identity = GoogleIdentity("sub-other", "other@example.com")
        second_token, _ = login(second_opener, base_url)
        own_list = api_request(base_url, "/api/me/library", second_token)
        with second_opener.open(own_list) as response:
            assert json.load(response) == {"entries": []}

        no_csrf = api_request(
            base_url,
            "/api/me/library/gap-2022",
            first_token,
            method="DELETE",
        )
        with pytest.raises(HTTPError) as rejected:
            first_opener.open(no_csrf)
        assert rejected.value.code == 403

        client.identity = GoogleIdentity("sub-admin", "admin@example.com")
        admin_opener = build_opener(HTTPCookieProcessor(CookieJar()))
        admin_token, admin_csrf = login(admin_opener, base_url)
        admin_save = api_request(
            base_url,
            "/api/me/library/gap-2022",
            admin_token,
            method="PUT",
            csrf=admin_csrf,
            payload=entry_payload(status="watched", episodesWatched=5),
        )
        with admin_opener.open(admin_save) as response:
            assert json.load(response)["status"] == "watched"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_personal_library_requires_authentication(tmp_path) -> None:
    server = create_web_server(tmp_path / "catalog.db", port=0, web_root=tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(HTTPError) as rejected:
            build_opener().open(
                f"http://127.0.0.1:{server.server_port}/api/me/library"
            )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    assert rejected.value.code == 401
