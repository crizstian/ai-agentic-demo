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
        const esc = (v) => {
          const d = document.createElement("div");
          d.appendChild(document.createTextNode(String(v)));
          return d.innerHTML;
        };
        if (result.success) {
          resultDiv.innerHTML =
            '<div class="alert alert-success" style="font-size:18px;font-weight:800;padding:24px;">✅ Transfer completed successfully!<br>Amount transferred: <strong>$' +
            esc(result.amount) +
            '</strong><br><span style="font-size:12px;color:#276749;">Transaction ID: ' +
            esc(result.transferId) +
            "</span></div>";
        } else {
          resultDiv.innerHTML =
            '<div class="alert alert-error">Error: ' + esc(result.error) + "</div>";
        }
      })
      .catch(() => {
        document.getElementById("transfer-result").innerHTML =
          '<div class="alert alert-error">Transfer request failed.</div>';
      });
  });
});
