let actresses = [];
let actingPairs = [];
let seriesPairings = [];
let series = [];
let providers = [{ id: "", name: "Todas", short: "GL", color: "#6f285f" }];

const importanceLabels = { lead: "Protagonista", supporting: "Secundaria", guest: "Invitada" };
const roleLabels = { main: "Pareja principal", supporting: "Pareja secundaria" };
const statusLabels = { announced: "Anunciada", airing: "En emisión", completed: "Completada", cancelled: "Cancelada" };
const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
const state = { search: "", provider: "", pairings: [], country: "", releaseMonth: "", releaseYear: "", sort: "newest", saved: new Set(), detailTrail: [] };
const grid = document.querySelector("#series-grid");
const resultCount = document.querySelector("#result-count");
const activeFilters = document.querySelector("#active-filters");
const emptyState = document.querySelector("#empty-state");
const dialog = document.querySelector("#detail-dialog");

const byId = (items, id) => items.find((item) => item.id === id);
const pairingsForSeries = (seriesId) => seriesPairings.filter((pairing) => pairing.seriesId === seriesId);
const pairHistory = (pairId) => seriesPairings.filter((pairing) => pairing.pairId === pairId);
const actressCredits = (actressId) => series.flatMap((item) => item.cast.filter((credit) => credit.actressId === actressId).map((credit) => ({ ...credit, series: item })));
const pairsForActress = (actressId) => actingPairs.filter((pair) => pair.actressIds.includes(actressId));
const releaseParts = (item) => item.releaseDate ? item.releaseDate.split("-") : [String(item.year), "", ""];

function formatReleaseDate(releaseDate) {
  if (!releaseDate) return "Fecha por confirmar";
  const [year, month, day] = releaseDate.split("-");
  return `${Number(day)} ${monthNames[Number(month) - 1].toLocaleLowerCase("es")} ${year}`;
}

function avatarMarkup(actress, large = false) {
  const image = actress.imageUrl ? `<img src="${actress.imageUrl}" alt="" loading="lazy" />` : "";
  return `<span class="cast-avatar${large ? " large" : ""}" style="--media-start:${actress.colors[0]};--media-end:${actress.colors[1]}"><span aria-hidden="true">${actress.initials}</span>${image}</span>`;
}

function mediaMarkup(item, kind, label, showSource = true) {
  const imageUrl = kind === "cover" ? item.coverImageUrl : item.imageUrl;
  const sourceUrl = kind === "cover" ? item.coverImageSourceUrl : item.imageSourceUrl;
  const fallback = `<span class="media-fallback" aria-hidden="true">${item.initials}</span>`;
  const media = imageUrl ? `${fallback}<img src="${imageUrl}" alt="${label}" />` : fallback;
  const source = showSource && sourceUrl ? `<a class="image-source" href="${sourceUrl}" target="_blank" rel="noreferrer">Fuente de la imagen ↗</a>` : "";
  return `<div class="entity-media ${kind}" style="--media-start:${item.colors[0]};--media-end:${item.colors[1]}">${media}${source}</div>`;
}

function pairingSummary(item) {
  const summary = pairingsForSeries(item.id).map((seriesPairing) => {
    const pair = byId(actingPairs, seriesPairing.pairId);
    return `${seriesPairing.characters.join(" · ")} · ${pair.name}`;
  }).join(" · ");
  return summary || "Sin pareja registrada";
}

function renderProviders() {
  document.querySelector("#provider-list").innerHTML = providers.map((provider) => `
    <button class="provider-pill ${state.provider === provider.id ? "active" : ""}" type="button" data-provider="${provider.id}">
      <span class="provider-icon" style="background:${provider.color}">${provider.short}</span>
      <span>${provider.name}<small>${provider.name === "Todas" ? "Todo el catálogo" : "Ver disponibles"}</small></span>
    </button>`).join("");
}

