// DemoBank AI SDLC — client-side JS
// Handles the transfer form submission via fetch

document.addEventListener("DOMContentLoaded", function () {
  // --- AI Chat Widget ---
  const chatToggle = document.getElementById("chat-toggle");
  const chatPanel = document.getElementById("chat-panel");
  const chatClose = document.getElementById("chat-close");
  const chatForm = document.getElementById("chat-input-form");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");

  if (chatToggle && chatPanel) {
    let chatOpened = false;

    function addMessage(text, type) {
      const bubble = document.createElement("div");
      bubble.className = "chat-bubble chat-bubble--" + type;
      bubble.textContent = text;
      chatMessages.appendChild(bubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      return bubble;
    }

    chatToggle.addEventListener("click", function () {
      chatPanel.classList.remove("chat-panel--hidden");
      chatToggle.style.display = "none";
      chatInput.focus();
      if (!chatOpened) {
        addMessage(
          "Hello! I'm your AI banking assistant. Ask me about your accounts, transactions, or exchange rates.",
          "ai"
        );
        chatOpened = true;
      }
    });

    chatClose.addEventListener("click", function () {
      chatPanel.classList.add("chat-panel--hidden");
      chatToggle.style.display = "flex";
    });

    chatForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var msg = chatInput.value.trim();
      if (!msg) return;

      addMessage(msg, "user");
      chatInput.value = "";

      var typing = addMessage("Thinking...", "typing");

      fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, session_id: "web-client" }),
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          typing.remove();
          addMessage(data.response || "Sorry, I couldn't process that request.", "ai");
        })
        .catch(function () {
          typing.remove();
          addMessage("Connection error. Please try again.", "ai");
        });
    });
  }

  // --- Transfer Form ---
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
