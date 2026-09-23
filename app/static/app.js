// DemoBank AI SDLC — client-side JS

// --- Split.io Feature Flag: ai_chat_enabled ---
var splitFactory = splitio({
  core: {
    authorizationKey: "cl0bl351743733kglfasq85pr2kq8ul9rmqv",
    key: "demobank-web",
  },
});
var splitClient = splitFactory.client();

function evaluateChatFlag() {
  var treatment = splitClient.getTreatment("ai_chat_enabled");
  var btn = document.getElementById("ai-chat-btn");
  var panel = document.getElementById("ai-chat-panel");
  if (treatment === "on") {
    if (btn) btn.style.display = "";
  } else {
    if (btn) btn.style.display = "none";
    if (panel) panel.style.display = "none";
  }
}

splitClient.on(splitClient.Event.SDK_READY, evaluateChatFlag);
splitClient.on(splitClient.Event.SDK_UPDATE, evaluateChatFlag);

// --- Chat Widget ---
var chatOpen = false;

function toggleChatPanel() {
  chatOpen = !chatOpen;
  var panel = document.getElementById("ai-chat-panel");
  if (!panel) return;
  panel.style.display = chatOpen ? "flex" : "none";
  if (chatOpen) {
    var msgs = document.getElementById("chat-messages");
    if (msgs && msgs.children.length === 0) {
      appendChatMessage(
        "ai",
        "Hello! I'm your AI banking assistant. Ask me about your accounts, transactions, or exchange rates."
      );
    }
    document.getElementById("chat-input").focus();
  }
}

function appendChatMessage(role, text) {
  var msgs = document.getElementById("chat-messages");
  var div = document.createElement("div");
  div.className = "chat-msg " + role;
  div.textContent = text;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function sendChatMessage() {
  var input = document.getElementById("chat-input");
  var text = input.value.trim();
  if (!text) return;
  input.value = "";
  appendChatMessage("user", text);
  appendChatMessage("ai", "Thinking...");

  fetch("/api/ai/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text, session_id: "web-client" }),
  })
    .then(function (res) {
      return res.json();
    })
    .then(function (data) {
      var msgs = document.getElementById("chat-messages");
      msgs.removeChild(msgs.lastChild);
      appendChatMessage("ai", data.response || data.error || "No response");
    })
    .catch(function () {
      var msgs = document.getElementById("chat-messages");
      msgs.removeChild(msgs.lastChild);
      appendChatMessage("ai", "Sorry, something went wrong. Please try again.");
    });
}

// --- Transfer form ---
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("transfer-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const data = {
      fromAccount: form.fromAccount.value,
      toAccount: form.toAccount.value,
      amount: form.amount.value,
      memo: form.memo.value,
    };

    fetch("/api/transfers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((result) => {
        const resultDiv = document.getElementById("transfer-result");
        if (result.success) {
          // DEMO UX BUG: shows success even for invalid (negative/zero) amounts
          resultDiv.innerHTML =
            '<div class="alert alert-success" style="font-size:18px;font-weight:800;padding:24px;">✅ Transfer completed successfully!<br>Amount transferred: <strong>$' +
            result.amount +
            '</strong><br><span style="font-size:12px;color:#276749;">Transaction ID: ' +
            result.transferId +
            "</span></div>";
        } else {
          resultDiv.innerHTML =
            '<div class="alert alert-error">Error: ' + result.error + "</div>";
        }
      })
      .catch(() => {
        document.getElementById("transfer-result").innerHTML =
          '<div class="alert alert-error">Transfer request failed.</div>';
      });
  });
});