function renderReleaseFilters() {
  const months = [...new Set(series.map((item) => Number(releaseParts(item)[1])).filter(Boolean))].sort((a, b) => a - b);
  const years = [...new Set(series.map((item) => releaseParts(item)[0]))].sort((a, b) => b.localeCompare(a));
  document.querySelector("#release-month-filter").innerHTML = `<option value="">Todos los meses</option>${months.map((month) => `<option value="${month}">${monthNames[month - 1]}</option>`).join("")}`;
  document.querySelector("#release-year-filter").innerHTML = `<option value="">Todos los años</option>${years.map((year) => `<option value="${year}">${year}</option>`).join("")}`;
}

function visibleSeries() {
  const term = state.search.toLocaleLowerCase("es");
  return series.filter((item) => {
    const actressNames = item.cast.map((credit) => byId(actresses, credit.actressId)?.stageName).join(" ");
    const searchable = `${item.title} ${pairingSummary(item)} ${actressNames}`.toLocaleLowerCase("es");
    const roles = pairingsForSeries(item.id).map((pairing) => pairing.role);
    const [releaseYear, releaseMonth] = releaseParts(item);
    return (!term || searchable.includes(term))
      && (!state.pairings.length || state.pairings.some((role) => roles.includes(role)))
      && (!state.provider || item.availability.some((entry) => entry.platformId === state.provider))
      && (!state.country || item.country === state.country)
      && (!state.releaseMonth || releaseMonth === state.releaseMonth.padStart(2, "0"))
      && (!state.releaseYear || releaseYear === state.releaseYear);
  }).sort((a, b) => {
    if (state.sort === "title") return a.title.localeCompare(b.title, "es");
    return (b.releaseDate || `${b.year}`).localeCompare(a.releaseDate || `${a.year}`);
  });
}

function renderCards() {
  const items = visibleSeries();
  resultCount.textContent = `${items.length} ${items.length === 1 ? "título" : "títulos"}`;
  grid.innerHTML = items.map((item, index) => `
    <article class="series-card">
      <div class="poster" role="button" tabindex="0" data-open="series:${item.id}" data-initials="${item.initials}" style="--poster-start:${item.colors[0]};--poster-end:${item.colors[1]}">
        ${item.coverImageUrl ? `<img src="${item.coverImageUrl}" alt="Portada de ${item.title}" />` : ""}
        <div class="poster-top"><span class="rank">#${index + 1}</span><button class="save-button ${state.saved.has(item.id) ? "saved" : ""}" type="button" data-save="${item.id}" aria-label="Guardar ${item.title}">${state.saved.has(item.id) ? "♥" : "♡"}</button></div>
        <div class="poster-title"><small>${item.country.toUpperCase()} · ${item.year}</small><strong>${item.title}</strong></div>
      </div>
      <div class="card-info"><h3>${item.title}</h3><span class="card-meta">${formatReleaseDate(item.releaseDate)} · ${statusLabels[item.status] || item.status}</span><div class="pair-row"><span class="pair-name">♡ ${pairingSummary(item)}</span></div></div>
    </article>`).join("");
  emptyState.hidden = items.length > 0;
  renderActiveFilters();
}

function renderUniverse() {
  document.querySelector("#pair-grid").innerHTML = actingPairs.map((pair) => {
    const members = pair.actressIds.map((id) => byId(actresses, id).stageName).join(" + ");
    return `<button class="universe-card" type="button" data-open="pair:${pair.id}">
      ${mediaMarkup(pair, "pair", `Imagen de ${pair.name}`, false)}
      <span class="universe-card-copy"><small>${pairHistory(pair.id).length} ${pairHistory(pair.id).length === 1 ? "serie" : "series"}</small><strong>${pair.name}</strong><span>${members}</span></span>
    </button>`;
  }).join("");

  document.querySelector("#actress-grid").innerHTML = actresses.map((actress) => `
    <button class="actress-card" type="button" data-open="actress:${actress.id}">
      ${mediaMarkup(actress, "portrait", `Imagen de ${actress.stageName}`, false)}
      <span><strong>${actress.stageName}</strong><small>${actressCredits(actress.id).length} ${actressCredits(actress.id).length === 1 ? "participación" : "participaciones"}</small></span>
    </button>`).join("");

  document.querySelector("#metric-series").textContent = series.length;
  document.querySelector("#metric-pairs").textContent = actingPairs.length;
  document.querySelector("#metric-actresses").textContent = actresses.length;
}

