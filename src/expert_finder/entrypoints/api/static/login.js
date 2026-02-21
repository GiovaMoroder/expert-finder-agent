const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("error");

if (loginForm && loginError) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    loginError.textContent = "";
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const username = usernameInput ? usernameInput.value.trim() : "";
    const password = passwordInput ? passwordInput.value : "";

    // UI login uses the same OAuth2 password flow, but relies on the HttpOnly cookie
    // set by the server (so JS never stores the token).
    const form = new URLSearchParams();
    form.set("username", username);
    form.set("password", password);

    const response = await fetch("/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({ detail: "Login failed." }));
      loginError.textContent = payload.detail || "Login failed.";
      return;
    }

    window.location.href = "/";
  });
}

