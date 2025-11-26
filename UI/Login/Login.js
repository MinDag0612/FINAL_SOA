const container = document.querySelector(".container");
const registerBtn = document.querySelector(".register-btn");
const loginBtn = document.querySelector(".login-btn");

const resolveBase = () => {
  const cached = localStorage.getItem("soa_api_base");
  const current = window.location.origin;
  if (!cached) return current;
  try {
    const cachedUrl = new URL(cached);
    const currentUrl = new URL(current);
    const sameHost = cachedUrl.host === currentUrl.host;
    const sameProtocol = cachedUrl.protocol === currentUrl.protocol;
    if (sameHost && sameProtocol) return cached;
  } catch (err) {
    console.warn("Invalid cached soa_api_base", cached);
  }
  return current;
};
const API_BASE = resolveBase();
const LOGIN_MESSAGE = document.getElementById("login-message");
const REGISTER_MESSAGE = document.getElementById("register-message");

registerBtn.addEventListener("click", () => {
  container.classList.add("active");
});

loginBtn.addEventListener("click", () => {
  container.classList.remove("active");
});

function setMessage(el, msg, isError = false) {
  if (!el) return;
  el.textContent = msg;
  el.style.color = isError ? "#ef4444" : "#16a34a";
}

function saveAuth(authPayload) {
  localStorage.setItem("soa_auth", JSON.stringify(authPayload));
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  setMessage(LOGIN_MESSAGE, "");
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  if (!email || !password) {
    setMessage(LOGIN_MESSAGE, "Vui lòng nhập email và mật khẩu", true);
    return;
  }

  try {
    const resp = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!resp.ok) {
      const errorText = await resp.text();
      throw new Error(errorText || `HTTP ${resp.status}`);
    }
    const data = await resp.json();
    if (!data?.token) throw new Error("Token không tìm thấy trong response");
    const user = data?.user || { email, user_id: null };
    saveAuth({ token: data.token, user });
    setMessage(LOGIN_MESSAGE, "Đăng nhập thành công!");
    setTimeout(() => {
      window.location.href = "../Homepage/homepage.html";
    }, 500);
  } catch (err) {
    console.error("Login error:", err);
    setMessage(LOGIN_MESSAGE, err.message || "Đăng nhập thất bại", true);
  }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  setMessage(REGISTER_MESSAGE, "");
  const fullname = document.getElementById("register-fullname").value;
  const email = document.getElementById("register-email").value;
  const password = document.getElementById("register-password").value;
  const role = document.getElementById("register-role").value || "customer";

  if (!fullname || !email || !password) {
    setMessage(REGISTER_MESSAGE, "Vui lòng nhập đủ thông tin", true);
    return;
  }

  try {
    const resp = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fullname, email, password, role }),
    });
    if (!resp.ok) {
      const errorText = await resp.text();
      throw new Error(errorText || `HTTP ${resp.status}`);
    }
    await resp.json();
    setMessage(REGISTER_MESSAGE, "Tạo tài khoản thành công! Vui lòng đăng nhập.");
    setTimeout(() => {
      container.classList.remove("active");
      document.getElementById("register-form").reset();
      document.getElementById("login-form").reset();
    }, 500);
  } catch (err) {
    console.error("Register error:", err);
    setMessage(REGISTER_MESSAGE, err.message || "Đăng ký thất bại", true);
  }
});
