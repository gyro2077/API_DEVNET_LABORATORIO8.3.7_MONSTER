const POLL_INTERVAL_MS = 2000;

const messagesEl = document.getElementById("messages");
const roomTitleEl = document.getElementById("room-title");
const statusEl = document.getElementById("connection-status");
const lastUpdateEl = document.getElementById("last-update");
const sendForm = document.getElementById("send-form");
const messageInput = document.getElementById("message-input");
const inviteForm = document.getElementById("invite-form");
const inviteEmail = document.getElementById("invite-email");
const inviteFeedback = document.getElementById("invite-feedback");
const membersList = document.getElementById("members-list");

const knownMessageIds = new Set();

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
    item.dataset.id = message.id;

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
    if (!response.ok) {
        throw new Error(data.error || `Error HTTP ${response.status}`);
    }
    return data;
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
        setStatus("Error de conexión", "error");
        lastUpdateEl.textContent = error.message;
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
        alert(error.message);
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
        inviteFeedback.textContent = error.message;
        inviteFeedback.className = "feedback error";
    }
});

async function init() {
    try {
        await loadRoom();
        await refreshAll();
        setInterval(refreshAll, POLL_INTERVAL_MS);
    } catch (error) {
        setStatus("Error de conexión", "error");
        roomTitleEl.textContent = error.message;
    }
}

init();
