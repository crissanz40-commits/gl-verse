let actresses = [];
let actingPairs = [];
let seriesPairings = [];
let series = [];
let providers = [{ id: "", name: "Todas", short: "GL", color: "#6f285f" }];

const importanceLabels = { lead: "Protagonista", supporting: "Secundaria", guest: "Invitada" };
const roleLabels = { main: "Pareja principal", supporting: "Pareja secundaria" };
const statusLabels = { announced: "Anunciada", airing: "En emisión", completed: "Completada", cancelled: "Cancelada" };
const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
const dramaLevels = ["zero_drama", "light", "moderate", "high"];
const dramaLabels = { zero_drama: "Sin drama", light: "Suave", moderate: "Moderado", high: "Alto" };
const endingLabels = { happy_ever_after: "Feliz para siempre", happy_for_now: "Feliz por ahora", bittersweet: "Agridulce", open: "Abierto", sad: "Triste", tragic: "Trágico", unknown: "Sin confirmar" };
const companyRoleLabels = { producer: "Producción", broadcaster: "Emisión", distributor: "Distribución" };
const personalStatusLabels = { want_to_watch: "Quiero verla", watching: "Viendo", watched: "Vista", paused: "En pausa", dropped: "Abandonada" };
const state = { search: "", provider: "", pairings: [], country: "", releaseMonth: "", releaseYear: "", drama: 3, endings: [], comfort: false, tag: "", sort: "newest", saved: new Set(), detailTrail: [] };
const grid = document.querySelector("#series-grid");
const resultCount = document.querySelector("#result-count");
const activeFilters = document.querySelector("#active-filters");
const emptyState = document.querySelector("#empty-state");
const dialog = document.querySelector("#detail-dialog");
const watchlistDialog = document.querySelector("#watchlist-dialog");
const sessionStorageKey = "glv_session";
let authSession = null;
let personalEntries = new Map();
let watchlistStatus = "all";

function sessionHeaders(headers = {}) {
  const sessionToken = window.sessionStorage.getItem(sessionStorageKey);
  return { ...(sessionToken ? { Authorization: `Bearer ${sessionToken}` } : {}), ...headers };
}

async function loadIdentity() {
  try {
    const response = await fetch("/api/auth/session", { headers: sessionHeaders() });
    const session = await response.json();
    const login = document.querySelector("#google-login");
    if (!session.googleConfigured) {
      login.hidden = true;
      return;
    }
    if (!session.authenticated) {
      await setupGoogleLogin(login);
      return;
    }
    authSession = session;
    const logout = document.createElement("a");
    logout.href = "#logout";
    logout.textContent = `Salir · ${session.user.name || session.user.email}`;
    logout.addEventListener("click", async (event) => {
      event.preventDefault();
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: sessionHeaders({ "Content-Type": "application/json", "X-GL-Verse-CSRF": session.csrfToken }),
        body: "{}",
      });
      window.sessionStorage.removeItem(sessionStorageKey);
      window.location.reload();
    });
    login.replaceChildren(logout);
    document.querySelector("#admin-link").hidden = session.user.role !== "admin";
    await loadPersonalLibrary();
  } catch {
    // El catálogo público sigue disponible aunque falle la sesión.
  }
}

