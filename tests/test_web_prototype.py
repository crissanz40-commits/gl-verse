from pathlib import Path

WEB_ROOT = Path(__file__).parents[1] / "web"


def test_web_prototype_has_all_static_assets() -> None:
    assert (WEB_ROOT / "index.html").is_file()
    assert (WEB_ROOT / "styles.css").is_file()
    assert (WEB_ROOT / "app.js").is_file()
    assert (WEB_ROOT / "admin.html").is_file()
    assert (WEB_ROOT / "admin.css").is_file()
    assert (WEB_ROOT / "admin.js").is_file()


def test_admin_prototype_uses_authenticated_api() -> None:
    html = (WEB_ROOT / "admin.html").read_text(encoding="utf-8")
    javascript = (WEB_ROOT / "admin.js").read_text(encoding="utf-8")
    stylesheet = (WEB_ROOT / "admin.css").read_text(encoding="utf-8")

    assert 'id="google-login"' in html
    assert "[hidden] { display:none !important; }" in stylesheet
    assert 'id="series-form"' in html
    assert "/api/auth/google/start" in javascript
    assert "accounts.google.com/gsi/client" in javascript
    assert "/api/auth/session" in javascript
    assert 'credentials: "same-origin"' in javascript
    assert "window.sessionStorage" in javascript
    assert "Authorization" in javascript
    assert "X-GL-Verse-CSRF" in javascript
    assert "/review-status" in javascript


def test_web_prototype_exposes_catalog_controls() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'id="search-input"' in html
    assert 'id="series-grid"' in html
    assert 'id="pair-grid"' in html
    assert 'id="actress-grid"' in html
    assert 'id="release-month-filter"' in html
    assert 'id="release-year-filter"' in html
    assert 'id="drama-fieldset" hidden' in html
    assert 'id="ending-fieldset" hidden' in html
    assert 'id="tag-fieldset" hidden' in html
    assert 'id="comfort-box" hidden' in html
    assert 'id="provider-list"' in html
    assert 'value="score" disabled' in html
    assert 'id="detail-dialog"' in html
    assert 'src="app.js' in html
    assert 'href="styles.css"' in html


def test_web_prototype_loads_relational_catalog_from_api() -> None:
    javascript = (WEB_ROOT / "app.js").read_text(encoding="utf-8")

    assert 'fetch("/api/catalog")' in javascript
    assert "actresses = payload.actresses" in javascript
    assert "actingPairs = payload.actingPairs" in javascript
    assert "seriesPairings = payload.seriesPairings" in javascript
    assert "series = payload.series" in javascript
    assert "...payload.platforms.map" in javascript
    assert "item.availability.some" in javascript
    assert 'class="availability-row"' in javascript
    assert 'showDetail("series"' in javascript
    assert 'data-open="pair:' in javascript
    assert 'data-open="actress:' in javascript
    assert "Pareja artística no registrada" in javascript
    assert "Sin pareja en esta serie" in javascript
    assert "pairing.characters.includes(credit.character)" in javascript
    assert "pair?.name" in javascript
    assert "item.viewingGuide" in javascript
    assert 'guide.dramaLevel === "zero_drama"' in javascript
    assert 'document.querySelector("#drama-fieldset").hidden = !hasViewingGuides' in javascript
    assert 'document.querySelector("#tag-fieldset").hidden = payload.tags.length === 0' in javascript
    assert "item.tags.some" in javascript
    assert "item.contentWarnings.map" in javascript
    assert "item.companies.map" in javascript
    assert "item.collections.map" in javascript
    assert "item.seasons.map" in javascript
    assert "item.reviewStatus" in javascript
    assert 'class="review-badge"' in javascript


def test_web_prototype_does_not_duplicate_catalog_data() -> None:
    javascript = (WEB_ROOT / "app.js").read_text(encoding="utf-8")

    assert "Rutricha Phapakithi" not in javascript
    assert "GAP: The Series" not in javascript
    assert "upload.wikimedia.org" not in javascript
    assert "function renderReleaseFilters()" in javascript
    assert "function avatarMarkup(actress" in javascript
    assert ".cast-avatar img" in javascript
