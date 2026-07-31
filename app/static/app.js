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
          const successDiv = document.createElement("div");
          successDiv.className = "alert alert-success";
          successDiv.style.fontSize = "18px";
          successDiv.style.fontWeight = "800";
          successDiv.style.padding = "24px";

          const line1 = document.createTextNode("✅ Transfer completed successfully!");
          const br1 = document.createElement("br");
          const line2 = document.createTextNode("Amount transferred: $");
          const amountStrong = document.createElement("strong");
          amountStrong.textContent = String(result.amount ?? "N/A");
          const br2 = document.createElement("br");
          const txIdSpan = document.createElement("span");
          txIdSpan.style.fontSize = "12px";
          txIdSpan.style.color = "#276749";
          txIdSpan.textContent = "Transaction ID: " + String(result.transferId ?? "N/A");

          successDiv.appendChild(line1);
          successDiv.appendChild(br1);
          successDiv.appendChild(line2);
          successDiv.appendChild(amountStrong);
          successDiv.appendChild(br2);
          successDiv.appendChild(txIdSpan);

          while (resultDiv.firstChild) resultDiv.removeChild(resultDiv.firstChild);
          resultDiv.appendChild(successDiv);
        } else {
          const errorDiv = document.createElement("div");
          errorDiv.className = "alert alert-error";
          errorDiv.textContent = "Error: " + String(result.error ?? "Unknown error");
          while (resultDiv.firstChild) resultDiv.removeChild(resultDiv.firstChild);
          resultDiv.appendChild(errorDiv);
        }
      })
      .catch(() => {
        const resultDiv = document.getElementById("transfer-result");
        const errorDiv = document.createElement("div");
        errorDiv.className = "alert alert-error";
        errorDiv.textContent = "Transfer request failed.";
        while (resultDiv.firstChild) resultDiv.removeChild(resultDiv.firstChild);
        resultDiv.appendChild(errorDiv);
      });
  });
});
