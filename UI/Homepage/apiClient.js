(() => {
  const LOGIN_PAGE = "../Login/Login.html";

  // Ưu tiên domain hiện tại; chỉ dùng cache nếu cùng host để tránh gọi nhầm về localhost khi chạy qua ngrok
  const resolveBase = () => {
    const cached = localStorage.getItem("soa_api_base");
    const current = window.location.origin;
    if (!cached) return current;
    try {
      const cachedUrl = new URL(cached);
      const currentUrl = new URL(current);
      const sameHost = cachedUrl.host === currentUrl.host;
      const sameProtocol = cachedUrl.protocol === currentUrl.protocol;
      // Nếu trang đang ở https (ngrok) nhưng cache là http, ưu tiên current để tránh mixed-content
      if (sameHost && sameProtocol) return cached;
    } catch (err) {
      console.warn("Invalid soa_api_base cache", cached);
    }
    return current;
  };
  const DEFAULT_BASE = resolveBase();
  console.info("SOA API base", DEFAULT_BASE);

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

  const withCacheBuster = (url) => {
    const cacheParam = `_=${Date.now()}`;
    return url.includes("?") ? `${url}&${cacheParam}` : `${url}?${cacheParam}`;
  };

  const request = async (path, options = {}) => {
    const { forceRefresh = false, ...fetchOptions } = options;
    const auth = getAuth();
    const headers = new Headers(fetchOptions.headers || {});
    if (!headers.has("Content-Type") && fetchOptions.body) {
      headers.set("Content-Type", "application/json");
    }
    if (auth.token) {
      headers.set("Authorization", `Bearer ${auth.token}`);
    }
    
    // Add ngrok bypass header
    headers.set("ngrok-skip-browser-warning", "true");

    if (forceRefresh) {
      headers.set("Cache-Control", "no-cache");
      headers.set("Pragma", "no-cache");
    }
    const requestUrl = forceRefresh ? withCacheBuster(`${DEFAULT_BASE}${path}`) : `${DEFAULT_BASE}${path}`;
    const resp = await fetch(requestUrl, {
      ...fetchOptions,
      headers,
      cache: forceRefresh ? "no-store" : fetchOptions.cache,
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
        try {
          const res = await request("/court/court");
          return res?.data || res || [];
        } catch (err) {
          console.error("Court list error:", err);
          throw err;
        }
      },
      listByFacility: async (facilityId) => {
        if (!facilityId) return [];
        try {
          const res = await request(`/court/manager/${facilityId}/courts`);
          console.log("[API] Courts raw response:", res);
          
          // Extract courts array from response
          let courts = [];
          if (Array.isArray(res)) {
            courts = res;
          } else if (res?.data?.courts && Array.isArray(res.data.courts)) {
            courts = res.data.courts;
          } else if (res?.data && Array.isArray(res.data)) {
            courts = res.data;
          } else if (res?.courts && Array.isArray(res.courts)) {
            courts = res.courts;
          }
          
          console.log("[API] Extracted courts:", courts.length, "courts");
          return courts;
        } catch (err) {
          console.error("Manager court list error:", err);
          return []; // Return empty array instead of throwing
        }
      },
    },
    booking: {
      list: async (query = {}, options = {}) => {
        try {
          const params = new URLSearchParams();
          Object.entries(query).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== "") {
              params.append(key, value);
            }
          });
          const queryString = params.toString();
          const res = await request(`/booking/booking${queryString ? `?${queryString}` : ""}`, options);
          return res?.data || res || [];
        } catch (err) {
          console.error("Booking list error:", err);
          throw err;
        }
      },
      get: async (bookingId, options = {}) => {
        try {
          const res = await request(`/booking/booking/${bookingId}`, options);
          return res?.data || res;
        } catch (err) {
          console.error("Booking get error:", err);
          throw err;
        }
      },
      delete: async (bookingId, options = {}) => {
        try {
          return request(`/booking/booking/${bookingId}`, {
            method: "DELETE",
            ...options,
          });
        } catch (err) {
          console.error("Booking delete error:", err);
          throw err;
        }
      },
      create: async (payload) => {
        try {
          const res = await request("/booking/booking", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          return res;
        } catch (err) {
          console.error("Booking create error:", err);
          throw err;
        }
      },
      managerList: async (facilityId, date) => {
        if (!facilityId) return [];
        try {
          const params = new URLSearchParams();
          if (date) params.append("date", date);
          const queryString = params.toString();
          const res = await request(
            `/booking/manager/${facilityId}/bookings${queryString ? `?${queryString}` : ""}`
          );
          const bookings = res?.data || res || [];
          console.log("[API] Bookings response:", bookings, "isArray:", Array.isArray(bookings));
          return Array.isArray(bookings) ? bookings : [];
        } catch (err) {
          console.error("Manager booking list error:", err);
          return []; // Return empty array instead of throwing
        }
      },
      cancel: async (bookingId, payload) => {
        try {
          return request(`/booking/booking/${bookingId}/cancel`, {
            method: "POST",
            body: JSON.stringify(payload || { reason: "Người dùng hủy" }),
          });
        } catch (err) {
          console.error("Booking cancel error:", err);
          throw err;
        }
      },
      updateStatus: async (bookingId, status) => {
        try {
          return request(`/booking/booking/${bookingId}`, {
            method: "PUT",
            body: JSON.stringify({ status }),
          });
        } catch (err) {
          console.error("Booking update status error:", err);
          throw err;
        }
      },
    },
    facility: {
      list: async () => {
        try {
          const res = await request("/facility/facility");
          return res?.data || res || [];
        } catch (err) {
          console.error("Facility list error:", err);
          throw err;
        }
      },
      managerList: async () => {
        try {
          const res = await request("/facility/manager/facilities");
          console.log("[API] Manager facilities response:", res);
          const facilities = res?.data || res || [];
          console.log("[API] Extracted facilities:", facilities, "isArray:", Array.isArray(facilities));
          return Array.isArray(facilities) ? facilities : [];
        } catch (err) {
          console.error("Manager facility list error:", err);
          return []; // Return empty array on error instead of throwing
        }
      },
    },
    billing: {
      history: async (userId, limit = 10) => {
        try {
          const res = await request(`/billing/history?userId=${userId}&limit=${limit}`);
          return res?.data || res || [];
        } catch (err) {
          console.error("Billing history error:", err);
          return [];
        }
      },
      createInvoice: async (payload) => {
        try {
          const res = await request("/billing/", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          return res?.data || res;
        } catch (err) {
          console.error("Create invoice error:", err);
          throw err;
        }
      },
      initiatePayment: async (invoiceId, payload) => {
        try {
          const res = await request(`/billing/${invoiceId}/pay`, {
            method: "POST",
            body: JSON.stringify(payload),
          });
          return res;
        } catch (err) {
          console.error("Initiate payment error:", err);
          throw err;
        }
      },
      getInvoice: async (invoiceId) => {
        try {
          const res = await request(`/billing/${invoiceId}`);
          return res?.data || res;
        } catch (err) {
          console.error("Get invoice error:", err);
          throw err;
        }
      },
      // SePay Payment Gateway
      createSePayPayment: async (invoiceId, payload) => {
        try {
          const res = await request(`/billing/${invoiceId}/sepay/create-payment`, {
            method: "POST",
            body: JSON.stringify(payload),
          });
          return res?.data || res;
        } catch (err) {
          console.error("Create SePay payment error:", err);
          throw err;
        }
      },
    },
    auth: {
      redirectToLogin: () => {
        window.location.href = LOGIN_PAGE;
      },
    },
    notification: {
      sendEmailVerify: async (userPayload) => {
        try {
          const res = await request("/notification/send-email-verify-register", {
            method: "POST",
            body: JSON.stringify(userPayload),
          });
          return res?.data || res;
        } catch (err) {
          console.error("Send email verify error:", err);
          throw err;
        }
      },
      sendBookingConfirmed: async (bookingInfo) => {
        try {
          const res = await request("/notification/send-booking-confirmed", {
            method: "POST",
            body: JSON.stringify(bookingInfo),
          });
          return res?.data || res;
        } catch (err) {
          console.error("Send booking confirmed error:", err);
          throw err;
        }
      },
    },
    report: {
      getPlaytimePlot: async (courtId) => {
        try {
          // This returns an image, not JSON
          const auth = getAuth();
          const headers = new Headers();
          if (auth.token) {
            headers.set("Authorization", `Bearer ${auth.token}`);
          }
          headers.set("ngrok-skip-browser-warning", "true");
          
          const resp = await fetch(`${DEFAULT_BASE}/report/manager/report-playtime-plot/court=${courtId}`, {
            headers,
          });
          
          if (!resp.ok) {
            throw new Error(`Failed to fetch playtime plot: ${resp.status}`);
          }
          
          // Return blob URL for image
          const blob = await resp.blob();
          return URL.createObjectURL(blob);
        } catch (err) {
          console.error("Get playtime plot error:", err);
          throw err;
        }
      },
    },
    notification: {
      sendBookingConfirmed: async (payload) => {
        try {
          // payload: { booking_id, user_email, scheduled_time, court_name }
          return await request("/notification/send-booking-confirmed", {
            method: "POST",
            body: JSON.stringify(payload),
          });
        } catch (err) {
          console.error("Send booking confirmation email error:", err);
          // Don't throw - email failure shouldn't block booking flow
          return { status: "error", message: err.message };
        }
      },
    },
  };

  window.api = api;
})();
