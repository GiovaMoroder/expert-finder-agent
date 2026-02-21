const askForm = document.getElementById("ask-form");
const outputEl = document.getElementById("output");
const errorEl = document.getElementById("error");
const logoutBtn = document.getElementById("logout");

if (askForm && outputEl && errorEl) {
  askForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorEl.textContent = "";
    const questionInput = document.getElementById("question");
    const question = questionInput ? questionInput.value.trim() : "";
    if (!question) {
      errorEl.textContent = "Question is required.";
      return;
    }

    outputEl.textContent = "Running...";
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (response.status === 401) {
      window.location.href = "/login";
      return;
    }

    const payload = await response.json();
    if (!response.ok) {
      errorEl.textContent = payload.detail || "Request failed.";
      outputEl.textContent = "";
      return;
    }

    outputEl.textContent = JSON.stringify(payload, null, 2);
  });
}

if (logoutBtn) {
  logoutBtn.addEventListener("click", async () => {
    await fetch("/logout", { method: "POST" });
    window.location.href = "/login";
  });
}