function renderActiveFilters() {
  const chips = [];
  if (state.search) chips.push([`Búsqueda: ${state.search}`, "search"]);
  if (state.provider) chips.push([byId(providers, state.provider)?.name || state.provider, "provider"]);
  state.pairings.forEach((value) => chips.push([roleLabels[value], `pairing:${value}`]));
  if (state.country) chips.push([state.country, "country"]);
  if (state.releaseMonth) chips.push([monthNames[Number(state.releaseMonth) - 1], "releaseMonth"]);
  if (state.releaseYear) chips.push([`Estreno ${state.releaseYear}`, "releaseYear"]);
  activeFilters.innerHTML = chips.map(([label, key]) => `<button class="filter-chip" type="button" data-remove-filter="${key}">${label}</button>`).join("");
}

function detailHeader(label, canGoBack = true) {
  return `<div class="detail-toolbar">${canGoBack && state.detailTrail.length ? '<button type="button" data-detail-back>← Volver</button>' : '<span></span>'}<span>${label}</span></div>`;
}

function seriesDetail(item) {
  const pairings = pairingsForSeries(item.id);
  const pairCards = pairings.map((seriesPairing) => {
    const pair = byId(actingPairs, seriesPairing.pairId);
    return `<button class="relation-card pair-relation" type="button" data-open="pair:${pair.id}">
      <span class="relation-avatar" style="--media-start:${pair.colors[0]};--media-end:${pair.colors[1]}">${pair.initials}</span>
      <span><small>${roleLabels[seriesPairing.role]}</small><strong>${seriesPairing.characters.join(" · ")}</strong><em>${pair.name} →</em></span>
    </button>`;
  }).join("");
  const castCards = item.cast.map((credit) => {
    const actress = byId(actresses, credit.actressId);
    const paired = pairings.find((seriesPairing) => byId(actingPairs, seriesPairing.pairId).actressIds.includes(actress.id));
    const status = paired ? byId(actingPairs, paired.pairId).name : "Sin pareja en esta serie";
    return `<button class="cast-row" type="button" data-open="actress:${actress.id}">
      ${avatarMarkup(actress)}
      <span><strong>${actress.stageName}</strong><small>${credit.character} · ${importanceLabels[credit.importance]}</small></span><em>${status} →</em>
    </button>`;
  }).join("");
  const accessLabels = { free: "Gratis", subscription: "Suscripción", rental: "Alquiler", purchase: "Compra" };
  const availabilityCards = item.availability.map((entry) => {
    const subtitles = entry.subtitleLanguages.length ? ` · Subtítulos: ${entry.subtitleLanguages.join(", ")}` : "";
    return `<a class="availability-row" href="${entry.officialUrl}" target="_blank" rel="noreferrer">
      <span class="provider-icon">${entry.platformName.slice(0, 2).toUpperCase()}</span>
      <span><strong>${entry.platformName}</strong><small>${entry.territory} · ${accessLabels[entry.accessModel] || entry.accessModel}${subtitles}</small></span><em>Ver ↗</em>
    </a>`;
  }).join("");
  return `${detailHeader("Ficha de serie")}
    <div class="detail-layout series-layout">
      <aside>${mediaMarkup(item, "cover", `Portada de ${item.title}`)}</aside>
      <div class="detail-main"><p class="eyebrow">${item.country.toUpperCase()} · ${formatReleaseDate(item.releaseDate).toUpperCase()}</p><h2>${item.title}</h2><p class="detail-lead">${item.synopsis}</p>${item.releaseDateSourceUrl ? `<a class="release-source" href="${item.releaseDateSourceUrl}" target="_blank" rel="noreferrer">Fuente de la fecha de estreno ↗</a>` : ""}
        <div class="score-strip"><span><small>ESTADO</small><strong>${statusLabels[item.status] || item.status}</strong></span><span><small>ESTRENO</small><strong>${item.year}</strong></span><span><small>PAÍS</small><strong>${item.country}</strong></span><span><small>REPARTO</small><strong>${item.cast.length}</strong></span></div>
        <section class="detail-section"><p class="section-kicker">DÓNDE VER</p><div class="availability-list">${availabilityCards || '<p class="pending-copy">Disponibilidad pendiente de verificar.</p>'}</div></section>
        <section class="detail-section"><p class="section-kicker">PAREJAS DE LA SERIE</p><div class="relation-grid">${pairCards}</div></section>
        <section class="detail-section"><p class="section-kicker">REPARTO GL</p><div class="cast-list">${castCards}</div></section>
      </div>
    </div>`;
}

