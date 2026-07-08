document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  let mode = params.get("mode") === "signup" ? "signup" : "login";

  const title = document.getElementById("auth-title");
  const subtitle = document.getElementById("auth-subtitle");
  const signupFields = document.getElementById("signup-fields");
  const loginOptions = document.getElementById("login-options");
  const btnText = document.getElementById("submit-btn-text");
  const switchText = document.getElementById("switch-text");
  const switchBtn = document.getElementById("switch-auth-mode");
  const form = document.getElementById("auth-form");

  const updateUI = () => {
    if (mode === "signup") {
      title.innerText = "Create Account";
      subtitle.innerText = "Join our network of premium creators and modern writers.";
      signupFields.classList.remove("hidden");
      loginOptions.classList.add("hidden");
      btnText.innerText = "Get Started";
      switchText.innerText = "Already registered?";
      switchBtn.innerText = "Sign in";
    } else {
      title.innerText = "Welcome Back";
      subtitle.innerText = "Enter your credentials to access your luxury writer hub.";
      signupFields.classList.add("hidden");
      loginOptions.classList.remove("hidden");
      btnText.innerText = "Sign In";
      switchText.innerText = "Don't have an account?";
      switchBtn.innerText = "Sign up";
    }
    lucide.createIcons();
  };

  switchBtn.addEventListener("click", () => {
    mode = mode === "login" ? "signup" : "login";
    updateUI();
  });

  // Password Visibility Toggle
  document.getElementById("toggle-pwd").addEventListener("click", () => {
    const pwdInput = document.getElementById("password");
    pwdInput.type = pwdInput.type === "password" ? "text" : "password";
  });

  // Handle Backend Communication via Fetch API
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    
    let url = "http://127.0.0.1:8080/api/auth/login";
    let bodyData = { email, password };

    if (mode === "signup") {
      url = "http://127.0.0.1:8080/api/auth/signup";
      bodyData.full_name = document.getElementById("fullname").value;
      bodyData.username = document.getElementById("username").value;
    }

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bodyData)
      });

      const resData = await response.json();
      if (!response.ok) throw new Error(resData.detail || "Authentication Failed");

      // Set auth keys to local storage tokens
      localStorage.setItem("access_token", resData.access_token);
      localStorage.setItem("refresh_token", resData.refresh_token);
      
      window.location.href = "dashboard.html";
    } catch (err) {
      alert(err.message);
    }
  });

  updateUI();
});