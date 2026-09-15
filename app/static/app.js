// DemoBank AI SDLC — client-side JS

var chatOpen = false;

function toggleChat() {
  chatOpen = !chatOpen;
  var panel = document.getElementById("chat-panel");
  if (chatOpen) {
    panel.classList.remove("chat-hidden");
    var msgs = document.getElementById("chat-messages");
    if (msgs.children.length === 0) {
      appendMessage("ai", "Hello! I'm your AI banking assistant.\nAsk me about your accounts, transactions, or exchange rates.");
    }
    document.getElementById("chat-input").focus();
  } else {
    panel.classList.add("chat-hidden");
  }
}

function appendMessage(role, text) {
  var msgs = document.getElementById("chat-messages");
  var bubble = document.createElement("div");
  bubble.className = "chat-bubble " + role;
  bubble.textContent = text;
  msgs.appendChild(bubble);
  msgs.scrollTop = msgs.scrollHeight;
  return bubble;
}

function sendChat() {
  var input = document.getElementById("chat-input");
  var message = input.value.trim();
  if (!message) return;

  input.value = "";
  appendMessage("user", message);

  var sendBtn = document.getElementById("chat-send");
  sendBtn.disabled = true;
  var typing = appendMessage("typing", "Thinking...");

  fetch("/api/ai/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message, session_id: "web-client" }),
  })
    .then(function (res) { return res.json(); })
    .then(function (data) {
      typing.remove();
      if (data.error) {
        appendMessage("ai", "Sorry, I encountered an error: " + data.error);
      } else {
        appendMessage("ai", data.response);
      }
    })
    .catch(function () {
      typing.remove();
      appendMessage("ai", "Sorry, I couldn't connect to the AI service. Please try again.");
    })
    .finally(function () {
      sendBtn.disabled = false;
      document.getElementById("chat-input").focus();
    });
}

// Split JS SDK — feature flag for chat widget visibility
(function initSplitFF() {
  if (typeof splitio === "undefined") return;
  var factory = splitio({
    core: {
      authorizationKey: "cl0bl351743733kglfasq85pr2kq8ul9rmqv",
      key: "demobank-web",
    },
  });
  var client = factory.client();

  function evalFlag() {
    var treatment = client.getTreatment("ai_chat_enabled");
    var toggle = document.getElementById("chat-toggle");
    var panel = document.getElementById("chat-panel");
    if (treatment === "on") {
      toggle.style.display = "";
    } else {
      toggle.style.display = "none";
      panel.classList.add("chat-hidden");
      chatOpen = false;
    }
  }

  client.on(client.Event.SDK_READY, evalFlag);
  client.on(client.Event.SDK_UPDATE, evalFlag);
})();

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
