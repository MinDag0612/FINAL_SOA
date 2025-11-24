(() => {
  const LOGIN_PAGE = "../Login/Login.html";
  const DEFAULT_BASE = localStorage.getItem("soa_api_base") || window.location.origin;

  const getAuth = () => {
    try {
      return JSON.parse(localStorage.getItem("soa_auth") || "{}");
    } catch (err) {
      console.warn("Cannot parse auth cache", err);
      return {};
    }
  };

  const setAuth = (payload) => {
    localStorage.setItem("soa_auth", JSON.stringify(payload));
  };

  const clearAuth = () => {
    localStorage.removeItem("soa_auth");
  };

  const request = async (path, options = {}) => {
    const auth = getAuth();
    const headers = new Headers(options.headers || {});
    if (!headers.has("Content-Type") && options.body) {
      headers.set("Content-Type", "application/json");
    }
    if (auth.token) {
      headers.set("Authorization", `Bearer ${auth.token}`);
    }

    const resp = await fetch(`${DEFAULT_BASE}${path}`, {
      ...options,
      headers,
    });

    if (resp.status === 401) {
      clearAuth();
      window.location.href = LOGIN_PAGE;
      return;
    }

    if (!resp.ok) {
      const message = await resp.text();
      throw new Error(message || `Request failed: ${resp.status}`);
    }
    const contentType = resp.headers.get("content-type") || "";
    if (contentType.includes("application/json")) return resp.json();
    return resp.text();
  };

  const api = {
    base: DEFAULT_BASE,
    getAuth,
    setAuth,
    clearAuth,
    request,
    court: {
      list: async () => {
        const res = await request("/court/court");
        return res?.data || [];
      },
    },
    booking: {
      list: async () => {
        const res = await request("/booking/booking");
        return res?.data || [];
      },
      create: async (payload) => {
        return request("/booking/booking", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      },
      cancel: async (bookingId, payload) => {
        return request(`/booking/booking/${bookingId}/cancel`, {
          method: "POST",
          body: JSON.stringify(payload || { reason: "Người dùng hủy" }),
        });
      },
    },
    billing: {
      history: async (userId, limit = 10) => {
        const res = await request(`/billing/history?userId=${userId}&limit=${limit}`);
        return res?.data || [];
      },
      pay: async (invoiceId, bookingId, method = "vnpay", returnUrl) => {
        return request(`/billing/${invoiceId}/pay`, {
          method: "POST",
          body: JSON.stringify({ booking_id: bookingId, method, return_url: returnUrl }),
        });
      },
    },
    facility: {
      list: async () => {
        const res = await request("/facility/facility");
        return res?.data || [];
      },
    },
    auth: {
      redirectToLogin: () => {
        window.location.href = LOGIN_PAGE;
      },
    },
  };

  window.api = api;
})();
