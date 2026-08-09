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
    assert 'id="release-month-filter"' in html
    assert 'id="release-year-filter"' in html
    assert '<option value="score">Mejor nota</option>' in html
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


def test_web_prototype_filters_real_release_dates_and_uses_cast_thumbnails() -> None:
    javascript = (WEB_ROOT / "app.js").read_text(encoding="utf-8")

    assert javascript.count('releaseDate: "') == 6
    assert javascript.count('releaseDateSourceUrl: "https://') == 6
    assert 'releaseDate: "2022-11-19"' in javascript
    assert 'releaseDate: "2024-03-08"' in javascript
    assert 'releaseDate: "2024-06-24"' in javascript
    assert 'releaseDate: "2024-08-04"' in javascript
    assert 'releaseDate: "2024-08-30"' in javascript
    assert 'releaseDate: "2024-10-19"' in javascript
    assert "function renderReleaseFilters()" in javascript
    assert 'state.sort === "score"' in javascript
    assert "function avatarMarkup(actress" in javascript
    assert ".cast-avatar img" in javascript


def test_web_prototype_uses_verified_current_actress_names_and_roles() -> None:
    javascript = (WEB_ROOT / "app.js").read_text(encoding="utf-8")

    assert 'name: "Rutricha Phapakithi", stageName: "Ciize"' in javascript
    assert 'name: "Sirilak Kwong", stageName: "Lingling"' in javascript
    assert 'actressId: "freen", character: "Pin"' in javascript
    assert 'actressId: "becky", character: "Anin"' in javascript