function pairDetail(pair) {
  const members = pair.actressIds.map((id) => byId(actresses, id));
  const history = pairHistory(pair.id).map((seriesPairing) => {
    const item = byId(series, seriesPairing.seriesId);
    return `<button class="history-row" type="button" data-open="series:${item.id}"><span class="history-year">${item.year}</span><span><strong>${item.title}</strong><small>${seriesPairing.characters.join(" · ")} · ${roleLabels[seriesPairing.role]}</small></span><em>Ver serie →</em></button>`;
  }).join("");
  const memberCards = members.map((actress) => `<button class="member-card" type="button" data-open="actress:${actress.id}">${avatarMarkup(actress, true)}<span><small>ACTRIZ</small><strong>${actress.stageName}</strong><em>${actress.name}</em></span><b>→</b></button>`).join("");
  return `${detailHeader("Ficha de pareja")}
    <div class="detail-layout pair-layout"><aside>${mediaMarkup(pair, "pair", `Imagen de ${pair.name}`)}</aside><div class="detail-main"><p class="eyebrow">PAREJA ARTÍSTICA</p><h2>${pair.name}</h2><p class="detail-lead">Una pareja independiente de sus personajes. Su historia se construye con cada serie en la que trabajan juntas.</p>
      <div class="member-grid">${memberCards}</div>
      <section class="detail-section"><p class="section-kicker">TRAYECTORIA JUNTAS · ${history ? pairHistory(pair.id).length : 0}</p><div class="history-list">${history}</div></section>
    </div></div>`;
}

function actressDetail(actress) {
  const credits = actressCredits(actress.id);
  const history = credits.map((credit) => {
    const seriesPairing = pairingsForSeries(credit.series.id).find((pairing) => byId(actingPairs, pairing.pairId).actressIds.includes(actress.id));
    const pairText = seriesPairing ? `Con ${byId(actingPairs, seriesPairing.pairId).name}` : "Sin pareja en esta serie";
    return `<button class="history-row" type="button" data-open="series:${credit.series.id}"><span class="history-year">${credit.series.year}</span><span><strong>${credit.series.title}</strong><small>${credit.character} · ${importanceLabels[credit.importance]} · ${pairText}</small></span><em>Ver serie →</em></button>`;
  }).join("");
  const pairCards = pairsForActress(actress.id).map((pair) => `<button class="compact-pair" type="button" data-open="pair:${pair.id}"><span style="--media-start:${pair.colors[0]};--media-end:${pair.colors[1]}">${pair.initials}</span><strong>${pair.name}</strong><em>Ver pareja →</em></button>`).join("");
  return `${detailHeader("Ficha de actriz")}
    <div class="detail-layout actress-layout"><aside>${mediaMarkup(actress, "portrait", `Imagen de ${actress.stageName}`)}</aside><div class="detail-main"><p class="eyebrow">ACTRIZ</p><h2>${actress.stageName}</h2><p class="real-name">${actress.name}</p>
      <div class="profile-metrics"><span><strong>${credits.length}</strong><small>series</small></span><span><strong>${pairsForActress(actress.id).length}</strong><small>parejas</small></span></div>
      ${pairCards ? `<section class="detail-section"><p class="section-kicker">PAREJAS ARTÍSTICAS</p><div class="compact-pair-grid">${pairCards}</div></section>` : ""}
      <section class="detail-section"><p class="section-kicker">TRAYECTORIA</p><div class="history-list">${history}</div></section>
    </div></div>`;
}

