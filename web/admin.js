let csrfToken = "";
let currentUser = null;
let series = [];
let selected = null;
const sessionStorageKey = "glv_session";

const loginPanel = document.querySelector("#login-panel");
const backoffice = document.querySelector("#backoffice");
const form = document.querySelector("#series-form");
const nullableFields = new Set(["originalTitle", "releaseDate", "synopsis", "coverImageUrl", "coverImageSourceUrl", "dramaLevel", "endingType", "endingNote"]);
const editableFields = ["title", "originalTitle", "country", "releaseYear", "releaseDate", "status", "synopsis", "coverImageUrl", "coverImageSourceUrl", "dramaLevel", "endingType", "endingNote"];

async function api(url, options = {}) {
  const sessionToken = window.sessionStorage.getItem(sessionStorageKey);
  const response = await fetch(url, { credentials: "same-origin", ...options, headers: { "Content-Type": "application/json", ...(sessionToken ? { Authorization: `Bearer ${sessionToken}` } : {}), ...(csrfToken ? { "X-GL-Verse-CSRF": csrfToken } : {}), ...(options.headers || {}) } });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
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
  return api("/api/auth/google", {
    method: "POST",
    body: JSON.stringify({ credential, loginCsrf: config.loginCsrf }),
  });
}

async function setupGoogleLogin() {
  const config = await api("/api/auth/google/start?next=/admin");
  await loadGoogleLibrary();
  window.google.accounts.id.initialize({
    client_id: config.clientId,
    nonce: config.nonce,
    callback: async ({ credential }) => {
      document.querySelector("#login-message").textContent = "Validando la cuenta con Google…";
      try {
        const result = await finishGoogleLogin(credential, config);
        window.sessionStorage.setItem(sessionStorageKey, result.sessionToken);
        window.location.replace(result.nextPath);
      } catch (error) {
        document.querySelector("#login-message").textContent = error.message;
      }
    },
  });
  window.google.accounts.id.renderButton(document.querySelector("#google-login"), {
    theme: "outline",
    size: "large",
    text: "continue_with",
  });
}

async function restoreSession() {
  try {
    const session = await api("/api/auth/session");
    if (!session.authenticated) {
      loginPanel.hidden = false; backoffice.hidden = true;
      if (!session.googleConfigured) {
        document.querySelector("#google-login").hidden = true;
        document.querySelector("#login-message").textContent = "Configura las credenciales de Google para habilitar el acceso.";
      }
      else await setupGoogleLogin();
      return;
    }
    if (session.user.role !== "admin") {
      loginPanel.hidden = false; backoffice.hidden = true;
      document.querySelector("#google-login").hidden = true;
      document.querySelector("#viewer-logout").hidden = false;
      document.querySelector("#login-message").textContent = `${session.user.email} tiene rol viewer y no puede acceder al backoffice.`;
      csrfToken = session.csrfToken;
      return;
    }
    activateSession(session);
    await loadSeries();
  } catch (error) {
    loginPanel.hidden = false;
    backoffice.hidden = true;
    document.querySelector("#login-message").textContent = error.message;
  }
}

function activateSession(session) {
  currentUser = session.user;
  csrfToken = session.csrfToken;
  document.querySelector("#session-user").textContent = currentUser.name || currentUser.email;
  const avatar = document.querySelector("#session-avatar");
  if (currentUser.pictureUrl) { avatar.src = currentUser.pictureUrl; avatar.hidden = false; }
  loginPanel.hidden = true;
  backoffice.hidden = false;
}

async function loadSeries() {
  const payload = await api("/api/admin/series");
  series = payload.series;
  renderSeries();
}

function renderSeries() {
  const term = document.querySelector("#admin-search").value.trim().toLocaleLowerCase("es");
  const list = document.querySelector("#admin-series-list");
  list.replaceChildren();
  series.filter((item) => !term || `${item.title} ${item.id}`.toLocaleLowerCase("es").includes(term)).forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = selected?.id === item.id ? "active" : "";
    const title = document.createElement("span"); title.textContent = item.title;
    const status = document.createElement("small"); status.textContent = item.reviewStatus === "approved" ? "✓ Revisada" : "Pendiente";
    button.append(title, status);
    button.addEventListener("click", () => selectSeries(item.id));
    list.append(button);
  });
}

function selectSeries(id) {
  selected = series.find((item) => item.id === id);
  document.querySelector("#editor-empty").hidden = true;
  form.hidden = false;
  document.querySelector("#editor-title").textContent = selected.title;
  document.querySelector("#editor-id").textContent = selected.id;
  editableFields.forEach((field) => { form.elements[field].value = selected[field] ?? ""; });
  updateReviewUI(); renderSeries();
  document.querySelector("#editor-message").textContent = "";
}

function updateReviewUI() {
  const approved = selected.reviewStatus === "approved";
  const pill = document.querySelector("#review-status");
  pill.textContent = approved ? "✓ Ficha aprobada" : "Pendiente de revisar";
  pill.className = `status-pill ${approved ? "approved" : ""}`;
  const button = document.querySelector("#review-button");
  button.textContent = approved ? "Reabrir revisión" : "Aprobar ficha";
  button.dataset.status = approved ? "pending" : "approved";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.submitter; button.disabled = true;
  const message = document.querySelector("#editor-message"); message.textContent = "";
  try {
    const data = new FormData(form); const fields = {};
    editableFields.forEach((field) => {
      let value = data.get(field);
      if (field === "releaseYear") value = Number(value);
      else if (nullableFields.has(field) && value === "") value = null;
      if (value !== selected[field]) fields[field] = value;
    });
    const source = { title: data.get("sourceTitle"), url: data.get("sourceUrl"), sourceType: data.get("sourceType"), verificationStatus: data.get("verificationStatus"), publisher: data.get("publisher") };
    const updated = await api(`/api/admin/series/${encodeURIComponent(selected.id)}`, { method: "PUT", body: JSON.stringify({ fields, source }) });
    series = series.map((item) => item.id === updated.id ? updated : item); selected = updated;
    selectSeries(updated.id); message.textContent = "Cambios guardados; la ficha vuelve a estar pendiente.";
  } catch (error) { message.textContent = error.message; } finally { button.disabled = false; }
});

document.querySelector("#review-button").addEventListener("click", async (event) => {
  event.currentTarget.disabled = true;
  const message = document.querySelector("#editor-message"); message.textContent = "";
  try {
    const review = await api(`/api/admin/series/${encodeURIComponent(selected.id)}/review-status`, { method: "PUT", body: JSON.stringify({ status: event.currentTarget.dataset.status }) });
    selected.reviewStatus = review.status; selected.reviewedAt = review.reviewedAt;
    series = series.map((item) => item.id === selected.id ? selected : item); updateReviewUI(); renderSeries();
  } catch (error) { message.textContent = error.message; } finally { event.currentTarget.disabled = false; }
});

document.querySelector("#logout-button").addEventListener("click", async () => {
  try { await api("/api/auth/logout", { method: "POST", body: "{}" }); } finally { window.sessionStorage.removeItem(sessionStorageKey); csrfToken = ""; currentUser = null; series = []; selected = null; window.location.assign("/"); }
});
document.querySelector("#viewer-logout").addEventListener("click", async () => {
  try { await api("/api/auth/logout", { method: "POST", body: "{}" }); } finally { window.sessionStorage.removeItem(sessionStorageKey); window.location.assign("/"); }
});
document.querySelector("#admin-search").addEventListener("input", renderSeries);
restoreSession();
