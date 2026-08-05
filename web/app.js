const series = [
  { id: "gap", title: "GAP: The Series", year: 2022, country: "Tailandia", pair: "Sam · Mon", actors: "FreenBecky", role: "main", ending: "happy", drama: 2, chemistry: 9.6, popularity: 100, provider: "YouTube", initials: "GM", colors: ["#62224f", "#da6296"], synopsis: "Mon empieza a trabajar en la empresa de Sam, a quien admira desde joven. La distancia entre sus mundos se convierte poco a poco en una historia de amor." },
  { id: "loyal-pin", title: "The Loyal Pin", year: 2024, country: "Tailandia", pair: "Anin · Pin", actors: "FreenBecky", role: "main", ending: "happy", drama: 3, chemistry: 9.5, popularity: 94, provider: "YouTube", initials: "AP", colors: ["#774626", "#d7a75a"], synopsis: "Una historia de época sobre dos jóvenes unidas desde la infancia que deben proteger un amor enfrentado a las expectativas de palacio." },
  { id: "pluto", title: "Pluto", year: 2024, country: "Tailandia", pair: "Ai-oon · May", actors: "NamtanFilm", role: "main", ending: "happy", drama: 4, chemistry: 9.4, popularity: 97, provider: "YouTube", initials: "AM", colors: ["#152950", "#7954a6"], synopsis: "Una identidad prestada y un vínculo inesperado abren un misterio romántico donde cada verdad cambia lo que creemos saber de la pareja." },
  { id: "23-5", title: "23.5", year: 2024, country: "Tailandia", pair: "Ongsa · Sun", actors: "MilkLove", role: "main", ending: "happy", drama: 1, chemistry: 8.9, popularity: 88, provider: "Netflix", initials: "OS", colors: ["#db744f", "#f5b766"], synopsis: "Ongsa, tímida y enamorada, conoce online a la popular Sun bajo un nombre que oculta quién es. Una comedia romántica luminosa y juvenil." },
  { id: "secret-of-us", title: "The Secret of Us", year: 2024, country: "Tailandia", pair: "Lada · Earn", actors: "LingOrm", role: "main", ending: "happy", drama: 4, chemistry: 9.3, popularity: 96, provider: "Ch3+", initials: "LE", colors: ["#315a5b", "#8bb596"], synopsis: "Dos antiguas amantes vuelven a encontrarse cuando sus vidas profesionales se cruzan, obligándolas a mirar de frente una ruptura nunca resuelta." },
  { id: "affair", title: "Affair", year: 2024, country: "Tailandia", pair: "Wan · Pleng", actors: "LMSY", role: "main", ending: "happy", drama: 5, chemistry: 9.2, popularity: 90, provider: "iQIYI", initials: "WP", colors: ["#682936", "#bf6a6f"], synopsis: "La amistad inseparable entre Wan y Pleng se transforma en algo más profundo mientras el tiempo, la familia y sus decisiones ponen a prueba el vínculo." },
];

const providers = [
  { name: "Todas", short: "GL", color: "#6f285f" },
  { name: "YouTube", short: "YT", color: "#e74355" },
  { name: "Netflix", short: "N", color: "#18151b" },
  { name: "Ch3+", short: "3+", color: "#3265a8" },
  { name: "iQIYI", short: "iQI", color: "#79b928" },
  { name: "WeTV", short: "W", color: "#ff8a31" },
];

const state = { search: "", provider: "Todas", drama: 5, endings: [], pairings: [], country: "", comfort: false, sort: "popular", saved: new Set() };
const grid = document.querySelector("#series-grid");
const resultCount = document.querySelector("#result-count");
const activeFilters = document.querySelector("#active-filters");
const emptyState = document.querySelector("#empty-state");
const dialog = document.querySelector("#detail-dialog");

function renderProviders() {
  document.querySelector("#provider-list").innerHTML = providers.map((provider) => `
    <button class="provider-pill ${state.provider === provider.name ? "active" : ""}" type="button" data-provider="${provider.name}">
      <span class="provider-icon" style="background:${provider.color}">${provider.short}</span>
      <span>${provider.name}<small>${provider.name === "Todas" ? "Todo el catálogo" : "Ver disponibles"}</small></span>
    </button>`).join("");
}