const escapeHtml = (value) => String(value ?? "").replace(/[&<>"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[character]);

async function personalRequest(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: sessionHeaders({
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(["PUT", "DELETE"].includes(options.method) ? { "X-GL-Verse-CSRF": authSession?.csrfToken || "" } : {}),
      ...(options.headers || {}),
    }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "No se pudo actualizar tu lista");
  return result;
}

async function loadPersonalLibrary() {
  const result = await personalRequest("/api/me/library");
  personalEntries = new Map(result.entries.map((entry) => [entry.seriesId, entry]));
  state.saved = new Set(personalEntries.keys());
  renderPersonalState();
}

function renderPersonalState() {
  document.querySelector("#saved-count").textContent = personalEntries.size;
  renderCards();
  renderWatchlist();
  const current = dialog.dataset.current?.split(":");
  if (dialog.open && current?.[0] === "series") showDetail("series", current[1], false);
}

function personalForm(item) {
  if (!authSession) return `<section class="personal-card signed-out"><p class="section-kicker">MI SEGUIMIENTO</p><strong>Inicia sesión para crear tu lista</strong><p>Tu progreso, notas y opiniones quedarán asociados únicamente a tu cuenta.</p></section>`;
  const entry = personalEntries.get(item.id);
  const totalEpisodes = item.seasons.reduce((total, season) => total + season.episodes.length, 0);
  const ratingOptions = Array.from({ length: 10 }, (_, index) => index + 1).map((score) => `<option value="${score}" ${entry?.rating === score ? "selected" : ""}>${score}/10</option>`).join("");
  const statusOptions = Object.entries(personalStatusLabels).map(([value, label]) => `<option value="${value}" ${entry?.status === value ? "selected" : ""}>${label}</option>`).join("");
  return `<section class="personal-card">
    <div class="personal-heading"><div><p class="section-kicker">MI SEGUIMIENTO</p><h3>${entry ? personalStatusLabels[entry.status] : "Añadir a mi lista"}</h3></div>${entry ? `<span>Actualizada ${new Date(entry.updatedAt).toLocaleDateString("es")}</span>` : ""}</div>
    <form data-personal-form="${item.id}">
      <label>Estado<select name="status">${statusOptions}</select></label>
      <label>Episodios vistos<span class="episode-input"><input name="episodesWatched" type="number" min="0" max="${totalEpisodes || 9999}" value="${entry?.episodesWatched ?? 0}" /><small>${totalEpisodes ? `de ${totalEpisodes}` : "total por confirmar"}</small></span></label>
      <label>Mi nota<select name="rating"><option value="">Sin puntuar</option>${ratingOptions}</select></label>
      <label>Empecé el<input name="startedOn" type="date" value="${entry?.startedOn || ""}" /></label>
      <label>Terminé el<input name="completedOn" type="date" value="${entry?.completedOn || ""}" /></label>
      <label class="review-field">Mi opinión<textarea name="review" maxlength="2000" rows="4" placeholder="¿Qué te gustó? ¿La recomendarías?">${escapeHtml(entry?.review || "")}</textarea><small>Privada · máximo 2000 caracteres</small></label>
      <div class="personal-actions"><button class="primary-button" type="submit">Guardar cambios</button>${entry ? '<button class="danger-button" type="button" data-delete-personal>Eliminar de mi lista</button>' : ""}<span class="personal-feedback" aria-live="polite"></span></div>
    </form>
  </section>`;
}

function renderWatchlist() {
  const tabs = document.querySelector("#watchlist-tabs");
  const list = document.querySelector("#watchlist-grid");
  if (!tabs || !list) return;
  const counts = Object.fromEntries(Object.keys(personalStatusLabels).map((status) => [status, [...personalEntries.values()].filter((entry) => entry.status === status).length]));
  tabs.innerHTML = [["all", "Todas"], ...Object.entries(personalStatusLabels)].map(([value, label]) => `<button type="button" class="${watchlistStatus === value ? "active" : ""}" data-watchlist-status="${value}">${label}<span>${value === "all" ? personalEntries.size : counts[value]}</span></button>`).join("");
  if (!authSession) {
    list.innerHTML = '<div class="watchlist-empty"><strong>Inicia sesión para usar Mi lista</strong><p>Guarda series, controla tu progreso y conserva tus valoraciones en cualquier dispositivo.</p></div>';
    return;
  }
  const entries = [...personalEntries.values()].filter((entry) => watchlistStatus === "all" || entry.status === watchlistStatus);
  list.innerHTML = entries.length ? entries.map((entry) => `<button class="watchlist-row" type="button" data-watchlist-open="${entry.seriesId}">
    <span class="watchlist-cover">${entry.coverImageUrl ? `<img src="${entry.coverImageUrl}" alt="" />` : "GL"}</span>
    <span><small>${personalStatusLabels[entry.status]}</small><strong>${escapeHtml(entry.title)}</strong><em>${entry.totalEpisodes ? `${entry.episodesWatched}/${entry.totalEpisodes} episodios` : `${entry.episodesWatched} episodios`}${entry.rating ? ` · ${entry.rating}/10` : ""}</em></span><b>Editar →</b>
  </button>`).join("") : '<div class="watchlist-empty"><strong>Aquí todavía no hay series</strong><p>Añádelas desde el corazón de una portada o desde su ficha.</p></div>';
}

function loadGoogleLibrary() {
  if (window.google?.accounts?.id) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.onload = resolve;
    script.onerror = () => reject(new Error("No se pudo cargar Google Identity Services"));
    document.head.append(script);
  });
}

