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
          // FIXED: DOM XSS vulnerability - using textContent instead of innerHTML
          const successDiv = document.createElement("div");
          successDiv.className = "alert alert-success";
          successDiv.style.fontSize = "18px";
          successDiv.style.fontWeight = "800";
          successDiv.style.padding = "24px";

          successDiv.textContent = "✅ Transfer completed successfully!\nAmount transferred: $";

          const amountStrong = document.createElement("strong");
          amountStrong.textContent = String(result.amount);
          successDiv.appendChild(amountStrong);

          const txIdSpan = document.createElement("span");
          txIdSpan.style.fontSize = "12px";
          txIdSpan.style.color = "#276749";
          txIdSpan.textContent = "\nTransaction ID: " + String(result.transferId);
          successDiv.appendChild(txIdSpan);

          resultDiv.innerHTML = "";
          resultDiv.appendChild(successDiv);
        } else {
          // FIXED: DOM XSS vulnerability - using textContent instead of innerHTML
          const errorDiv = document.createElement("div");
          errorDiv.className = "alert alert-error";
          errorDiv.textContent = "Error: " + String(result.error);
          resultDiv.innerHTML = "";
          resultDiv.appendChild(errorDiv);
        }
      })
      .catch(() => {
        // FIXED: DOM XSS vulnerability - using textContent instead of innerHTML
        const resultDiv = document.getElementById("transfer-result");
        const errorDiv = document.createElement("div");
        errorDiv.className = "alert alert-error";
        errorDiv.textContent = "Transfer request failed.";
        resultDiv.innerHTML = "";
        resultDiv.appendChild(errorDiv);
      });
  });
});