function visibleSeries() {
  const term = state.search.toLocaleLowerCase("es");
  return series.filter((item) => {
    const searchable = `${item.title} ${item.pair} ${item.actors}`.toLocaleLowerCase("es");
    return (!term || searchable.includes(term))
      && (state.provider === "Todas" || item.provider === state.provider)
      && item.drama <= state.drama
      && (!state.endings.length || state.endings.includes(item.ending))
      && (!state.pairings.length || state.pairings.includes(item.role))
      && (!state.country || item.country === state.country)
      && (!state.comfort || (item.ending === "happy" && item.drama <= 2));
  }).sort((a, b) => {
    if (state.sort === "chemistry") return b.chemistry - a.chemistry;
    if (state.sort === "newest") return b.year - a.year;
    if (state.sort === "drama") return a.drama - b.drama;
    return b.popularity - a.popularity;
  });
}

function renderCards() {
  const items = visibleSeries();
  resultCount.textContent = `${items.length} ${items.length === 1 ? "título" : "títulos"}`;
  grid.innerHTML = items.map((item, index) => `
    <article class="series-card">
      <div class="poster" role="button" tabindex="0" data-series="${item.id}" data-initials="${item.initials}" style="background:linear-gradient(145deg,${item.colors[0]},${item.colors[1]})">
        <div class="poster-top"><span class="rank">#${index + 1}</span><button class="save-button ${state.saved.has(item.id) ? "saved" : ""}" type="button" data-save="${item.id}" aria-label="Guardar ${item.title}">${state.saved.has(item.id) ? "♥" : "♡"}</button></div>
        <div class="poster-title"><small>${item.country.toUpperCase()} · ${item.year}</small><strong>${item.title}</strong></div>
      </div>
      <div class="card-info"><h3>${item.title}</h3><span class="card-meta">${item.year} · ${item.provider} · Drama ${item.drama}/5</span><div class="pair-row"><span class="pair-name">♡ ${item.pair} · ${item.actors}</span><span class="badges"><span class="badge happy">☺ FELIZ</span><span class="badge drama">✦ ${item.chemistry}</span></span></div></div>
    </article>`).join("");
  emptyState.hidden = items.length > 0;
  renderActiveFilters();
}

function renderActiveFilters() {
  const chips = [];
  if (state.search) chips.push([`Búsqueda: ${state.search}`, "search"]);
  if (state.provider !== "Todas") chips.push([state.provider, "provider"]);
  if (state.drama < 5) chips.push([`Drama ≤ ${state.drama}`, "drama"]);
  if (state.comfort) chips.push(["Modo confort", "comfort"]);
  state.endings.forEach((value) => chips.push([value === "happy" ? "Final feliz" : `Final ${value}`, `ending:${value}`]));
  if (state.country) chips.push([state.country, "country"]);
  activeFilters.innerHTML = chips.map(([label, key]) => `<button class="filter-chip" type="button" data-remove-filter="${key}">${label}</button>`).join("");
}

function showDetail(id) {
  const item = series.find((candidate) => candidate.id === id);
  if (!item) return;
  document.querySelector("#detail-content").innerHTML = `
    <div class="detail-hero" style="background:linear-gradient(135deg,${item.colors[0]},${item.colors[1]})"><div><p class="eyebrow">${item.country.toUpperCase()} · ${item.year}</p><h2>${item.title}</h2></div></div>
    <div class="detail-body"><div><div class="pair-card"><small>PAREJA PRINCIPAL</small><h3>${item.pair}</h3><p>Interpretada por <strong>${item.actors}</strong></p></div><p>${item.synopsis}</p></div><div><div class="score-grid"><div><span>QUÍMICA</span><strong>✦ ${item.chemistry}</strong></div><div><span>DRAMA</span><strong>${item.drama}/5</strong></div><div><span>FINAL</span><strong>☺ Feliz</strong></div><div><span>ROL</span><strong>Principal</strong></div></div><div class="where-to-watch"><span>Disponible en</span><strong>${item.provider}</strong></div></div></div>`;
  dialog.showModal();
}

