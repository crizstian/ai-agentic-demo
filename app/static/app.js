// DemoBank AI SDLC — client-side JS

document.addEventListener("DOMContentLoaded", function () {
  // --- AI Chat Widget ---
  const chatToggle = document.getElementById("chat-toggle");
  const chatPanel = document.getElementById("chat-panel");
  const chatClose = document.getElementById("chat-close");
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const chatSend = document.getElementById("chat-send");

  if (chatToggle && chatPanel) {
    const WELCOME_MSG =
      "Hello! I'm your AI banking assistant. Ask me about your accounts, transactions, or exchange rates.";
    var chatEnabled = false;

    chatToggle.style.display = "none";

    function applyTreatment(treatment) {
      chatEnabled = treatment === "on";
      chatToggle.style.display = chatEnabled ? "" : "none";
      if (!chatEnabled && !chatPanel.classList.contains("chat-hidden")) {
        chatPanel.classList.add("chat-hidden");
      }
    }

    if (typeof splitio !== "undefined") {
      var factory = splitio({
        core: {
          authorizationKey: "cl0bl351743733kglfasq85pr2kq8ul9rmqv",
          key: "demobank-web"
        }
      });
      var splitClient = factory.client();

      splitClient.on(splitClient.Event.SDK_READY, function () {
        applyTreatment(splitClient.getTreatment("ai_chat_enabled"));
      });

      splitClient.on(splitClient.Event.SDK_UPDATE, function () {
        applyTreatment(splitClient.getTreatment("ai_chat_enabled"));
      });
    }

    function addBubble(text, cls) {
      const div = document.createElement("div");
      div.className = "chat-bubble " + cls;
      div.textContent = text;
      chatMessages.appendChild(div);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      return div;
    }

    function openChat() {
      chatPanel.classList.remove("chat-hidden");
      if (!chatMessages.hasChildNodes()) {
        addBubble(WELCOME_MSG, "ai");
      }
      chatInput.focus();
    }

    function closeChat() {
      chatPanel.classList.add("chat-hidden");
    }

    function sendMessage() {
      const text = chatInput.value.trim();
      if (!text) return;

      addBubble(text, "user");
      chatInput.value = "";
      chatSend.disabled = true;

      const typing = addBubble("Thinking...", "typing");

      fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: "web-client" }),
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          typing.remove();
          addBubble(data.response || data.error || "No response", "ai");
        })
        .catch(function () {
          typing.remove();
          addBubble("Sorry, something went wrong. Please try again.", "ai");
        })
        .finally(function () {
          chatSend.disabled = false;
          chatInput.focus();
        });
    }

    chatToggle.addEventListener("click", function () {
      chatPanel.classList.contains("chat-hidden") ? openChat() : closeChat();
    });
    chatClose.addEventListener("click", closeChat);
    chatSend.addEventListener("click", sendMessage);
    chatInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") sendMessage();
    });
  }

  // --- Transfer form ---
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