async function finishGoogleLogin(credential, config) {
  const response = await fetch("/api/auth/google", {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ credential, loginCsrf: config.loginCsrf }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "No se pudo iniciar sesión con Google");
  return result;
}

async function setupGoogleLogin(container) {
  const response = await fetch("/api/auth/google/start?next=/");
  if (!response.ok) throw new Error("Google no está configurado");
  const config = await response.json();
  await loadGoogleLibrary();
  window.google.accounts.id.initialize({
    client_id: config.clientId,
    nonce: config.nonce,
    callback: async ({ credential }) => {
      try {
        const result = await finishGoogleLogin(credential, config);
        window.sessionStorage.setItem(sessionStorageKey, result.sessionToken);
        window.location.replace(result.nextPath);
      } catch (error) {
        container.textContent = error.message;
      }
    },
  });
  window.google.accounts.id.renderButton(container, { theme: "outline", size: "medium" });
}

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
    return `${seriesPairing.characters.join(" · ")} · ${pair?.name || "Pareja artística no registrada"}`;
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
    const guide = item.viewingGuide;
    const endingGroup = guide && (["happy_ever_after", "happy_for_now"].includes(guide.endingType) ? "happy" : ["sad", "tragic"].includes(guide.endingType) ? "sad" : guide.endingType);
    return (!term || searchable.includes(term))
      && (!state.pairings.length || state.pairings.some((role) => roles.includes(role)))
      && (!state.provider || item.availability.some((entry) => entry.platformId === state.provider))
      && (!state.country || item.country === state.country)
      && (!state.releaseMonth || releaseMonth === state.releaseMonth.padStart(2, "0"))
      && (!state.releaseYear || releaseYear === state.releaseYear)
      && (state.drama === 3 || (guide && dramaLevels.indexOf(guide.dramaLevel) <= state.drama))
      && (!state.endings.length || (guide && state.endings.includes(endingGroup)))
      && (!state.comfort || (guide && guide.dramaLevel === "zero_drama" && ["happy_ever_after", "happy_for_now"].includes(guide.endingType)))
      && (!state.tag || item.tags.some((tag) => tag.id === state.tag));
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
      <div class="card-info"><h3>${item.title}</h3><span class="card-meta">${formatReleaseDate(item.releaseDate)} · ${statusLabels[item.status] || item.status}</span>${personalEntries.has(item.id) ? `<span class="personal-status">${personalStatusLabels[personalEntries.get(item.id).status]}${personalEntries.get(item.id).rating ? ` · ${personalEntries.get(item.id).rating}/10` : ""}</span>` : ""}${item.reviewStatus === "approved" ? '<span class="review-badge">✓ Ficha revisada</span>' : ""}<div class="pair-row"><span class="pair-name">♡ ${pairingSummary(item)}</span></div></div>
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
  if (state.drama < 3) chips.push([`Drama: hasta ${dramaLabels[dramaLevels[state.drama]]}`, "drama"]);
  state.endings.forEach((value) => chips.push([`Final: ${value}`, `ending:${value}`]));
  if (state.comfort) chips.push(["Modo confort", "comfort"]);
  if (state.tag) chips.push([series.flatMap((item) => item.tags).find((tag) => tag.id === state.tag)?.name || state.tag, "tag"]);
  activeFilters.innerHTML = chips.map(([label, key]) => `<button class="filter-chip" type="button" data-remove-filter="${key}">${label}</button>`).join("");
}

function detailHeader(label, canGoBack = true) {
  return `<div class="detail-toolbar">${canGoBack && state.detailTrail.length ? '<button type="button" data-detail-back>← Volver</button>' : '<span></span>'}<span>${label}</span></div>`;
}

