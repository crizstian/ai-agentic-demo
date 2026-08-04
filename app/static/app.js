// DemoBank AI SDLC — client-side JS
// Handles the transfer form submission via fetch

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
          const div = document.createElement("div");
          div.className = "alert alert-success";
          div.style.cssText = "font-size:18px;font-weight:800;padding:24px;";
          div.appendChild(document.createTextNode("Transfer completed successfully!"));
          div.appendChild(document.createElement("br"));
          const amountLine = document.createElement("strong");
          amountLine.textContent = "Amount transferred: $" + Number(result.amount).toFixed(2);
          div.appendChild(amountLine);
          div.appendChild(document.createElement("br"));
          const txSpan = document.createElement("span");
          txSpan.style.cssText = "font-size:12px;color:#276749;";
          txSpan.textContent = "Transaction ID: " + parseInt(result.transferId, 10);
          div.appendChild(txSpan);
          resultDiv.replaceChildren(div);
        } else {
          const div = document.createElement("div");
          div.className = "alert alert-error";
          div.textContent = "Error: " + (result.error || "Unknown error");
          resultDiv.replaceChildren(div);
        }
      })
      .catch(() => {
        document.getElementById("transfer-result").innerHTML =
          '<div class="alert alert-error">Transfer request failed.</div>';
      });
  });
});
