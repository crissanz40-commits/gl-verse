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
    assert 'id="pair-grid"' in html
    assert 'id="actress-grid"' in html
    assert 'id="detail-dialog"' in html
    assert 'src="app.js"' in html
    assert 'href="styles.css"' in html


def test_web_prototype_keeps_series_actresses_and_pairs_separate() -> None:
    javascript = (WEB_ROOT / "app.js").read_text(encoding="utf-8")

    assert "const actresses = [" in javascript
    assert "const actingPairs = [" in javascript
    assert "const seriesPairings = [" in javascript
    assert "const series = [" in javascript
    assert 'showDetail("series"' in javascript
    assert 'data-open="pair:' in javascript
    assert 'data-open="actress:' in javascript
    assert "Sin pareja en esta serie" in javascript


def test_web_prototype_has_traceable_images_for_all_actresses_and_series() -> None:
    javascript = (WEB_ROOT / "app.js").read_text(encoding="utf-8")

    assert javascript.count('imageSourceUrl: "https://') == 11
    assert javascript.count('coverImageSourceUrl: "https://') == 6
    assert "commons.wikimedia.org/wiki/File:" in javascript
    assert "www.gmm-tv.com/artists/view/24/" in javascript
    assert "www.change2561.com/changeartist" in javascript
    assert ".entity-media img, .poster > img" in javascript
