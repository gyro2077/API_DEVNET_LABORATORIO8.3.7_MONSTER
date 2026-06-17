const POLL_INTERVAL_MS = 2000;

const loginScreen = document.getElementById("login-screen");
const appScreen = document.getElementById("app-screen");
const loginError = document.getElementById("login-error");
const messagesEl = document.getElementById("messages");
const roomTitleEl = document.getElementById("room-title");
const userLabelEl = document.getElementById("user-label");
const statusEl = document.getElementById("connection-status");
const lastUpdateEl = document.getElementById("last-update");
const sendForm = document.getElementById("send-form");
const messageInput = document.getElementById("message-input");
const inviteForm = document.getElementById("invite-form");
const inviteEmail = document.getElementById("invite-email");
const inviteFeedback = document.getElementById("invite-feedback");
const membersList = document.getElementById("members-list");

const knownMessageIds = new Set();
let pollTimer = null;
let currentUser = null;

function showLogin(errorMessage = "") {
    loginScreen.classList.remove("hidden");
    appScreen.classList.add("hidden");
    if (errorMessage) {
        loginError.textContent = errorMessage;
        loginError.classList.remove("hidden");
    }
}

function showApp() {
    loginScreen.classList.add("hidden");
    appScreen.classList.remove("hidden");
}

function setStatus(text, type = "online") {
    statusEl.textContent = text;
    statusEl.className = `badge ${type}`;
}

function formatTime(isoString) {
    if (!isoString) return "";
    return new Date(isoString).toLocaleTimeString("es-EC", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}

function renderMessage(message) {
    if (knownMessageIds.has(message.id)) {
        return;
    }

    knownMessageIds.add(message.id);

    const item = document.createElement("div");
    item.className = "message";
    if (currentUser && message.personEmail === currentUser.email) {
        item.classList.add("mine");
    }

    const author = message.personEmail || message.personDisplayName || "Desconocido";
    const text = message.text || message.markdown || "";

    item.innerHTML = `
        <div class="meta">
            <strong>${author}</strong>
            <span>${formatTime(message.created)}</span>
        </div>
        <div class="text"></div>
    `;

    item.querySelector(".text").textContent = text;
    messagesEl.appendChild(item);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));
    if (response.status === 401) {
        showLogin("Tu sesión expiró. Vuelve a iniciar sesión con Webex.");
        throw new Error("No autenticado");
    }
    if (!response.ok) {
        throw new Error(data.error || `Error HTTP ${response.status}`);
    }
    return data;
}

async function loadAuth() {
    const response = await fetch("/api/auth/me");
    if (response.status === 401) {
        showLogin();
        return false;
    }

    currentUser = await response.json();
    userLabelEl.textContent = `Conectado como ${currentUser.displayName || currentUser.email}`;
    showApp();
    return true;
}

async function loadRoom() {
    const room = await fetchJson("/api/room");
    roomTitleEl.textContent = room.title || "Sala Webex";
}

async function loadMessages() {
    const data = await fetchJson("/api/messages");
    data.items.forEach(renderMessage);
    lastUpdateEl.textContent = `Última actualización: ${new Date().toLocaleTimeString("es-EC")}`;
    setStatus("En vivo", "online");
}

async function loadMembers() {
    const data = await fetchJson("/api/members");
    membersList.innerHTML = "";

    if (!data.items.length) {
        membersList.innerHTML = "<li>No hay participantes.</li>";
        return;
    }

    data.items.forEach((member) => {
        const item = document.createElement("li");
        const name = member.personDisplayName || member.personEmail || "Participante";
        item.textContent = name;
        membersList.appendChild(item);
    });
}

async function refreshAll() {
    try {
        await Promise.all([loadMessages(), loadMembers()]);
    } catch (error) {
        if (error.message !== "No autenticado") {
            setStatus("Error de conexión", "error");
            lastUpdateEl.textContent = error.message;
        }
    }
}

sendForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = messageInput.value.trim();
    if (!text) return;

    try {
        await fetchJson("/api/messages", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        messageInput.value = "";
        await loadMessages();
    } catch (error) {
        if (error.message !== "No autenticado") {
            alert(error.message);
        }
    }
});

inviteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = inviteEmail.value.trim();
    if (!email) return;

    inviteFeedback.textContent = "Invitando...";
    inviteFeedback.className = "feedback";

    try {
        const result = await fetchJson("/api/members", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email }),
        });
        inviteFeedback.textContent = result.message || "Compañero invitado correctamente.";
        inviteFeedback.className = "feedback success";
        inviteEmail.value = "";
        await loadMembers();
    } catch (error) {
        if (error.message !== "No autenticado") {
            inviteFeedback.textContent = error.message;
            inviteFeedback.className = "feedback error";
        }
    }
});

function readLoginErrorFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const error = params.get("error");
    if (!error) return "";
    if (error === "access_denied") return "Cancelaste el inicio de sesión.";
    if (error === "invalid_scope") {
        return "Scopes OAuth no coinciden. En developer.webex.com/my-apps marca 'spark:all' en tu Integration y usa OAUTH_SCOPES = 'spark:all' en config_local.py.";
    }
    return `Error de login: ${error}`;
}

async function init() {
    const urlError = readLoginErrorFromUrl();
    if (urlError) {
        window.history.replaceState({}, "", "/");
    }

    const authenticated = await loadAuth();
    if (!authenticated) {
        showLogin(urlError);
        return;
    }

    try {
        await loadRoom();
        await refreshAll();
        pollTimer = setInterval(refreshAll, POLL_INTERVAL_MS);
    } catch (error) {
        setStatus("Error de conexión", "error");
        roomTitleEl.textContent = error.message;
    }
}

init();