function showDetail(type, id, push = true) {
  if (push && dialog.open) {
    const current = dialog.dataset.current?.split(":");
    if (current?.length === 2) state.detailTrail.push(current);
  }
  const item = type === "series" ? byId(series, id) : type === "pair" ? byId(actingPairs, id) : byId(actresses, id);
  if (!item) return;
  document.querySelector("#detail-content").innerHTML = type === "series" ? seriesDetail(item) : type === "pair" ? pairDetail(item) : actressDetail(item);
  dialog.dataset.current = `${type}:${id}`;
  if (!dialog.open) dialog.showModal();
  dialog.scrollTop = 0;
}

function resetFilters() {
  Object.assign(state, { search: "", provider: "", pairings: [], country: "", releaseMonth: "", releaseYear: "", sort: "newest" });
  document.querySelector("#search-input").value = "";
  document.querySelector("#drama-filter").value = 5;
  document.querySelector("#drama-value").textContent = 5;
  document.querySelector("#country-filter").value = "";
  document.querySelector("#release-month-filter").value = "";
  document.querySelector("#release-year-filter").value = "";
  document.querySelector("#sort-select").value = "newest";
  document.querySelectorAll(".filters input[type=checkbox]").forEach((input) => { input.checked = false; });
  document.querySelector("#comfort-toggle").setAttribute("aria-checked", "false");
  renderProviders(); renderCards();
}

document.addEventListener("click", (event) => {
  const provider = event.target.closest("[data-provider]");
  if (provider) { state.provider = provider.dataset.provider; renderProviders(); renderCards(); }
  const save = event.target.closest("[data-save]");
  if (save) { event.stopPropagation(); state.saved.has(save.dataset.save) ? state.saved.delete(save.dataset.save) : state.saved.add(save.dataset.save); document.querySelector("#saved-count").textContent = state.saved.size; renderCards(); return; }
  const opener = event.target.closest("[data-open]");
  if (opener) { const [type, id] = opener.dataset.open.split(":"); showDetail(type, id); }
  if (event.target.closest("[data-open-featured]")) showDetail("series", "gap-2022");
  if (event.target.closest("[data-open-latest]") && series.length) showDetail("series", visibleSeries()[0].id);
  if (event.target.closest("[data-detail-back]")) { const previous = state.detailTrail.pop(); if (previous) showDetail(previous[0], previous[1], false); }
  if (event.target.closest("[data-quick-filter=comfort]")) { state.comfort = true; document.querySelector("#comfort-toggle").setAttribute("aria-checked", "true"); renderCards(); document.querySelector("#popular").scrollIntoView(); }
  if (event.target.closest("[data-reset]")) resetFilters();
  const remove = event.target.closest("[data-remove-filter]");
  if (remove) { const [type, value] = remove.dataset.removeFilter.split(":"); if (type === "search") { state.search = ""; document.querySelector("#search-input").value = ""; } if (type === "provider") { state.provider = ""; renderProviders(); } if (type === "drama") { state.drama = 5; document.querySelector("#drama-filter").value = 5; document.querySelector("#drama-value").textContent = 5; } if (type === "comfort") { state.comfort = false; document.querySelector("#comfort-toggle").setAttribute("aria-checked", "false"); } if (type === "ending") state.endings = state.endings.filter((ending) => ending !== value); if (type === "pairing") state.pairings = state.pairings.filter((role) => role !== value); if (type === "country") { state.country = ""; document.querySelector("#country-filter").value = ""; } if (type === "releaseMonth") { state.releaseMonth = ""; document.querySelector("#release-month-filter").value = ""; } if (type === "releaseYear") { state.releaseYear = ""; document.querySelector("#release-year-filter").value = ""; } renderCards(); }
});

