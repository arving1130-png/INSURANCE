// ── State ───────────────────────────────────────────
const conversationHistory = [];

// ── DOM refs ────────────────────────────────────────
const chatMessages   = document.getElementById("chatMessages");
const chatForm       = document.getElementById("chatForm");
const userInput      = document.getElementById("userInput");
const sendBtn        = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");

// ── Helpers ─────────────────────────────────────────
function formatTime(date = new Date()) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

// Set welcome message timestamp
const welcomeTimeEl = document.getElementById("welcomeTime");
if (welcomeTimeEl) welcomeTimeEl.textContent = formatTime();

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Convert simple markdown-ish formatting to HTML
function renderMarkdown(text) {
  // Escape HTML first
  let html = escapeHtml(text);

  // Bold: **text** or __text__
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__(.+?)__/g, "<strong>$1</strong>");

  // Italic: *text* or _text_
  html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, "<em>$1</em>");

  // Bullet lists
  const lines = html.split("\n");
  const processed = [];
  let inList = false;

  for (const line of lines) {
    const bulletMatch = line.match(/^[-*•]\s+(.+)/);
    if (bulletMatch) {
      if (!inList) { processed.push("<ul>"); inList = true; }
      processed.push(`<li>${bulletMatch[1]}</li>`);
    } else {
      if (inList) { processed.push("</ul>"); inList = false; }
      if (line.trim() === "") {
        processed.push("<br/>");
      } else {
        processed.push(`<p>${line}</p>`);
      }
    }
  }
  if (inList) processed.push("</ul>");

  return processed.join("");
}

// ── Append message ───────────────────────────────────
function appendMessage(role, text, isError = false) {
  const wrapper = document.createElement("div");
  wrapper.className = `message message-${role === "user" ? "user" : "bot"}${isError ? " message-error" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "U" : "A";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  if (role === "user") {
    bubble.innerHTML = `<p>${escapeHtml(text)}</p>`;
  } else {
    bubble.innerHTML = renderMarkdown(text);
  }

  const timeEl = document.createElement("div");
  timeEl.className = "message-time";
  timeEl.textContent = formatTime();

  if (role === "user") {
    wrapper.appendChild(timeEl);
    wrapper.appendChild(bubble);
    wrapper.appendChild(avatar);
  } else {
    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    wrapper.appendChild(timeEl);
  }

  chatMessages.appendChild(wrapper);
  scrollToBottom();
}

// ── Send message ─────────────────────────────────────
async function sendMessage(text) {
  const trimmed = text.trim();
  if (!trimmed) return;

  // Show user message
  appendMessage("user", trimmed);
  conversationHistory.push({ role: "user", content: trimmed });

  // Disable input while waiting
  userInput.value = "";
  userInput.style.height = "auto";
  userInput.disabled = true;
  sendBtn.disabled = true;
  typingIndicator.classList.add("visible");
  scrollToBottom();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: conversationHistory }),
    });

    const data = await response.json();

    typingIndicator.classList.remove("visible");

    if (!response.ok || data.error) {
      const errMsg = data.error || "Something went wrong. Please try again.";
      appendMessage("assistant", errMsg, true);
    } else {
      appendMessage("assistant", data.reply);
      conversationHistory.push({ role: "assistant", content: data.reply });
    }
  } catch (err) {
    typingIndicator.classList.remove("visible");
    appendMessage("assistant", "Connection error. Please check your connection and try again.", true);
    // Remove failed user message from history so conversation stays valid
    conversationHistory.pop();
  } finally {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}

// ── Form submit ──────────────────────────────────────
chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(userInput.value);
});

// ── Enter key handling ────────────────────────────────
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage(userInput.value);
  }
});

// ── Auto-resize textarea ──────────────────────────────
userInput.addEventListener("input", () => {
  userInput.style.height = "auto";
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
});

// ── Quick-topic buttons ───────────────────────────────
document.querySelectorAll(".quick-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const msg = btn.dataset.msg;
    if (msg) sendMessage(msg);
  });
});

// ── Initial focus ─────────────────────────────────────
userInput.focus();
