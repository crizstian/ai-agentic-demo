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
          const amount = document.createElement("strong");
          amount.textContent = "$" + result.amount;
          const txId = document.createElement("span");
          txId.style.cssText = "font-size:12px;color:#276749;";
          txId.textContent = "Transaction ID: " + result.transferId;
          const msg = document.createElement("div");
          msg.className = "alert alert-success";
          msg.style.cssText = "font-size:18px;font-weight:800;padding:24px;";
          msg.append("✅ Transfer completed successfully!\nAmount transferred: ", amount, document.createElement("br"), txId);
          resultDiv.replaceChildren(msg);
        } else {
          const errDiv = document.createElement("div");
          errDiv.className = "alert alert-error";
          errDiv.textContent = "Error: " + (result.error || "Unknown error");
          resultDiv.replaceChildren(errDiv);
        }
      })
      .catch(() => {
        document.getElementById("transfer-result").innerHTML =
          '<div class="alert alert-error">Transfer request failed.</div>';
      });
  });
});
