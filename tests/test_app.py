from gl_verse.app import welcome_message


def test_welcome_message_mentions_project_name() -> None:
    assert "GL Verse" in welcome_message()
