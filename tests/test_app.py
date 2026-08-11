from gl_verse.admin_auth import authenticate
from gl_verse.app import main, welcome_message
from gl_verse.database import connect_database


def test_welcome_message_mentions_project_name() -> None:
    assert "GL Verse" in welcome_message()


def test_create_admin_command_prompts_twice_and_persists_user(tmp_path, monkeypatch) -> None:
    passwords = iter(["una-frase-segura-2026", "una-frase-segura-2026"])
    monkeypatch.setattr("getpass.getpass", lambda _prompt: next(passwords))
    database_path = tmp_path / "catalog.db"

    result = main(["crear-admin", "cris", "--database", str(database_path)])

    connection = connect_database(database_path)
    assert result == 0
    assert authenticate(connection, "cris", "una-frase-segura-2026")
    connection.close()