function resetFilters() {
  Object.assign(state, { search: "", provider: "Todas", drama: 5, endings: [], pairings: [], country: "", comfort: false, sort: "popular" });
  document.querySelector("#search-input").value = "";
  document.querySelector("#drama-filter").value = 5;
  document.querySelector("#drama-value").textContent = 5;
  document.querySelector("#country-filter").value = "";
  document.querySelector("#sort-select").value = "popular";
  document.querySelectorAll(".filters input[type=checkbox]").forEach((input) => { input.checked = false; });
  document.querySelector("#comfort-toggle").setAttribute("aria-checked", "false");
  renderProviders(); renderCards();
}

document.addEventListener("click", (event) => {
  const provider = event.target.closest("[data-provider]");
  if (provider) { state.provider = provider.dataset.provider; renderProviders(); renderCards(); }
  const save = event.target.closest("[data-save]");
  if (save) { event.stopPropagation(); state.saved.has(save.dataset.save) ? state.saved.delete(save.dataset.save) : state.saved.add(save.dataset.save); document.querySelector("#saved-count").textContent = state.saved.size; renderCards(); }
  const poster = event.target.closest("[data-series]");
  if (poster) showDetail(poster.dataset.series);
  if (event.target.closest("[data-open-featured]")) showDetail("gap");
  if (event.target.closest("[data-quick-filter=comfort]")) { state.comfort = true; document.querySelector("#comfort-toggle").setAttribute("aria-checked", "true"); renderCards(); document.querySelector("#popular").scrollIntoView(); }
  if (event.target.closest("[data-reset]")) resetFilters();
  const remove = event.target.closest("[data-remove-filter]");
  if (remove) { const [type, value] = remove.dataset.removeFilter.split(":"); if (type === "search") { state.search = ""; document.querySelector("#search-input").value = ""; } if (type === "provider") { state.provider = "Todas"; renderProviders(); } if (type === "drama") { state.drama = 5; document.querySelector("#drama-filter").value = 5; document.querySelector("#drama-value").textContent = 5; } if (type === "comfort") { state.comfort = false; document.querySelector("#comfort-toggle").setAttribute("aria-checked", "false"); } if (type === "ending") { state.endings = state.endings.filter((ending) => ending !== value); document.querySelector(`input[name=ending][value=${value}]`).checked = false; } if (type === "country") { state.country = ""; document.querySelector("#country-filter").value = ""; } renderCards(); }
});

document.querySelector("#search-input").addEventListener("input", (event) => { state.search = event.target.value.trim(); renderCards(); });
document.querySelector("#drama-filter").addEventListener("input", (event) => { state.drama = Number(event.target.value); document.querySelector("#drama-value").textContent = state.drama; renderCards(); });
document.querySelectorAll("input[name=ending]").forEach((input) => input.addEventListener("change", () => { state.endings = [...document.querySelectorAll("input[name=ending]:checked")].map((item) => item.value); renderCards(); }));
document.querySelectorAll("input[name=pairing]").forEach((input) => input.addEventListener("change", () => { state.pairings = [...document.querySelectorAll("input[name=pairing]:checked")].map((item) => item.value); renderCards(); }));
document.querySelector("#country-filter").addEventListener("change", (event) => { state.country = event.target.value; renderCards(); });
document.querySelector("#sort-select").addEventListener("change", (event) => { state.sort = event.target.value; renderCards(); });
document.querySelector("#comfort-toggle").addEventListener("click", (event) => { state.comfort = event.currentTarget.getAttribute("aria-checked") !== "true"; event.currentTarget.setAttribute("aria-checked", String(state.comfort)); renderCards(); });
document.querySelector("#reset-filters").addEventListener("click", resetFilters);
document.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
document.addEventListener("keydown", (event) => { if ((event.metaKey || event.ctrlKey) && event.key === "k") { event.preventDefault(); document.querySelector("#search-input").focus(); } if (event.key === "Enter" && event.target.matches("[data-series]")) showDetail(event.target.dataset.series); });

renderProviders();
renderCards();
