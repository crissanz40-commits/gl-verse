const actresses = [
  { id: "freen", name: "Sarocha Chankimha", stageName: "Freen", initials: "FS", colors: ["#63325a", "#d76f9c"], imageUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Freen_Sarocha_Chankimha_2026-01-12.jpg/500px-Freen_Sarocha_Chankimha_2026-01-12.jpg", imageSourceUrl: "https://commons.wikimedia.org/wiki/File:Freen_Sarocha_Chankimha_2026-01-12.jpg" },
  { id: "becky", name: "Rebecca Armstrong", stageName: "Becky", initials: "BA", colors: ["#7d3c55", "#e6a17f"], imageUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Becky_Rebecca_Long_Live_Love_movie_%282023%29.jpg/500px-Becky_Rebecca_Long_Live_Love_movie_%282023%29.jpg", imageSourceUrl: "https://commons.wikimedia.org/wiki/File:Becky_Rebecca_Long_Live_Love_movie_(2023).jpg" },
  { id: "namtan", name: "Tipnaree Weerawatnodom", stageName: "Namtan", initials: "NT", colors: ["#203b70", "#7761ae"], imageUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Tipnaree_2024-12-27.png/500px-Tipnaree_2024-12-27.png", imageSourceUrl: "https://commons.wikimedia.org/wiki/File:Tipnaree_2024-12-27.png" },
  { id: "film", name: "Rachanun Mahawan", stageName: "Film", initials: "FR", colors: ["#423b7e", "#a66ab1"], imageUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Rachanun_Mahawan_at_Seoul_International_Drama_Awards%2C_2_October_2025_04.png/500px-Rachanun_Mahawan_at_Seoul_International_Drama_Awards%2C_2_October_2025_04.png", imageSourceUrl: "https://commons.wikimedia.org/wiki/File:Rachanun_Mahawan_at_Seoul_International_Drama_Awards,_2_October_2025_04.png" },
  { id: "milk", name: "Pansa Vosbein", stageName: "Milk", initials: "MP", colors: ["#a14b3e", "#e99568"], imageUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/MilkPansaBookfluencer.jpg/500px-MilkPansaBookfluencer.jpg", imageSourceUrl: "https://commons.wikimedia.org/wiki/File:MilkPansaBookfluencer.jpg" },
  { id: "love", name: "Pattranite Limpatiyakorn", stageName: "Love", initials: "LP", colors: ["#ca6a75", "#f1b88d"], imageUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Pattranite_2024-11-27.png/500px-Pattranite_2024-11-27.png", imageSourceUrl: "https://commons.wikimedia.org/wiki/File:Pattranite_2024-11-27.png" },
  { id: "ciize", name: "Apichaya Saejung", stageName: "Ciize", initials: "CA", colors: ["#285a69", "#6eb6ad"], imageUrl: "https://www.gmm-tv.com/cms/upload_file/vj_floating2026/pic/Ciize_800.jpg", imageSourceUrl: "https://www.gmm-tv.com/artists/view/24/" },
  { id: "lingling", name: "Sirila Kwong", stageName: "Lingling", initials: "LK", colors: ["#315a5b", "#81a88f"], imageUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Lingling_Kwong_%40_The_Secret_Of_Us.png/500px-Lingling_Kwong_%40_The_Secret_Of_Us.png", imageSourceUrl: "https://commons.wikimedia.org/wiki/File:Lingling_Kwong_@_The_Secret_Of_Us.png" },
  { id: "orm", name: "Kornnaphat Sethratanapong", stageName: "Orm", initials: "OK", colors: ["#4b6d5c", "#b2c991"], imageUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Orm_Kornnaphat_%40_The_Secret_Of_Us.png/500px-Orm_Kornnaphat_%40_The_Secret_Of_Us.png", imageSourceUrl: "https://commons.wikimedia.org/wiki/File:Orm_Kornnaphat_@_The_Secret_Of_Us.png" },
  { id: "lookmhee", name: "Punyapat Wangpongsathaporn", stageName: "Lookmhee", initials: "LP", colors: ["#693344", "#c96d78"], imageUrl: "https://www.change2561.com/assets/uploads/img/Artist/image/20251223194320_84BD818B-F3F0-4097-9DCC-813BC54D14AE.jpeg", imageSourceUrl: "https://www.change2561.com/changeartist" },
  { id: "sonya", name: "Saranphat Pedersen", stageName: "Sonya", initials: "SS", colors: ["#843e52", "#df8c89"], imageUrl: "https://www.change2561.com/assets/uploads/img/Artist/image/20251223184747_B50D049D-5ED1-478C-A46A-9BB754D16AAF.jpeg", imageSourceUrl: "https://www.change2561.com/changeartist" },
];

const actingPairs = [
  { id: "freenbecky", name: "FreenBecky", actressIds: ["freen", "becky"], initials: "FB", colors: ["#662450", "#db6b9b"], imageUrl: null, imageSourceUrl: null },
  { id: "namtanfilm", name: "NamtanFilm", actressIds: ["namtan", "film"], initials: "NF", colors: ["#172e5c", "#7d58a5"], imageUrl: null, imageSourceUrl: null },
  { id: "milklove", name: "MilkLove", actressIds: ["milk", "love"], initials: "ML", colors: ["#be5f4b", "#efaa79"], imageUrl: null, imageSourceUrl: null },
  { id: "lingorm", name: "LingOrm", actressIds: ["lingling", "orm"], initials: "LO", colors: ["#285052", "#8cb797"], imageUrl: null, imageSourceUrl: null },
  { id: "lmsy", name: "LMSY", actressIds: ["lookmhee", "sonya"], initials: "LS", colors: ["#682936", "#bf6a6f"], imageUrl: null, imageSourceUrl: null },
];

const seriesPairings = [
  { id: "sam-mon", seriesId: "gap", pairId: "freenbecky", characters: ["Sam", "Mon"], role: "main" },
  { id: "anin-pin", seriesId: "loyal-pin", pairId: "freenbecky", characters: ["Anin", "Pin"], role: "main" },
  { id: "ai-oon-may", seriesId: "pluto", pairId: "namtanfilm", characters: ["Ai-oon", "May"], role: "main" },
  { id: "ongsa-sun", seriesId: "23-5", pairId: "milklove", characters: ["Ongsa", "Sun"], role: "main" },
  { id: "lada-earn", seriesId: "secret-of-us", pairId: "lingorm", characters: ["Lada", "Earn"], role: "main" },
  { id: "wan-pleng", seriesId: "affair", pairId: "lmsy", characters: ["Wan", "Pleng"], role: "main" },
];

const series = [
  { id: "gap", title: "GAP: The Series", year: 2022, releaseDate: "2022-11-19", releaseDateSourceUrl: "https://en.wikipedia.org/wiki/Gap_(TV_series)", country: "Tailandia", ending: "happy", drama: 2, chemistry: 9.6, popularity: 100, provider: "YouTube", initials: "GM", colors: ["#62224f", "#da6296"], coverImageUrl: "https://upload.wikimedia.org/wikipedia/en/a/a1/Gaptheseriesposter.png", coverImageSourceUrl: "https://en.wikipedia.org/wiki/Gap_(TV_series)", synopsis: "Mon empieza a trabajar en la empresa de Sam, a quien admira desde joven. La distancia entre sus mundos se convierte poco a poco en una historia de amor.", cast: [{ actressId: "freen", character: "Sam", importance: "lead" }, { actressId: "becky", character: "Mon", importance: "lead" }] },
  { id: "loyal-pin", title: "The Loyal Pin", year: 2024, releaseDate: "2024-08-04", releaseDateSourceUrl: "https://en.wikipedia.org/wiki/The_Loyal_Pin", country: "Tailandia", ending: "happy", drama: 3, chemistry: 9.5, popularity: 94, provider: "YouTube", initials: "AP", colors: ["#774626", "#d7a75a"], coverImageUrl: "https://upload.wikimedia.org/wikipedia/en/4/44/TheLoyalPin.jpg", coverImageSourceUrl: "https://en.wikipedia.org/wiki/The_Loyal_Pin", synopsis: "Una historia de época sobre dos jóvenes unidas desde la infancia que deben proteger un amor enfrentado a las expectativas de palacio.", cast: [{ actressId: "freen", character: "Anin", importance: "lead" }, { actressId: "becky", character: "Pin", importance: "lead" }] },
  { id: "pluto", title: "Pluto", year: 2024, releaseDate: "2024-10-19", releaseDateSourceUrl: "https://en.wikipedia.org/wiki/Pluto_(Thai_TV_series)", country: "Tailandia", ending: "happy", drama: 4, chemistry: 9.4, popularity: 97, provider: "YouTube", initials: "AM", colors: ["#152950", "#7954a6"], coverImageUrl: "https://upload.wikimedia.org/wikipedia/en/d/d7/Pluto_2024_Official_Poster.png", coverImageSourceUrl: "https://en.wikipedia.org/wiki/Pluto_(Thai_TV_series)", synopsis: "Una identidad prestada y un vínculo inesperado abren un misterio romántico donde cada verdad cambia lo que creemos saber de la pareja.", cast: [{ actressId: "namtan", character: "Ai-oon", importance: "lead" }, { actressId: "film", character: "May", importance: "lead" }] },
  { id: "23-5", title: "23.5", year: 2024, releaseDate: "2024-03-08", releaseDateSourceUrl: "https://en.wikipedia.org/wiki/23.5", country: "Tailandia", ending: "happy", drama: 1, chemistry: 8.9, popularity: 88, provider: "Netflix", initials: "OS", colors: ["#db744f", "#f5b766"], coverImageUrl: "https://upload.wikimedia.org/wikipedia/en/9/96/23.5_Official_Poster_%282024%29.jpg", coverImageSourceUrl: "https://en.wikipedia.org/wiki/23.5", synopsis: "Ongsa, tímida y enamorada, conoce online a la popular Sun bajo un nombre que oculta quién es. Una comedia romántica luminosa y juvenil.", cast: [{ actressId: "milk", character: "Ongsa", importance: "lead" }, { actressId: "love", character: "Sun", importance: "lead" }, { actressId: "ciize", character: "Alpha", importance: "supporting" }] },
  { id: "secret-of-us", title: "The Secret of Us", year: 2024, releaseDate: "2024-06-24", releaseDateSourceUrl: "https://en.wikipedia.org/wiki/The_Secret_of_Us_(TV_series)", country: "Tailandia", ending: "happy", drama: 4, chemistry: 9.3, popularity: 96, provider: "Ch3+", initials: "LE", colors: ["#315a5b", "#8bb596"], coverImageUrl: "https://upload.wikimedia.org/wikipedia/en/9/9a/The_Secret_of_Us_poster_%282024%29.jpeg", coverImageSourceUrl: "https://en.wikipedia.org/wiki/The_Secret_of_Us_(TV_series)", synopsis: "Dos antiguas amantes vuelven a encontrarse cuando sus vidas profesionales se cruzan, obligándolas a mirar de frente una ruptura nunca resuelta.", cast: [{ actressId: "lingling", character: "Lada", importance: "lead" }, { actressId: "orm", character: "Earn", importance: "lead" }] },
  { id: "affair", title: "Affair", year: 2024, releaseDate: "2024-08-30", releaseDateSourceUrl: "https://en.wikipedia.org/wiki/Affair_(Thai_Drama)", country: "Tailandia", ending: "happy", drama: 5, chemistry: 9.2, popularity: 90, provider: "iQIYI", initials: "WP", colors: ["#682936", "#bf6a6f"], coverImageUrl: "https://upload.wikimedia.org/wikipedia/en/8/88/Affair_2024_Official_Poster.jpg", coverImageSourceUrl: "https://en.wikipedia.org/wiki/Affair_(Thai_Drama)", synopsis: "La amistad inseparable entre Wan y Pleng se transforma en algo más profundo mientras el tiempo, la familia y sus decisiones ponen a prueba el vínculo.", cast: [{ actressId: "lookmhee", character: "Wan", importance: "lead" }, { actressId: "sonya", character: "Pleng", importance: "lead" }] },
];

const providers = [
  { name: "Todas", short: "GL", color: "#6f285f" },
  { name: "YouTube", short: "YT", color: "#e74355" },
  { name: "Netflix", short: "N", color: "#18151b" },
  { name: "Ch3+", short: "3+", color: "#3265a8" },
  { name: "iQIYI", short: "iQI", color: "#79b928" },
];

const importanceLabels = { lead: "Protagonista", supporting: "Secundaria", guest: "Invitada" };
const roleLabels = { main: "Pareja principal", supporting: "Pareja secundaria" };
const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
const state = { search: "", provider: "Todas", drama: 5, endings: [], pairings: [], country: "", releaseMonth: "", releaseYear: "", comfort: false, sort: "popular", saved: new Set(), detailTrail: [] };
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
const releaseParts = (item) => item.releaseDate.split("-");

function formatReleaseDate(releaseDate) {
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
  return pairingsForSeries(item.id).map((seriesPairing) => {
    const pair = byId(actingPairs, seriesPairing.pairId);
    return `${seriesPairing.characters.join(" · ")} · ${pair.name}`;
  }).join(" · ");
}

function renderProviders() {
  document.querySelector("#provider-list").innerHTML = providers.map((provider) => `
    <button class="provider-pill ${state.provider === provider.name ? "active" : ""}" type="button" data-provider="${provider.name}">
      <span class="provider-icon" style="background:${provider.color}">${provider.short}</span>
      <span>${provider.name}<small>${provider.name === "Todas" ? "Todo el catálogo" : "Ver disponibles"}</small></span>
    </button>`).join("");
}

function renderReleaseFilters() {
  const months = [...new Set(series.map((item) => Number(releaseParts(item)[1])))].sort((a, b) => a - b);
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
      && (state.provider === "Todas" || item.provider === state.provider)
      && item.drama <= state.drama
      && (!state.endings.length || state.endings.includes(item.ending))
      && (!state.pairings.length || state.pairings.some((role) => roles.includes(role)))
      && (!state.country || item.country === state.country)
      && (!state.releaseMonth || releaseMonth === state.releaseMonth.padStart(2, "0"))
      && (!state.releaseYear || releaseYear === state.releaseYear)
      && (!state.comfort || (item.ending === "happy" && item.drama <= 2));
  }).sort((a, b) => {
    if (state.sort === "score") return b.chemistry - a.chemistry;
    if (state.sort === "newest") return b.releaseDate.localeCompare(a.releaseDate);
    if (state.sort === "drama") return a.drama - b.drama;
    return b.popularity - a.popularity;
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
      <div class="card-info"><h3>${item.title}</h3><span class="card-meta">${formatReleaseDate(item.releaseDate)} · ${item.provider} · Drama ${item.drama}/5</span><div class="pair-row"><span class="pair-name">♡ ${pairingSummary(item)}</span><span class="badges"><span class="badge happy">☺ FELIZ</span><span class="badge drama">✦ ${item.chemistry}</span></span></div></div>
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
  if (state.provider !== "Todas") chips.push([state.provider, "provider"]);
  if (state.drama < 5) chips.push([`Drama ≤ ${state.drama}`, "drama"]);
  if (state.comfort) chips.push(["Modo confort", "comfort"]);
  state.endings.forEach((value) => chips.push([value === "happy" ? "Final feliz" : `Final ${value}`, `ending:${value}`]));
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
  return `${detailHeader("Ficha de serie")}
    <div class="detail-layout series-layout">
      <aside>${mediaMarkup(item, "cover", `Portada de ${item.title}`)}</aside>
      <div class="detail-main"><p class="eyebrow">${item.country.toUpperCase()} · ${formatReleaseDate(item.releaseDate).toUpperCase()}</p><h2>${item.title}</h2><p class="detail-lead">${item.synopsis}</p><a class="release-source" href="${item.releaseDateSourceUrl}" target="_blank" rel="noreferrer">Fuente de la fecha de estreno ↗</a>
        <div class="score-strip"><span><small>QUÍMICA</small><strong>✦ ${item.chemistry}</strong></span><span><small>DRAMA</small><strong>${item.drama}/5</strong></span><span><small>FINAL</small><strong>☺ Feliz</strong></span><span><small>DÓNDE VER</small><strong>${item.provider}</strong></span></div>
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
  Object.assign(state, { search: "", provider: "Todas", drama: 5, endings: [], pairings: [], country: "", releaseMonth: "", releaseYear: "", comfort: false, sort: "popular" });
  document.querySelector("#search-input").value = "";
  document.querySelector("#drama-filter").value = 5;
  document.querySelector("#drama-value").textContent = 5;
  document.querySelector("#country-filter").value = "";
  document.querySelector("#release-month-filter").value = "";
  document.querySelector("#release-year-filter").value = "";
  document.querySelector("#sort-select").value = "popular";
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
  if (event.target.closest("[data-open-featured]")) showDetail("series", "gap");
  if (event.target.closest("[data-detail-back]")) { const previous = state.detailTrail.pop(); if (previous) showDetail(previous[0], previous[1], false); }
  if (event.target.closest("[data-quick-filter=comfort]")) { state.comfort = true; document.querySelector("#comfort-toggle").setAttribute("aria-checked", "true"); renderCards(); document.querySelector("#popular").scrollIntoView(); }
  if (event.target.closest("[data-reset]")) resetFilters();
  const remove = event.target.closest("[data-remove-filter]");
  if (remove) { const [type, value] = remove.dataset.removeFilter.split(":"); if (type === "search") { state.search = ""; document.querySelector("#search-input").value = ""; } if (type === "provider") { state.provider = "Todas"; renderProviders(); } if (type === "drama") { state.drama = 5; document.querySelector("#drama-filter").value = 5; document.querySelector("#drama-value").textContent = 5; } if (type === "comfort") { state.comfort = false; document.querySelector("#comfort-toggle").setAttribute("aria-checked", "false"); } if (type === "ending") state.endings = state.endings.filter((ending) => ending !== value); if (type === "pairing") state.pairings = state.pairings.filter((role) => role !== value); if (type === "country") { state.country = ""; document.querySelector("#country-filter").value = ""; } if (type === "releaseMonth") { state.releaseMonth = ""; document.querySelector("#release-month-filter").value = ""; } if (type === "releaseYear") { state.releaseYear = ""; document.querySelector("#release-year-filter").value = ""; } renderCards(); }
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

renderProviders();
renderReleaseFilters();
renderCards();
renderUniverse();