function seriesDetail(item) {
  const pairings = pairingsForSeries(item.id);
  const pairCards = pairings.map((seriesPairing) => {
    const pair = byId(actingPairs, seriesPairing.pairId);
    if (!pair) {
      return `<div class="relation-card pair-relation">
        <span class="relation-avatar" style="--media-start:#8b7182;--media-end:#c9a9bc">♡</span>
        <span><small>${roleLabels[seriesPairing.role]}</small><strong>${seriesPairing.characters.join(" · ")}</strong><em>Pareja artística no registrada</em></span>
      </div>`;
    }
    return `<button class="relation-card pair-relation" type="button" data-open="pair:${pair.id}">
      <span class="relation-avatar" style="--media-start:${pair.colors[0]};--media-end:${pair.colors[1]}">${pair.initials}</span>
      <span><small>${roleLabels[seriesPairing.role]}</small><strong>${seriesPairing.characters.join(" · ")}</strong><em>${pair.name} →</em></span>
    </button>`;
  }).join("");
  const castCards = item.cast.map((credit) => {
    const actress = byId(actresses, credit.actressId);
    const characterPairing = pairings.find((pairing) => pairing.characters.includes(credit.character));
    const actingPair = characterPairing ? byId(actingPairs, characterPairing.pairId) : null;
    const status = actingPair?.name || (characterPairing ? "Pareja artística no registrada" : "Sin pareja en esta serie");
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
  const guide = item.viewingGuide;
  const guideCard = guide ? `<section class="detail-section"><p class="section-kicker">GUÍA DE VISIONADO</p><div class="metadata-grid"><span><small>DRAMA</small><strong>${dramaLabels[guide.dramaLevel]}</strong></span><span><small>FINAL</small><strong>${endingLabels[guide.endingType]}</strong></span></div>${guide.endingNote ? `<p class="pending-copy">${guide.endingNote}</p>` : ""}</section>` : "";
  const tagCards = item.tags.map((tag) => `<span class="metadata-chip">${tag.name}</span>`).join("");
  const companyCards = item.companies.map((company) => `<div class="metadata-row"><strong>${company.name}</strong><small>${companyRoleLabels[company.role]}</small></div>`).join("");
  const collectionCards = item.collections.map((collection) => `<div class="metadata-row"><strong>${collection.title}</strong><small>${collection.kind} · parte ${collection.position}</small></div>`).join("");
  const warningCards = item.contentWarnings.map((warning) => `<div class="warning-row ${warning.severity}"><strong>${warning.name}</strong><small>${warning.description || "Sin descripción adicional"}</small></div>`).join("");
  const seasonCards = item.seasons.map((season) => `<details class="season-row"><summary>Temporada ${season.number}${season.title ? ` · ${season.title}` : ""} <small>${season.episodes.length} episodios</small></summary>${season.episodes.map((episode) => `<p><strong>${episode.kind === "special" ? "Especial" : `Episodio ${episode.number}`}</strong><span>${episode.title || "Título pendiente"}${episode.durationMinutes ? ` · ${episode.durationMinutes} min` : ""}</span></p>`).join("")}</details>`).join("");
  return `${detailHeader("Ficha de serie")}
    <div class="detail-layout series-layout">
      <aside>${mediaMarkup(item, "cover", `Portada de ${item.title}`)}</aside>
      <div class="detail-main"><p class="eyebrow">${item.country.toUpperCase()} · ${formatReleaseDate(item.releaseDate).toUpperCase()}</p><h2>${item.title}</h2><p class="detail-lead">${item.synopsis}</p>${item.releaseDateSourceUrl ? `<a class="release-source" href="${item.releaseDateSourceUrl}" target="_blank" rel="noreferrer">Fuente de la fecha de estreno ↗</a>` : ""}
        <div class="score-strip"><span><small>ESTADO</small><strong>${statusLabels[item.status] || item.status}</strong></span><span><small>ESTRENO</small><strong>${item.year}</strong></span><span><small>PAÍS</small><strong>${item.country}</strong></span><span><small>REPARTO</small><strong>${item.cast.length}</strong></span></div>
        ${personalForm(item)}
        <section class="detail-section"><p class="section-kicker">DÓNDE VER</p><div class="availability-list">${availabilityCards || '<p class="pending-copy">Disponibilidad pendiente de verificar.</p>'}</div></section>
        ${guideCard}
        ${tagCards ? `<section class="detail-section"><p class="section-kicker">ETIQUETAS</p><div class="metadata-chips">${tagCards}</div></section>` : ""}
        ${companyCards ? `<section class="detail-section"><p class="section-kicker">EMPRESAS</p><div class="metadata-list">${companyCards}</div></section>` : ""}
        ${collectionCards ? `<section class="detail-section"><p class="section-kicker">COLECCIONES</p><div class="metadata-list">${collectionCards}</div></section>` : ""}
        ${seasonCards ? `<section class="detail-section"><p class="section-kicker">EPISODIOS</p><div class="metadata-list">${seasonCards}</div></section>` : ""}
        ${warningCards ? `<section class="detail-section"><p class="section-kicker">AVISOS DE CONTENIDO</p><div class="metadata-list">${warningCards}</div></section>` : ""}
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
    const characterPairing = pairingsForSeries(credit.series.id).find((pairing) => pairing.characters.includes(credit.character));
    const actingPair = characterPairing ? byId(actingPairs, characterPairing.pairId) : null;
    const pairText = actingPair ? `Con ${actingPair.name}` : characterPairing ? "Pareja artística no registrada" : "Sin pareja en esta serie";
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
  Object.assign(state, { search: "", provider: "", pairings: [], country: "", releaseMonth: "", releaseYear: "", drama: 3, endings: [], comfort: false, tag: "", sort: "newest" });
  document.querySelector("#search-input").value = "";
  document.querySelector("#drama-filter").value = 3;
  document.querySelector("#drama-value").textContent = 3;
  document.querySelector("#country-filter").value = "";
  document.querySelector("#release-month-filter").value = "";
  document.querySelector("#release-year-filter").value = "";
  document.querySelector("#tag-filter").value = "";
  document.querySelector("#sort-select").value = "newest";
  document.querySelectorAll(".filters input[type=checkbox]").forEach((input) => { input.checked = false; });
  document.querySelector("#comfort-toggle").setAttribute("aria-checked", "false");
  renderProviders(); renderCards();
}

document.addEventListener("click", async (event) => {
  const provider = event.target.closest("[data-provider]");
  if (provider) { state.provider = provider.dataset.provider; renderProviders(); renderCards(); }
  const save = event.target.closest("[data-save]");
  if (save) {
    event.stopPropagation();
    if (!authSession) { document.querySelector("#google-login").scrollIntoView({ behavior: "smooth" }); return; }
    try {
      const existing = personalEntries.get(save.dataset.save);
      if (existing) {
        await personalRequest(`/api/me/library/${encodeURIComponent(save.dataset.save)}`, { method: "DELETE" });
        personalEntries.delete(save.dataset.save);
      } else {
        const entry = await personalRequest(`/api/me/library/${encodeURIComponent(save.dataset.save)}`, {
          method: "PUT",
          body: JSON.stringify({ status: "want_to_watch", episodesWatched: 0, rating: null, review: null, startedOn: null, completedOn: null }),
        });
        personalEntries.set(entry.seriesId, entry);
      }
      state.saved = new Set(personalEntries.keys());
      renderPersonalState();
    } catch (error) { window.alert(error.message); }
    return;
  }
  const watchlistFilter = event.target.closest("[data-watchlist-status]");
  if (watchlistFilter) { watchlistStatus = watchlistFilter.dataset.watchlistStatus; renderWatchlist(); return; }
  const watchlistOpen = event.target.closest("[data-watchlist-open]");
  if (watchlistOpen) { watchlistDialog.close(); showDetail("series", watchlistOpen.dataset.watchlistOpen); return; }
  if (event.target.closest(".watchlist-button")) { renderWatchlist(); watchlistDialog.showModal(); return; }
  if (event.target.closest("[data-delete-personal]")) {
    const form = event.target.closest("form");
    if (!window.confirm("¿Eliminar esta serie y todo su seguimiento personal?")) return;
    try {
      await personalRequest(`/api/me/library/${encodeURIComponent(form.dataset.personalForm)}`, { method: "DELETE" });
      personalEntries.delete(form.dataset.personalForm);
      state.saved = new Set(personalEntries.keys());
      renderPersonalState();
    } catch (error) { form.querySelector(".personal-feedback").textContent = error.message; }
    return;
  }
  const opener = event.target.closest("[data-open]");
  if (opener) { const [type, id] = opener.dataset.open.split(":"); showDetail(type, id); }
  if (event.target.closest("[data-open-featured]")) showDetail("series", "gap-2022");
  if (event.target.closest("[data-open-latest]") && series.length) showDetail("series", visibleSeries()[0].id);
  if (event.target.closest("[data-detail-back]")) { const previous = state.detailTrail.pop(); if (previous) showDetail(previous[0], previous[1], false); }
  if (event.target.closest("[data-quick-filter=comfort]")) { state.comfort = true; document.querySelector("#comfort-toggle").setAttribute("aria-checked", "true"); renderCards(); document.querySelector("#popular").scrollIntoView(); }
  if (event.target.closest("[data-reset]")) resetFilters();
  const remove = event.target.closest("[data-remove-filter]");
  if (remove) { const [type, value] = remove.dataset.removeFilter.split(":"); if (type === "search") { state.search = ""; document.querySelector("#search-input").value = ""; } if (type === "provider") { state.provider = ""; renderProviders(); } if (type === "drama") { state.drama = 3; document.querySelector("#drama-filter").value = 3; document.querySelector("#drama-value").textContent = 3; } if (type === "comfort") { state.comfort = false; document.querySelector("#comfort-toggle").setAttribute("aria-checked", "false"); } if (type === "ending") state.endings = state.endings.filter((ending) => ending !== value); if (type === "tag") { state.tag = ""; document.querySelector("#tag-filter").value = ""; } if (type === "pairing") state.pairings = state.pairings.filter((role) => role !== value); if (type === "country") { state.country = ""; document.querySelector("#country-filter").value = ""; } if (type === "releaseMonth") { state.releaseMonth = ""; document.querySelector("#release-month-filter").value = ""; } if (type === "releaseYear") { state.releaseYear = ""; document.querySelector("#release-year-filter").value = ""; } renderCards(); }
});

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("[data-personal-form]");
  if (!form) return;
  event.preventDefault();
  const feedback = form.querySelector(".personal-feedback");
  const values = new FormData(form);
  feedback.textContent = "Guardando…";
  try {
    const entry = await personalRequest(`/api/me/library/${encodeURIComponent(form.dataset.personalForm)}`, {
      method: "PUT",
      body: JSON.stringify({
        status: values.get("status"),
        episodesWatched: Number(values.get("episodesWatched")),
        rating: values.get("rating") ? Number(values.get("rating")) : null,
        review: values.get("review") || null,
        startedOn: values.get("startedOn") || null,
        completedOn: values.get("completedOn") || null,
      }),
    });
    personalEntries.set(entry.seriesId, entry);
    state.saved = new Set(personalEntries.keys());
    renderPersonalState();
  } catch (error) { feedback.textContent = error.message; }
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
document.querySelector("#tag-filter").addEventListener("change", (event) => { state.tag = event.target.value; renderCards(); });
document.querySelector("#sort-select").addEventListener("change", (event) => { state.sort = event.target.value; renderCards(); });
document.querySelector("#comfort-toggle").addEventListener("click", (event) => { state.comfort = event.currentTarget.getAttribute("aria-checked") !== "true"; event.currentTarget.setAttribute("aria-checked", String(state.comfort)); renderCards(); });
document.querySelector("#reset-filters").addEventListener("click", resetFilters);
document.querySelector(".dialog-close").addEventListener("click", () => { state.detailTrail = []; dialog.close(); });
dialog.addEventListener("click", (event) => { if (event.target === dialog) { state.detailTrail = []; dialog.close(); } });
watchlistDialog.querySelector(".dialog-close").addEventListener("click", () => watchlistDialog.close());
watchlistDialog.addEventListener("click", (event) => { if (event.target === watchlistDialog) watchlistDialog.close(); });
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
    const hasViewingGuides = series.some((item) => item.viewingGuide);
    document.querySelector("#drama-fieldset").hidden = !hasViewingGuides;
    document.querySelector("#ending-fieldset").hidden = !hasViewingGuides;
    document.querySelector("#comfort-box").hidden = !hasViewingGuides;
    document.querySelector("#tag-fieldset").hidden = payload.tags.length === 0;
    document.querySelector("#tag-filter").innerHTML = `<option value="">Todas las etiquetas</option>${payload.tags.map((tag) => `<option value="${tag.id}">${tag.name}</option>`).join("")}`;
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

loadIdentity();
loadCatalog();
