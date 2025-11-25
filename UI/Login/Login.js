const container = document.querySelector(".container");
const registerBtn = document.querySelector(".register-btn");
const loginBtn = document.querySelector(".login-btn");

const API_BASE = localStorage.getItem("soa_api_base") || "http://localhost";
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

  try {
    const resp = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    if (!data?.token || !data?.user) throw new Error("Thông tin đăng nhập không hợp lệ");
    saveAuth({ token: data.token, user: data.user });
    setMessage(LOGIN_MESSAGE, "Đăng nhập thành công!");
    setTimeout(() => {
      window.location.href = "../Homepage/homepage.html";
    }, 500);
  } catch (err) {
    console.error(err);
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

  try {
    const resp = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fullname, email, password, role }),
    });
    if (!resp.ok) throw new Error(await resp.text());
    await resp.json();
    setMessage(REGISTER_MESSAGE, "Tạo tài khoản thành công! Vui lòng đăng nhập.");
    setTimeout(() => {
      container.classList.remove("active");
    }, 500);
  } catch (err) {
    console.error(err);
    setMessage(REGISTER_MESSAGE, err.message || "Đăng ký thất bại", true);
  }
});
