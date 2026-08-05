from pathlib import Path

WEB_ROOT = Path(__file__).parents[1] / "web"


def test_web_prototype_has_all_static_assets() -> None:
    assert (WEB_ROOT / "index.html").is_file()
    assert (WEB_ROOT / "styles.css").is_file()
    assert (WEB_ROOT / "app.js").is_file()


def test_web_prototype_exposes_gl_discovery_controls() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'id="search-input"' in html
    assert 'id="drama-filter"' in html
    assert 'id="provider-list"' in html
    assert 'id="comfort-toggle"' in html
    assert 'id="series-grid"' in html
    assert 'src="app.js"' in html
    assert 'href="styles.css"' in html