document.addEventListener("error", (event) => {
  if (event.target.matches(".entity-media img, .poster > img, .cast-avatar img")) event.target.remove();
}, true);

document.querySelector("#search-input").addEventListener("input", (event) => { state.search = event.target.value.trim(); renderCards(); });
document.querySelector("#drama-filter").addEventListener("input", (event) => { state.drama = Number(event.target.value); document.querySelector("#drama-value").textContent = state.drama; renderCards(); });
document.querySelectorAll("input[name=ending]").forEach((input) => input.addEventListener("change", () => { state.endings = [...document.querySelectorAll("input[name=ending]:checked")].map((item) => item.value); renderCards(); }));
document.querySelectorAll("input[name=pairing]").forEach((input) => input.addEventListener("change", () => { state.pairings = [...document.querySelectorAll("input[name=pairing]:checked")].map((item) => item.value); renderCards(); }));
document.querySelector("#country-filter").addEventListener("change", (event) => { state.country = event.target.value; renderCards(); });
document.querySelector("#release-month-filter").addEventListener("change", (event) => { state.releaseMonth = event.target.value; renderCards(); });
document.querySelector("#release-year-filter").addEventListener("change", (event) => { state.releaseYear = event.target.value; renderCards(); });
document.querySelector("#sort-select").addEventListener("change", (event) => { state.sort = event.target.value; renderCards(); });
document.querySelector("#comfort-toggle").addEventListener("click", (event) => { state.comfort = event.currentTarget.getAttribute("aria-checked") !== "true"; event.currentTarget.setAttribute("aria-checked", String(state.comfort)); renderCards(); });
document.querySelector("#reset-filters").addEventListener("click", resetFilters);
document.querySelector(".dialog-close").addEventListener("click", () => { state.detailTrail = []; dialog.close(); });
dialog.addEventListener("click", (event) => { if (event.target === dialog) { state.detailTrail = []; dialog.close(); } });
document.addEventListener("keydown", (event) => { if ((event.metaKey || event.ctrlKey) && event.key === "k") { event.preventDefault(); document.querySelector("#search-input").focus(); } if (event.key === "Enter" && event.target.matches("[data-open]") && event.target.getAttribute("role") === "button") { const [type, id] = event.target.dataset.open.split(":"); showDetail(type, id); } });

async function loadCatalog() {
  try {
    const response = await fetch("/api/catalog");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    actresses = payload.actresses;
    actingPairs = payload.actingPairs;
    seriesPairings = payload.seriesPairings;
    series = payload.series;
    providers = [
      { id: "", name: "Todas", short: "GL", color: "#6f285f" },
      ...payload.platforms.map((platform) => ({ ...platform, short: platform.name.slice(0, 2).toUpperCase(), color: "#9b4d85" })),
    ];
    document.querySelector(".provider-section").hidden = payload.platforms.length === 0;
    const countries = [...new Set(series.map((item) => item.country))].sort((a, b) => a.localeCompare(b, "es"));
    document.querySelector("#country-filter").innerHTML = `<option value="">Todos los países</option>${countries.map((country) => `<option>${country}</option>`).join("")}`;
    renderProviders();
    renderReleaseFilters();
    renderCards();
    renderUniverse();
  } catch (error) {
    resultCount.textContent = "Sin conexión";
    grid.innerHTML = "";
    emptyState.hidden = false;
    emptyState.querySelector("h3").textContent = "No hemos podido cargar el catálogo";
    emptyState.querySelector("p").textContent = "Inicia GL Verse con el comando web y vuelve a intentarlo.";
    console.error("No se pudo cargar /api/catalog", error);
  }
}

loadCatalog();
