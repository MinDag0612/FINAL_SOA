const dynamicContent = document.getElementById("dynamic-content");
const pageTitle = document.getElementById("page-title");

const START_HOUR = 0;
const END_HOUR = 24;
const DEFAULT_VIEW_HOUR = 8;
const HOURLY_RATE = 50000;
const SAVED_FACILITY = parseInt(localStorage.getItem("soa_facility_id") || "", 10) || null;
const SAVED_DATE = localStorage.getItem("soa_booking_date") || null;
const SHOULD_PROMPT_SELECTION = !SAVED_FACILITY;
const SLOT_STEP_MINUTES = 60;

let currentView = "dashboard";
let state = {
  courts: [],
  bookings: [],
  facilities: [],
  managerFacilities: [],
  managerFacilityId: SAVED_FACILITY,
  managerDate: SAVED_DATE,
  selectedFacilityId: SAVED_FACILITY,
  selectedDate: SAVED_DATE,
  selectedSlots: [],
  userProfile: {
    id: null,
    name: "Khách hàng",
    phone: "Chưa cập nhật",
    email: "",
    balance: 0,
    rank: "Khách",
  },
};

// Expose state to window for manager modules
window.state = state;

function formatCurrency(amount = 0) {
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(amount);
}
window.formatCurrency = formatCurrency;

function formatDateVi(dateObj) {
  if (!dateObj) return "--";
  const d = new Date(dateObj);
  return `${String(d.getDate()).padStart(2, "0")}/${String(d.getMonth() + 1).padStart(2, "0")}/${d.getFullYear()}`;
}
window.formatDateVi = formatDateVi;

function formatTimeFromMinutes(minute) {
  const h = Math.floor(minute / 60);
  const mm = String(minute % 60).padStart(2, "0");
  return `${h}:${mm}`;
}

function formatTimeLabel(dateObj) {
  if (!dateObj) return "--:--";
  const h = String(dateObj.getHours()).padStart(2, "0");
  const m = String(dateObj.getMinutes()).padStart(2, "0");
  return `${h}:${m}`;
}

function formatSlotRangeLabel(startMinute) {
  const endMinute = startMinute + SLOT_STEP_MINUTES;
  return `${formatTimeFromMinutes(startMinute)} - ${formatTimeFromMinutes(endMinute)}`;
}

function showToast(msg) {
  const toast = document.getElementById("toast");
  document.getElementById("toast-msg").innerText = msg;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}
window.showToast = showToast;

function showConfirmDialog(message, onConfirm) {
  const existing = document.getElementById("confirm-overlay");
  if (existing) existing.remove();
  const overlay = document.createElement("div");
  overlay.id = "confirm-overlay";
  overlay.style.position = "fixed";
  overlay.style.inset = "0";
  overlay.style.background = "rgba(0,0,0,0.45)";
  overlay.style.display = "flex";
  overlay.style.alignItems = "center";
  overlay.style.justifyContent = "center";
  overlay.style.zIndex = "9999";
  overlay.innerHTML = `
    <div style="background:#0f172a;color:#e2e8f0;padding:18px 20px;border-radius:12px;min-width:300px;box-shadow:0 10px 30px rgba(0,0,0,0.25);">
      <div style="font-weight:600;margin-bottom:8px;">Xác nhận</div>
      <div style="margin-bottom:16px;font-size:14px;line-height:1.4;">${message}</div>
      <div style="display:flex;justify-content:flex-end;gap:10px;">
        <button id="confirm-cancel" style="padding:8px 12px;border-radius:8px;border:1px solid #94a3b8;background:#1e293b;color:#e2e8f0;cursor:pointer;">Hủy</button>
        <button id="confirm-ok" style="padding:8px 12px;border-radius:8px;border:none;background:#22c55e;color:#0b1120;font-weight:700;cursor:pointer;">Đồng ý</button>
      </div>
    </div>
  `;
  overlay.querySelector("#confirm-cancel").onclick = () => overlay.remove();
  overlay.querySelector("#confirm-ok").onclick = () => {
    overlay.remove();
    onConfirm?.();
  };
  document.body.appendChild(overlay);
}

const STATUS_STYLES = {
  active: { bg: "#dcfce7", border: "#16a34a", text: "#166534", label: "Đã xác nhận" },
  booked: { bg: "#fef9c3", border: "#eab308", text: "#854d0e", label: "Chờ thanh toán" },
  cancelled: { bg: "#fee2e2", border: "#ef4444", text: "#991b1b", label: "Đã hủy" },
  completed: { bg: "#e0f2fe", border: "#0284c7", text: "#0b5394", label: "Hoàn tất" },
  expired: { bg: "#f3f4f6", border: "#9ca3af", text: "#4b5563", label: "Hết hạn" },
  blank: { bg: "#f8fafc", border: "#cbd5e1", text: "#475569", label: "Sân trống" },
};

function getStatusStyle(uiStatus) {
  return STATUS_STYLES[uiStatus] || STATUS_STYLES.blank;
}

function mapUiStatus(status, paymentStatus) {
  if (status === "cancelled" || paymentStatus === "failed") return "cancelled";
  if (status === "completed") return "completed";
  if (status === "expired") return "expired";
  if (status === "confirmed") return "active";
  return "booked";
}

function closeModal(id) {
  document.getElementById(id)?.classList.remove("show");
}

function getAuthOrRedirect() {
  const auth = window.api?.getAuth() || {};
  if (!auth.token) {
    window.api?.auth.redirectToLogin();
    return null;
  }
  return auth;
}

function buildProfileFromAuth(user = {}) {
  return {
    id: user.user_id || user.id || null,
    name: user.fullname || user.name || "Khách hàng",
    phone: user.phone || "Chưa cập nhật",
    email: user.email || "",
    balance: user.balance || 0,
    rank: user.role === "manager" ? "Quản lý" : "Khách hàng",
  };
}

function setAvatarInitials(name) {
  const avatar = document.querySelector(".avatar");
  if (avatar) {
    const initials = name
      .split(" ")
      .filter(Boolean)
      .map((p) => p[0])
      .join("")
      .slice(0, 2)
      .toUpperCase();
    avatar.innerText = initials || "KH";
  }
}

function mapCourt(c) {
  return {
    id: c.court_id || c.id,
    name: c.name || c.court_name || `Sân ${c.court_id || c.id}`,
    type: c.surface_type || c.type || "Tiêu chuẩn",
    facilityId: c.facility_id || c.facilityId || null,
    hourlyRate: c.price_per_hour || c.price || c.hourly_rate || HOURLY_RATE,
  };
}

function isSameDate(dateA, dateStrB) {
  if (!dateA || !dateStrB) return false;
  const d = new Date(dateStrB);
  return (
    dateA.getFullYear() === d.getFullYear() &&
    dateA.getMonth() === d.getMonth() &&
    dateA.getDate() === d.getDate()
  );
}

function normalizeBooking(raw) {
  const firstItem = raw.items && raw.items.length ? raw.items[0] : null;
  let start = null, end = null;
  
  if (firstItem?.start_time) {
    try {
      start = new Date(firstItem.start_time);
      if (isNaN(start.getTime())) start = null;
    } catch (e) {
      console.warn("Invalid start_time:", firstItem.start_time);
      start = null;
    }
  } else if (firstItem?.startTime) {
    try {
      start = new Date(firstItem.startTime);
      if (isNaN(start.getTime())) start = null;
    } catch (e) {
      console.warn("Invalid startTime:", firstItem.startTime);
      start = null;
    }
  }

  if (firstItem?.end_time) {
    try {
      end = new Date(firstItem.end_time);
      if (isNaN(end.getTime())) end = null;
    } catch (e) {
      console.warn("Invalid end_time:", firstItem.end_time);
      end = null;
    }
  } else if (firstItem?.endTime) {
    try {
      end = new Date(firstItem.endTime);
      if (isNaN(end.getTime())) end = null;
    } catch (e) {
      console.warn("Invalid endTime:", firstItem.endTime);
      end = null;
    }
  }

  const duration = start && end ? (end - start) / (1000 * 60 * 60) : null;
  const itemTotal = Array.isArray(raw.items)
    ? raw.items.reduce((sum, it) => sum + (it.total_price || it.totalPrice || it.price || 0), 0)
    : null;
  const inferredRate = getCourtHourlyRate(firstItem?.court_id || firstItem?.courtId);
  const uiStatus = mapUiStatus(raw.status, raw.payment_status);
  const paymentRef = raw.payment_reference || raw.paymentReference;
  return {
    id: raw.booking_id || raw.id,
    courtId: firstItem?.court_id || firstItem?.courtId,
    facilityId: raw.facility_id || raw.facilityId || null,
    startHour: start ? start.getHours() : null,
    duration: duration || 0,
    status: raw.status,
    uiStatus,
    paymentStatus: raw.payment_status,
    paymentReference: paymentRef,
    customer: state.userProfile.name,
    start,
    end,
    total: raw.total_amount || itemTotal || (firstItem?.price ?? (duration || 1) * (inferredRate || HOURLY_RATE)),
    raw,
  };
}

function getCourtName(courtId) {
  return state.courts.find((c) => c.id === courtId)?.name || `Sân #${courtId}`;
}

function getFacilityName(facilityId) {
  return state.facilities.find((f) => f.facility_id === facilityId || f.id === facilityId)?.name || `Cơ sở #${facilityId}`;
}

function getFacilityInfo(facilityId) {
  return state.facilities.find((f) => f.facility_id === facilityId || f.id === facilityId) || {};
}

function getFacilityCode(facilityId) {
  const facility = state.facilities.find((f) => f.facility_id === facilityId || f.id === facilityId);
  if (!facility || !facility.name) return "CN";
  const words = facility.name.split(" ").filter(Boolean);
  return words
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

function setSelection(facilityId, dateStr) {
  state.selectedFacilityId = facilityId;
  state.selectedDate = dateStr;
  state.selectedSlots = [];
  localStorage.setItem("soa_facility_id", facilityId || "");
  localStorage.setItem("soa_booking_date", dateStr || "");
}

function toggleSelectedSlot(courtId, startDate) {
  if (!startDate || Number.isNaN(startDate.getTime())) return;
  const end = new Date(startDate.getTime() + 60 * 60 * 1000);
  const key = `${courtId}-${startDate.toISOString()}`;
  const existingIndex = state.selectedSlots.findIndex((s) => `${s.courtId}-${s.start.toISOString()}` === key);

  if (existingIndex >= 0) {
    state.selectedSlots.splice(existingIndex, 1);
  } else {
    state.selectedSlots.push({ courtId, start: startDate, end });
  }

  state.selectedSlots.sort((a, b) => a.start.getTime() - b.start.getTime());
  updateSelectionBar();
  const body = document.getElementById("timeline-body-grid");
  if (body) {
    body.querySelectorAll(".timeline-cell.active").forEach((c) => c.classList.remove("active"));
    state.selectedSlots.forEach((slot) => {
      const cell = body.querySelector(`.timeline-cell[data-court="${slot.courtId}"][data-start="${slot.start.toISOString()}"]`);
      if (cell) cell.classList.add("active");
    });
  }
}

function getCourtHourlyRate(courtId) {
  const rate = state.courts.find((c) => c.id === courtId)?.hourlyRate;
  const num = typeof rate === "number" ? rate : parseFloat(rate);
  return Number.isFinite(num) ? num : HOURLY_RATE;
}

function summarizeSelectionPricing(slots) {
  if (!slots || !slots.length) return { total: 0, hours: 0, priceLabel: "--", rates: [] };
  const infos = slots.map((slot) => {
    const hours = (slot.end - slot.start) / (1000 * 60 * 60) || 1;
    const rate = getCourtHourlyRate(slot.courtId);
    return { hours, rate };
  });
  const total = infos.reduce((sum, item) => sum + item.hours * item.rate, 0);
  const hours = infos.reduce((sum, item) => sum + item.hours, 0);
  const rates = Array.from(new Set(infos.map((i) => i.rate)));
  const minRate = Math.min(...rates);
  const maxRate = Math.max(...rates);
  let priceLabel = formatCurrency(minRate);
  if (rates.length > 1 && maxRate !== minRate) priceLabel = `${formatCurrency(minRate)} - ${formatCurrency(maxRate)} (theo sân)`;
  return { total, hours, priceLabel, rates };
}

function isSlotSelected(courtId, startDate) {
  if (!startDate) return false;
  const key = `${courtId}-${startDate.toISOString()}`;
  return state.selectedSlots.some((s) => `${s.courtId}-${s.start.toISOString()}` === key);
}

function updateSelectionBar() {
  const textEl = document.getElementById("selection-text");
  const totalEl = document.getElementById("selection-total");
  const nextBtn = document.getElementById("btn-next");
  if (!textEl || !totalEl || !nextBtn) return;
  if (!state.selectedSlots.length) {
    textEl.innerText = "Chưa chọn";
    totalEl.innerText = "0 đ";
    nextBtn.disabled = true;
    return;
  }
  const { total } = summarizeSelectionPricing(state.selectedSlots);
  const first = state.selectedSlots[0];
  const label = first
    ? `${getCourtName(first.courtId)} · ${first.start.getHours()}:${String(first.start.getMinutes()).padStart(2, "0")} - ${first.end
        .getHours()
        .toString()
        .padStart(2, "0")}:${String(first.end.getMinutes()).padStart(2, "0")}`
    : "Đã chọn";
  const suffix = state.selectedSlots.length > 1 ? `  +${state.selectedSlots.length - 1} ô khác` : "";
  textEl.innerText = `${label}${suffix}`;
  totalEl.innerText = formatCurrency(total);
  nextBtn.disabled = false;
}

function openQuickCheckout() {
  if (!state.selectedSlots.length) {
    showToast("Vui lòng chọn khung giờ trước.");
    return;
  }
  const modal = document.getElementById("quickCheckoutModal");
  if (!modal) return;
  const facility = getFacilityInfo(state.selectedFacilityId);
  const branchCode = getFacilityCode(state.selectedFacilityId);
  const pricing = summarizeSelectionPricing(state.selectedSlots);
  const firstSlotRate = getCourtHourlyRate(state.selectedSlots[0].courtId);
  const totalHours = pricing.hours;
  const total = pricing.total;

  const slotText = state.selectedSlots
    .map((slot) => {
      const timeRange = `${formatTimeLabel(slot.start)} - ${formatTimeLabel(slot.end)}`;
      return `<div class="slot-line">• ${getCourtName(slot.courtId)}: ${timeRange} (${formatDateVi(slot.start)} - ${branchCode})</div>`;
    })
    .join("");

  const summaryFields = {
    "qc-branch": `CN ${branchCode} ${facility.name ? "- " + facility.name : ""}`,
    "qc-address": facility.address || facility.location || "Đang cập nhật địa chỉ",
    "qc-slot": slotText || "--",
    "qc-price-hour": state.selectedSlots.length > 1 ? pricing.priceLabel : formatCurrency(firstSlotRate),
    "qc-hour-count": totalHours,
    "qc-total": formatCurrency(total),
  };
  Object.entries(summaryFields).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (!el) return;
    if (id === "qc-slot") {
      el.innerHTML = val;
    } else {
      el.innerText = val;
    }
  });

  const nameInput = document.getElementById("qc-name");
  const phoneInput = document.getElementById("qc-phone");
  const emailInput = document.getElementById("qc-email");
  if (nameInput) nameInput.value = state.userProfile.name || "";
  if (phoneInput) phoneInput.value = state.userProfile.phone || "";
  if (emailInput) emailInput.value = state.userProfile.email || "";

  modal.classList.add("show");
}

async function submitQuickCheckout() {
  if (!state.selectedSlots.length) {
    alert("Vui lòng chọn khung giờ trước.");
    return;
  }
  const name = document.getElementById("qc-name")?.value.trim();
  const phone = document.getElementById("qc-phone")?.value.trim();
  const email = document.getElementById("qc-email")?.value.trim();
  const coupon = document.getElementById("qc-coupon")?.value.trim();
  if (!name || !phone || !email) {
    alert("Vui lòng nhập đủ tên, số điện thoại và email.");
    return;
  }
  if (!state.selectedFacilityId) {
    openSelectionModal();
    return;
  }

  const submitBtn = document.querySelector(".btn-pay-cta");
  const originalText = submitBtn.innerText;
  submitBtn.disabled = true;
  submitBtn.innerText = "Đang xử lý...";

  try {
    const bookingData = {
      facility_id: state.selectedFacilityId,
      items: state.selectedSlots.map((slot) => ({
        court_id: slot.courtId,
        start_time: slot.start.toISOString(),
        end_time: slot.end.toISOString(),
        price: getCourtHourlyRate(slot.courtId),
      })),
      customer_name: name,
      customer_phone: phone,
      customer_email: email,
      coupon: coupon || null,
    };

    const paymentResult = await window.PaymentHandler.processPayment(bookingData, state.userProfile);

    if (!paymentResult.success) {
      alert("Lỗi thanh toán: " + paymentResult.message);
      submitBtn.disabled = false;
      submitBtn.innerText = originalText;
      return;
    }

    console.log("[submitQuickCheckout] Payment result:", paymentResult);

    if (paymentResult.redirectUrl) {
      showToast("Đang chuyển hướng đến trang thanh toán...");
      setTimeout(() => {
        window.location.href = paymentResult.redirectUrl;
      }, 1500);
      return;
    }

    if (paymentResult.paymentStatus === "paid") {
      showToast("Thanh toán thành công! Booking đã được xác nhận.");
      
      await refreshBookings();
      
      closeModal("quickCheckoutModal");
      changeView(currentView);
      state.selectedSlots = [];
      updateSelectionBar();
      
      document.getElementById("qc-name").value = "";
      document.getElementById("qc-phone").value = "";
      document.getElementById("qc-email").value = "";
      document.getElementById("qc-coupon").value = "";
    } else {
      showToast("Booking tạo thành công, đang xử lý thanh toán...");
      await refreshBookings();
      closeModal("quickCheckoutModal");
      changeView(currentView);
      state.selectedSlots = [];
      updateSelectionBar();
    }
  } catch (err) {
    console.error("[submitQuickCheckout] Error:", err);
    alert("Không đặt được sân: " + err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = originalText;
  }
}

function openSelectionModal() {
  const modal = document.getElementById("selectionModal");
  if (!modal) return;
  const select = document.getElementById("facility-select");
  const dateInput = document.getElementById("facility-date");
  if (select) {
    select.innerHTML = state.facilities
      .map((f) => `<option value="${f.facility_id || f.id}">${f.name}</option>`)
      .join("");
    if (state.selectedFacilityId) select.value = state.selectedFacilityId;
  }
  if (dateInput) {
    dateInput.value = state.selectedDate || new Date().toISOString().split("T")[0];
  }
  modal.classList.add("show");
}

function confirmSelection() {
  const facilityId = parseInt(document.getElementById("facility-select")?.value || "", 10);
  const dateStr = document.getElementById("facility-date")?.value;
  if (!facilityId || !dateStr) {
    alert("Vui lòng chọn cơ sở và ngày.");
    return;
  }
  setSelection(facilityId, dateStr);
  document.getElementById("selectionModal")?.classList.remove("show");
  refreshBookings().then(() => changeView(currentView));
}

async function refreshCourts() {
  try {
    state.courts = (await window.api.court.list()).map(mapCourt);
  } catch (err) {
    console.error(err);
    showToast("Không tải được danh sách sân");
  }
}

async function refreshFacilities() {
  try {
    state.facilities = await window.api.facility.list();
  } catch (err) {
    console.error(err);
    showToast("Không tải được danh sách cơ sở");
  }
}

async function refreshBookings(options = {}) {
  const { forceRefresh = false } = options;
  try {
    const data = await window.api.booking.list({}, { forceRefresh });
    state.bookings = data.map(normalizeBooking);
  } catch (err) {
    console.error(err);
    showToast("Không tải được lịch đặt");
  }
}
window.refreshBookings = refreshBookings;

async function reloadBookingsForSelection(options = {}) {
  const { forceRefresh = false } = options;
  await refreshBookings({ forceRefresh });
  if (currentView === "booking") {
    if (typeof window.renderBookingGrid === "function") {
      window.renderBookingGrid();
    } else {
      renderBooking();
    }
  }
}
window.reloadBookingsForSelection = reloadBookingsForSelection;

async function bootstrapCustomerView() {
  const auth = getAuthOrRedirect();
  if (!auth) return;
  state.userProfile = buildProfileFromAuth(auth.user);
  const adminNav = document.querySelector('[data-view="admin"]')?.parentElement;
  if (adminNav && state.userProfile.rank !== "Quản lý") {
    adminNav.style.display = "none";
  }
  setAvatarInitials(state.userProfile.name);
  await Promise.all([refreshFacilities(), refreshCourts(), refreshBookings()]);
  if (!state.selectedFacilityId && state.facilities.length) {
    setSelection(state.facilities[0].facility_id || state.facilities[0].id, state.selectedDate || new Date().toISOString().split("T")[0]);
  }
  if (!state.selectedDate) {
    setSelection(state.selectedFacilityId, new Date().toISOString().split("T")[0]);
  }
  const defaultView = state.userProfile.rank === "Quản lý" ? "admin" : "booking";
  changeView(defaultView);
  if (!state.selectedFacilityId || !state.selectedDate || SHOULD_PROMPT_SELECTION) {
    openSelectionModal();
  }
}

function changeView(viewName) {
  currentView = viewName;
  document.querySelectorAll(".nav-link").forEach((link) => link.classList.remove("active"));
  const activeLink = document.querySelector(`[data-view="${viewName}"]`);
  if (activeLink) activeLink.classList.add("active");

  dynamicContent.innerHTML = "";

  if (viewName === "dashboard") {
    pageTitle.innerText = "Dashboard khách hàng";
    renderDashboard();
  } else if (viewName === "profile") {
    pageTitle.innerText = "Hồ sơ";
    renderProfile();
  } else if (viewName === "booking") {
    pageTitle.innerText = "Đặt sân theo giờ";
    renderBooking();
  } else if (viewName === "admin") {
    pageTitle.innerText = "Quản lý";
    renderManager();
  } else {
    pageTitle.innerText = "Dashboard khách hàng";
    renderDashboard();
  }
}

function renderDashboard() {
  const dashboardHtml = `
    <div class="dashboard-shell">
      <div class="hero-panel">
        <div>
          <p class="eyebrow">Tổng quan</p>
          <h2 class="hero-title">Điều phối sân</h2>
          <p class="muted">Theo dõi trạng thái sân và xử lý nhanh các phiên đặt.</p>
        </div>
        <div class="hero-selection">
          <div class="muted">Cơ sở & ngày</div>
          <div class="selection-line">${getFacilityName(state.selectedFacilityId)} · ${state.selectedDate || new Date().toISOString().split("T")[0]}</div>
          <button class="btn-outline" onclick="openSelectionModal()">Đổi lựa chọn</button>
        </div>
      </div>

      <div class="stat-row" id="stat-row"></div>

      <div class="filter-bar" id="filter-container">
        <button class="filter-chip active" data-filter="all"><i class="fa-solid fa-layer-group"></i> Tất cả</button>
        <button class="filter-chip" data-filter="blank"><i class="fa-regular fa-circle"></i> Sân trống</button>
        <button class="filter-chip" data-filter="active"><i class="fa-solid fa-circle-check"></i> Đã xác nhận</button>
        <button class="filter-chip" data-filter="booked"><i class="fa-regular fa-credit-card"></i> Chờ thanh toán</button>
      </div>

      <div class="court-grid court-grid-modern" id="court-grid-dashboard"></div>
    </div>
  `;
  dynamicContent.innerHTML = dashboardHtml;

  const renderStats = () => {
    const filteredCourts = state.selectedFacilityId
      ? state.courts.filter((c) => c.facilityId === state.selectedFacilityId)
      : state.courts;
    const counts = {
      total: filteredCourts.length,
      blank: 0,
      active: 0,
      booked: 0,
    };
    filteredCourts.forEach((c) => {
      const booking = state.bookings.find(
        (b) =>
          b.courtId === c.id &&
          (b.facilityId ? b.facilityId === c.facilityId : true) &&
          (!state.selectedDate || (b.start && isSameDate(new Date(state.selectedDate), b.start.toISOString()))) &&
          !["cancelled", "expired"].includes(b.uiStatus)
      );
      if (!booking) counts.blank += 1;
      else if (booking.uiStatus === "active") counts.active += 1;
      else counts.booked += 1;
    });
    document.getElementById("stat-row").innerHTML = `
      <div class="stat-card">
        <div class="stat-icon soft"><i class="fa-solid fa-layer-group"></i></div>
        <div>
          <div class="stat-label">Tổng số sân</div>
          <div class="stat-value">${counts.total}</div>
          <div class="stat-hint">Đang quản lý</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success"><i class="fa-solid fa-circle-check"></i></div>
        <div>
          <div class="stat-label">Sân trống</div>
          <div class="stat-value">${counts.blank}</div>
          <div class="stat-hint">Sẵn sàng nhận đặt</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon info"><i class="fa-solid fa-ticket-simple"></i></div>
        <div>
          <div class="stat-label">Đã xác nhận</div>
          <div class="stat-value">${counts.active}</div>
          <div class="stat-hint">Đã thanh toán / giữ slot</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning"><i class="fa-regular fa-credit-card"></i></div>
        <div>
          <div class="stat-label">Chờ thanh toán</div>
          <div class="stat-value">${counts.booked}</div>
          <div class="stat-hint">Cần nhắc khách thanh toán</div>
        </div>
      </div>
    `;
  };

  const renderCourtCards = (filter = "all") => {
    const grid = document.getElementById("court-grid-dashboard");
    grid.innerHTML = "";

    const filteredCourts = state.selectedFacilityId
      ? state.courts.filter((c) => c.facilityId === state.selectedFacilityId)
      : state.courts;

    const combinedCourts = filteredCourts.map((c) => {
      const booking = state.bookings.find(
        (b) =>
          b.courtId === c.id &&
          (b.facilityId ? b.facilityId === c.facilityId : true) &&
          (!state.selectedDate || (b.start && isSameDate(new Date(state.selectedDate), b.start.toISOString()))) &&
          !["cancelled", "expired"].includes(b.uiStatus)
      );
      return { ...c, booking, status: booking ? booking.uiStatus : "blank" };
    });

    combinedCourts
      .filter((c) => filter === "all" || c.status === filter)
      .forEach((c) => {
        const style = getStatusStyle(c.status);
        let content = "";

        if (c.booking) {
          content = `
            <div class="court-card-meta">
              <span><i class="fa-solid fa-user"></i> ${c.booking.customer}</span>
              <span><i class="fa-regular fa-clock"></i> ${c.booking.startHour || "--"}:00</span>
            </div>
            <div class="court-card-price">${formatCurrency(c.booking.total)}</div>
            <div class="court-card-actions">
              <button class="btn-outline" onclick="openCheckoutModal(${c.booking.id})">Chi tiết</button>
            </div>`;
        } else {
          content = `
            <div class="card-content-empty-modern">
              <div class="empty-icon"><i class="fa-solid fa-plus"></i></div>
              <div class="empty-text">Sân trống</div>
            </div>
            <div class="court-card-actions">
              <button class="btn-primary" onclick="openBookingModal(${c.id})">Đặt ngay</button>
            </div>`;
        }

        grid.innerHTML += `
          <div class="card court-card ${c.status}">
            <div class="status-strip" style="background:${style.border};"></div>
            <div class="card-header-simple">
              <div>
                <div class="court-name">${c.name}</div>
                <div class="court-type">${c.type}</div>
              </div>
              <div class="badge modern" style="color:${style.text};background:${style.bg};border:1px solid ${style.border};">${style.label}</div>
            </div>
            <div class="card-body">${content}</div>
          </div>`;
      });
    renderStats();
  };

  document.querySelectorAll("#filter-container .filter-chip").forEach((btn) => {
    btn.addEventListener("click", function () {
      document.querySelectorAll("#filter-container .filter-chip").forEach((b) => b.classList.remove("active"));
      this.classList.add("active");
      renderCourtCards(this.getAttribute("data-filter"));
    });
  });

  renderCourtCards();
}

function renderProfile() {
  const profileHtml = `
        <div class="profile-grid">
            <div class="card profile-card">
                <div class="card-header-simple">
                    <h3>Thông tin cá nhân</h3>
                    <button class="btn-icon" onclick="openEditModal()"><i class="fa-solid fa-pen-to-square"></i></button>
                </div>
                <div class="profile-details">
                    <div class="profile-avatar-large">${(state.userProfile.name[0] || "K").toUpperCase()}</div>
                    <h2 id="user-name">${state.userProfile.name}</h2>
                    <p id="user-rank" class="rank-badge">${state.userProfile.rank}</p>
                    <div class="detail-row"><i class="fa-solid fa-phone"></i> <span id="user-phone">${state.userProfile.phone}</span></div>
                    <div class="detail-row"><i class="fa-solid fa-envelope"></i> <span id="user-email">${state.userProfile.email}</span></div>
                </div>
            </div>
        </div>

        <div class="history-section">
            <h3>Lịch sử thanh toán</h3>
            <p style="color:#94a3b8;margin-top:8px;">Tính năng thanh toán trực tuyến hiện đã được vô hiệu hóa.</p>
        </div>
    `;
  dynamicContent.innerHTML = profileHtml;
}

function openEditModal() {
  document.getElementById("edit-name").value = state.userProfile.name;
  document.getElementById("edit-phone").value = state.userProfile.phone;
  document.getElementById("edit-email").value = state.userProfile.email;
  document.getElementById("editModal").classList.add("show");
}

function saveProfile() {
  state.userProfile.name = document.getElementById("edit-name").value;
  state.userProfile.phone = document.getElementById("edit-phone").value;
  state.userProfile.email = document.getElementById("edit-email").value;
  renderProfile();
  closeModal("editModal");
  showToast("Cập nhật hồ sơ thành công!");
}

function renderBooking() {
  let hasAutoScrolled = false;
  const slots = Array.from({ length: ((END_HOUR - START_HOUR) * 60) / SLOT_STEP_MINUTES }, (_, i) => START_HOUR * 60 + i * SLOT_STEP_MINUTES);
  const today = new Date();
  const defaultDate = today.toISOString().split("T")[0];
  const activeDate = state.selectedDate || defaultDate;
  const columnStyle = `style="grid-template-columns: repeat(${slots.length}, 140px);"`;

  const bookingHtml = `
    <section class="booking-shell">
      <div class="booking-header-hero">
        <div class="hero-left">
          <p class="eyebrow">Đặt sân theo giờ</p>
          <h1 class="page-hero">Đặt sân Badminton</h1>
          <a class="guide-link" href="#">Xem giá, hướng dẫn</a>
        </div>
        <div class="hero-center">
          <label class="date-label">Chọn ngày</label>
          <div class="date-input-pill">
            <input type="date" id="booking-date" value="${activeDate}" />
          </div>
        </div>
        <div class="hero-right">
          <div class="hotline-card muted-card">Thông tin liên hệ sẽ cập nhật</div>
        </div>
      </div>

      <div class="facility-strip">
        ${
          state.facilities.length
            ? state.facilities
                .map(
                  (f) => `
          <label class="facility-chip">
            <input type="radio" name="facility-radio" value="${f.facility_id || f.id}" ${
                    f.facility_id === state.selectedFacilityId || f.id === state.selectedFacilityId ? "checked" : ""
                  } />
            <span class="facility-bullet"></span>
            <span class="facility-name">${f.name}</span>
          </label>`
                )
                .join("")
            : "<div class='muted'>Chưa có danh sách cơ sở</div>"
        }
      </div>

      <div class="booking-legend">
        <div class="legend-item"><span class="legend-box blank"></span>Trống</div>
        <div class="legend-item"><span class="legend-box booked"></span>Đã đặt</div>
        <div class="legend-item"><span class="legend-box active"></span>Đang chọn</div>
        <div class="legend-item"><span class="legend-box pass"></span>Cần Pass</div>
      </div>

      <div class="schedule-panel">
        <div class="corner-cell">Sân</div>
        <div class="time-row">
          <div class="time-track" ${columnStyle}>
            ${slots.map((m) => `<div class="time-cell">${formatSlotRangeLabel(m)}</div>`).join("")}
          </div>
        </div>
        <div class="court-list" id="court-list"></div>
        <div class="timeline-body-grid" id="timeline-body-grid"></div>
      </div>

      <div class="selection-bar bright">
        <div class="selection-info">
          <div class="label">Đang chọn:</div>
          <div class="value" id="selection-text">Chưa chọn</div>
        </div>
        <div class="selection-total">Tổng: <span id="selection-total">0 đ</span></div>
        <button class="btn-primary" id="btn-next" disabled>Tiếp theo</button>
      </div>
    </section>
  `;
  dynamicContent.innerHTML = bookingHtml;

  document.getElementById("btn-next").onclick = () => {
    if (state.selectedSlots.length) {
      openQuickCheckout();
    }
  };

  const renderGrid = () => {
    const selectedDate = document.getElementById("booking-date")?.value || state.selectedDate;
    const filteredBookings = state.bookings.filter(
      (b) =>
        (!state.selectedFacilityId || !b.facilityId || b.facilityId === state.selectedFacilityId) &&
        (!selectedDate || (b.start && isSameDate(b.start, selectedDate)))
    );
    const courts = state.courts.filter((c) => !state.selectedFacilityId || c.facilityId === state.selectedFacilityId);
    const slots = Array.from({ length: ((END_HOUR - START_HOUR) * 60) / SLOT_STEP_MINUTES }, (_, i) => START_HOUR * 60 + i * SLOT_STEP_MINUTES);
    const body = document.getElementById("timeline-body-grid");
    const courtList = document.getElementById("court-list");
    if (!body) return;
    if (courtList) {
      courtList.innerHTML = courts
        .map(
          (c) => `
          <div class="court-item">
            <div class="court-code">${getFacilityCode(state.selectedFacilityId)}</div>
            <div class="court-name">${c.name}</div>
          </div>`
        )
        .join("");
    }

    body.innerHTML = courts
      .map((c) => {
        const cells = slots
          .map((m) => {
            const h = Math.floor(m / 60);
            const mm = m % 60;
            const start = new Date(selectedDate || new Date().toISOString().split("T")[0]);
            start.setHours(h, mm, 0, 0);
            const booking = filteredBookings.find((b) => b.courtId === c.id && b.start && b.end && b.start <= start && b.end > start);
            let status = "blank";
            if (booking) status = "booked";
            if (isSlotSelected(c.id, start)) status = "active";
            return `<div class="timeline-cell ${status}" data-court="${c.id}" data-start="${start.toISOString()}"></div>`;
          })
          .join("");
        return `<div class="timeline-row">
          <div class="timeline-cells" ${columnStyle}>${cells}</div>
        </div>`;
      })
      .join("");

    if (!hasAutoScrolled) {
      const schedule = document.querySelector(".schedule-panel");
      if (schedule) {
        const slotWidth = 140;
        const offsetHour = Math.max(0, DEFAULT_VIEW_HOUR - START_HOUR);
        schedule.scrollLeft = offsetHour * slotWidth;
      }
      hasAutoScrolled = true;
    }
  };

  document.getElementById("booking-date")?.addEventListener("change", (e) => {
    setSelection(state.selectedFacilityId, e.target.value);
    renderGrid();
    updateSelectionBar();
  });

  document.querySelectorAll('input[name="facility-radio"]').forEach((radio) => {
    radio.addEventListener("change", (e) => {
      const facilityId = parseInt(e.target.value, 10);
      setSelection(facilityId, document.getElementById("booking-date")?.value || state.selectedDate);
      refreshBookings().then(() => renderBooking());
    });
  });

  document.getElementById("timeline-body-grid")?.addEventListener("click", (e) => {
    const cell = e.target.closest(".timeline-cell");
    if (!cell) return;
    if (cell.classList.contains("booked")) return;
    const courtId = parseInt(cell.dataset.court, 10);
    const start = new Date(cell.dataset.start);
    toggleSelectedSlot(courtId, start);
    renderGrid();
  });

  renderGrid();
  updateSelectionBar();
  window.renderBookingGrid = renderGrid;
}

function renderManager() {
  const today = new Date();
  const activeDate = state.selectedDate || today.toISOString().split("T")[0];

  const managerHtml = `
    <div class="dashboard-shell">
      <div class="hero-panel">
        <div>
          <p class="eyebrow">Quản lý</p>
          <h2 class="hero-title">Điều phối cơ sở</h2>
          <p class="muted">Quản lý sân, booking, và xem báo cáo doanh thu.</p>
        </div>
        <div class="hero-selection">
          <div class="muted">Cơ sở quản lý</div>
          <select id="manager-facility-select" class="manager-facility-select">
            <option value="">Đang tải...</option>
          </select>
          <div class="muted" style="margin-top:8px;">Ngày hiện tại</div>
          <div class="selection-line" id="manager-date-display">${activeDate}</div>
          <input type="date" id="manager-date-picker" value="${activeDate}" style="margin-top:8px;" />
        </div>
      </div>

      <!-- Tab Navigation -->
      <div class="tab-navigation" id="manager-tabs">
        <button class="tab-button active" data-tab="courts">
          <i class="fa-solid fa-map-pin"></i> Danh Sách Sân
        </button>
        <button class="tab-button" data-tab="bookings">
          <i class="fa-solid fa-calendar-check"></i> Quản Lý Booking
        </button>
        <button class="tab-button" data-tab="reports">
          <i class="fa-solid fa-chart-line"></i> Báo Cáo
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Courts Tab -->
        <div id="tab-courts" class="tab-pane active">
          <div id="courts-stats"></div>
          <div id="courts-list"></div>
        </div>

        <!-- Bookings Tab -->
        <div id="tab-bookings" class="tab-pane">
          <div id="bookings-header"></div>
          <div id="bookings-walkin-form"></div>
          <div id="bookings-list"></div>
        </div>

        <!-- Reports Tab -->
        <div id="tab-reports" class="tab-pane">
          <div id="reports-filter"></div>
          <div id="report-container"></div>
        </div>
      </div>
    </div>
  `;

  dynamicContent.innerHTML = managerHtml;

  setupManagerTabs();

  initManagerContext();
}

function setupManagerTabs() {
  const tabButtons = document.querySelectorAll("#manager-tabs .tab-button");
  const tabPanes = document.querySelectorAll(".tab-pane");

  console.log("[setupManagerTabs] Found", tabButtons.length, "buttons and", tabPanes.length, "panes");

  tabButtons.forEach(button => {
    button.addEventListener("click", () => {
      const tabName = button.getAttribute("data-tab");
      console.log("[setupManagerTabs] Switching to tab:", tabName);

      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      button.classList.add("active");
      const targetPane = document.getElementById(`tab-${tabName}`);
      if (targetPane) {
        targetPane.classList.add("active");
        console.log("[setupManagerTabs] Activated pane:", `tab-${tabName}`);
      } else {
        console.error("[setupManagerTabs] Target pane not found:", `tab-${tabName}`);
      }
    });
  });

  document.getElementById("manager-date-picker")?.addEventListener("change", (e) => {
    const newDate = e.target.value;
    setManagerSelection(state.managerFacilityId, newDate);
    refreshManagerView(newDate);
  });
}

function getManagerActiveDate() {
  return state.managerDate || state.selectedDate || new Date().toISOString().split("T")[0];
}

function updateManagerDateUI(dateStr) {
  const display = document.getElementById("manager-date-display");
  if (display) display.innerText = dateStr;
  const picker = document.getElementById("manager-date-picker");
  if (picker) picker.value = dateStr;
}

function setManagerSelection(facilityId, dateStr) {
  const nextDate = dateStr || getManagerActiveDate();
  if (facilityId) {
    state.managerFacilityId = facilityId;
  }
  if (nextDate) {
    state.managerDate = nextDate;
  }
  if (state.managerFacilityId && nextDate) {
    setSelection(state.managerFacilityId, nextDate);
  }
  updateManagerDateUI(nextDate);
}

function renderManagerFacilityOptions() {
  const select = document.getElementById("manager-facility-select");
  if (!select) return;
  if (!state.managerFacilities.length) {
    select.innerHTML = `<option value="">Không có cơ sở</option>`;
    select.disabled = true;
    return;
  }
  select.innerHTML = state.managerFacilities
    .map(
      (facility) => `<option value="${facility.facility_id}">${facility.name || `Cơ sở #${facility.facility_id}`}</option>`
    )
    .join("");
  select.value = state.managerFacilityId || state.managerFacilities[0].facility_id;
  select.disabled = false;
}

function showManagerLoadError(message) {
  const errorHtml = `<div class="error-message">${message}</div>`;
  const statsContainer = document.getElementById("courts-stats");
  if (statsContainer) statsContainer.innerHTML = "";
  const courtsContainer = document.getElementById("courts-list");
  if (courtsContainer) courtsContainer.innerHTML = errorHtml;
  const bookingsContainer = document.getElementById("bookings-list");
  if (bookingsContainer) bookingsContainer.innerHTML = errorHtml;
  const headerContainer = document.getElementById("bookings-header");
  if (headerContainer) headerContainer.innerHTML = "";
  const reportContainer = document.getElementById("report-container");
  if (reportContainer) reportContainer.innerHTML = errorHtml;
  const filterContainer = document.getElementById("reports-filter");
  if (filterContainer) filterContainer.innerHTML = "";
}

async function initManagerContext() {
  try {
    const rawFacilities = await window.api.facility.managerList();
    console.log("[initManagerContext] Raw facilities response:", rawFacilities);
    
    // Handle both array and object responses
    let facilitiesArray = [];
    if (Array.isArray(rawFacilities)) {
      facilitiesArray = rawFacilities;
    } else if (rawFacilities && typeof rawFacilities === 'object') {
      // If it's an object, try to extract array from common property names
      facilitiesArray = rawFacilities.data || rawFacilities.facilities || rawFacilities.items || [];
    }
    
    console.log("[initManagerContext] Facilities array:", facilitiesArray);
    
    state.managerFacilities = (facilitiesArray || [])
      .map((facility) => {
        const id = Number(facility.facility_id || facility.id || facility.facilityId);
        return {
          facility_id: Number.isFinite(id) ? id : null,
          name: facility.name || facility.title || `Cơ sở #${facility.facility_id || facility.id || id || "?"}`,
        };
      })
      .filter((facility) => facility.facility_id);

    console.log("[initManagerContext] Manager facilities:", state.managerFacilities);
    
    if (!state.managerFacilities || !state.managerFacilities.length) {
      showManagerLoadError("Bạn chưa được gán cơ sở nào hoặc phiên đăng nhập đã hết hạn.");
      return;
    }
    if (!state.managerFacilityId) {
      state.managerFacilityId = state.managerFacilities[0].facility_id;
    }
    if (!state.managerDate) {
      state.managerDate = state.selectedDate || new Date().toISOString().split("T")[0];
    }

    renderManagerFacilityOptions();

    const facilitySelect = document.getElementById("manager-facility-select");
    if (facilitySelect) {
      facilitySelect.onchange = async (event) => {
        const nextId = parseInt(event.target.value, 10);
        console.log("[facilitySelect.onchange] Selected facility ID:", nextId);
        if (Number.isNaN(nextId)) return;
        setManagerSelection(nextId, state.managerDate);
        try {
          await refreshManagerView();
        } catch (err) {
          console.error("[facilitySelect.onchange] Error refreshing view:", err);
          showManagerLoadError(`Không tải được dữ liệu: ${err.message}`);
        }
      };
    }

    setManagerSelection(state.managerFacilityId, state.managerDate);
    await refreshManagerView();
  } catch (err) {
    console.error("[initManagerContext] Error:", err);
    showManagerLoadError(`Không tải được cơ sở: ${err.message}`);
  }
}

async function refreshManagerView(dateOverride) {
  const facilityId = state.managerFacilityId;
  console.log("[refreshManagerView] Called with facilityId:", facilityId, "dateOverride:", dateOverride);
  
  if (!facilityId) {
    showManagerLoadError("Vui lòng chọn cơ sở để xem dữ liệu.");
    return { bookings: [], courts: [] };
  }

  const dateStr = dateOverride || getManagerActiveDate();
  setManagerSelection(facilityId, dateStr);
  
  console.log("[refreshManagerView] Loading data for facility:", facilityId, "date:", dateStr);

  try {
    const [courtsData, bookingsData] = await Promise.all([
      window.api.court.listByFacility(facilityId),
      window.api.booking.managerList(facilityId, dateStr),
    ]);
    
    console.log("[refreshManagerView] Courts data:", courtsData, "isArray:", Array.isArray(courtsData));
    console.log("[refreshManagerView] Bookings data:", bookingsData, "isArray:", Array.isArray(bookingsData));
    
    // Ensure we have arrays
    const courtsArray = Array.isArray(courtsData) ? courtsData : (courtsData?.data || []);
    const bookingsArray = Array.isArray(bookingsData) ? bookingsData : (bookingsData?.data || []);
    
    const courts = courtsArray.map(mapCourt);
    const bookings = bookingsArray.map(normalizeBooking);

    const statsHtml = window.ManagerCourts.renderCourtsStats(courts, bookings);
    const statsContainer = document.getElementById("courts-stats");
    if (statsContainer) statsContainer.innerHTML = statsHtml;

    const courtsContainer = document.getElementById("courts-list");
    if (courtsContainer) {
      const courtsHtml = window.ManagerCourts.renderCourtsSection(courts, bookings, dateStr);
      courtsContainer.innerHTML = courtsHtml;
      console.log("[refreshManagerView] Courts HTML updated, length:", courtsHtml.length);
    } else {
      console.error("[refreshManagerView] courts-list container not found!");
    }

    const headerContainer = document.getElementById("bookings-header");
    if (headerContainer) {
      headerContainer.innerHTML = `
        <div class="card" style="margin-bottom: 20px;">
          <h4>Booking hôm: ${formatDateVi(new Date(dateStr))}</h4>
          <p class="muted">Tổng: ${bookings.length} booking</p>
        </div>
      `;
    }

    const walkinContainer = document.getElementById("bookings-walkin-form");
    if (walkinContainer) {
      try {
        console.log("[refreshManagerView] Rendering walk-in form with", courts.length, "courts");
        walkinContainer.innerHTML = window.ManagerBooking.renderWalkInForm(courts);
      } catch (err) {
        console.error("[refreshManagerView] Error rendering walk-in form:", err);
        walkinContainer.innerHTML = `<div class="error-message">Lỗi hiển thị form walk-in: ${err.message}</div>`;
      }
    }

    const bookingsContainer = document.getElementById("bookings-list");
    if (bookingsContainer) {
      try {
        console.log("[refreshManagerView] Rendering booking table with", bookings.length, "bookings");
        const tableHtml = window.ManagerBooking.renderBookingTable(bookings, courts);
        bookingsContainer.innerHTML = tableHtml;
        console.log("[refreshManagerView] Booking table HTML length:", tableHtml.length, "Container innerHTML length:", bookingsContainer.innerHTML.length);
      } catch (err) {
        console.error("[refreshManagerView] Error rendering booking table:", err);
        bookingsContainer.innerHTML = `<div class="error-message">Lỗi hiển thị bảng booking: ${err.message}</div>`;
      }
    } else {
      console.error("[refreshManagerView] bookings-list container not found!");
    }

    window.refreshManagerBookings = () => refreshManagerView();
    window.refreshManagerView = refreshManagerView;

    try {
      console.log("[refreshManagerView] Loading manager report");
      await loadManagerReport(bookings, courts);
    } catch (err) {
      console.error("[refreshManagerView] Error loading report:", err);
      const reportContainer = document.getElementById("report-container");
      if (reportContainer) {
        reportContainer.innerHTML = `<div class="error-message">Lỗi tải báo cáo: ${err.message}</div>`;
      }
    }

    return { bookings, courts };
  } catch (err) {
    console.error("[refreshManagerView] Error:", err);
    showManagerLoadError(`Không tải được dữ liệu quản lý: ${err.message}`);
    return { bookings: [], courts: [] };
  }
}

async function loadManagerReport(preloadedBookings = null, preloadedCourts = null) {
  const facilityId = state.managerFacilityId;
  const today = new Date();
  const startDate = new Date(today);
  startDate.setDate(today.getDate() - 7);
  const startDateStr = startDate.toISOString().split("T")[0];
  const endDateStr = today.toISOString().split("T")[0];

  const filterContainer = document.getElementById("reports-filter");
  if (filterContainer) {
    filterContainer.innerHTML = window.ManagerReport.renderDateRangeFilter(startDateStr, endDateStr);
  }

  if (!facilityId) {
    showManagerLoadError("Vui lòng chọn cơ sở để xem báo cáo.");
    return;
  }

  try {
    const bookingsData = preloadedBookings || (await window.api.booking.managerList(facilityId));
    const courtsData = preloadedCourts || (await window.api.court.listByFacility(facilityId));
    const bookings = (bookingsData || []).map(normalizeBooking);
    const courts = (courtsData || []).map(mapCourt);

    // Render usage stats (new feature)
    const usageStatsHtml = window.ManagerReportCharts?.renderUsageStats(bookings, courts) || '';
    
    // Render revenue table
    const reportData = window.ManagerReport.calculateRevenueByCourtId(bookings, courts, startDateStr, endDateStr);
    const dateRange = `${formatDateVi(startDate)} - ${formatDateVi(today)}`;
    const reportHtml = window.ManagerReport.renderReportTable(reportData, dateRange);
    
    // Render playtime charts (new feature - async!)
    let chartsHtml = '';
    if (window.ManagerReportCharts?.renderPlaytimeCharts) {
      try {
        chartsHtml = await window.ManagerReportCharts.renderPlaytimeCharts(courts);
      } catch (chartErr) {
        console.error("[loadManagerReport] Error rendering charts:", chartErr);
        chartsHtml = `<div class="error-message">Lỗi load charts: ${chartErr.message}</div>`;
      }
    }
    
    const reportContainer = document.getElementById("report-container");
    if (reportContainer) {
      reportContainer.innerHTML = usageStatsHtml + reportHtml + chartsHtml;
    }
  } catch (err) {
    console.error("[loadManagerReport] Error:", err);
    const reportContainer = document.getElementById("report-container");
    if (reportContainer) {
      reportContainer.innerHTML = `<div class="error-message">Lỗi load report: ${err.message}</div>`;
    }
  }
}

async function confirmBooking() {
  const auth = getAuthOrRedirect();
  if (!auth) return;

  const name = document.getElementById("b-name").value;
  const courtId = parseInt(document.getElementById("b-court").value, 10);
  const hourStr = document.getElementById("b-hour")?.value || "08";
  const minuteStr = document.getElementById("b-minute")?.value || "00";
  const endHourStr = document.getElementById("b-end-hour")?.value || "09";
  const endMinuteStr = document.getElementById("b-end-minute")?.value || "00";
  const dateStr = document.getElementById("b-date")?.value;

  if (!name || hourStr === "" || !dateStr) {
    alert("Vui lòng nhập đủ thông tin");
    return;
  }
  if (!state.selectedFacilityId) {
    openSelectionModal();
    return;
  }

  const start = new Date(dateStr);
  const hour = parseInt(hourStr, 10);
  const minute = parseInt(minuteStr, 10);
  start.setHours(hour, minute, 0, 0);
  const end = new Date(dateStr);
  end.setHours(parseInt(endHourStr, 10), parseInt(endMinuteStr, 10), 0, 0);

  if (end <= start) {
    alert("Giờ kết thúc phải sau giờ bắt đầu.");
    return;
  }

  const duration = (end.getTime() - start.getTime()) / (1000 * 60 * 60);

  const payload = {
    facility_id: state.selectedFacilityId,
    items:
      state.selectedSlots.length > 0
        ? state.selectedSlots.map((slot) => ({
            court_id: slot.courtId,
            start_time: slot.start.toISOString(),
            end_time: slot.end.toISOString(),
            price: getCourtHourlyRate(slot.courtId),
          }))
        : [
            {
              court_id: courtId,
              start_time: start.toISOString(),
              end_time: end.toISOString(),
              price: duration * getCourtHourlyRate(courtId),
            },
          ],
    note: `Khách: ${name}`,
  };

  try {
    await window.api.booking.create(payload);
    await refreshBookings();
    closeModal("bookingModal");
    changeView(currentView);
    state.selectedSlots = [];
    updateSelectionBar();
    showToast("Đã tạo lịch đặt sân thành công.");
  } catch (err) {
    console.error(err);
    alert("Không đặt được sân: " + err.message);
  }
}

function populateHourOptions(selectEl, defaultHour = null) {
  if (!selectEl) return;
  selectEl.innerHTML = Array.from({ length: 24 }, (_, h) => {
    const hh = String(h).padStart(2, "0");
    const selected = defaultHour === h ? "selected" : "";
    return `<option value="${hh}" ${selected}>${hh}:00</option>`;
  }).join("");
}

function openBookingModal(courtId = null, startTime = null) {
  return;
}

function openCheckoutModal(bookingId) {
  const booking = state.bookings.find((b) => b.id === bookingId);
  if (!booking) return;
  document.getElementById("c-customer").innerText = booking.customer;
  document.getElementById("c-court-name").innerText = getCourtName(booking.courtId);
  document.getElementById("c-time-detail").innerText = booking.start
    ? `${booking.start.getHours()}:${booking.start.getMinutes().toString().padStart(2, "0")}`
    : "--";
  document.getElementById("c-duration-detail").innerText = booking.duration || "--";
  const statusTag = document.getElementById("c-status");
  const style = getStatusStyle(booking.uiStatus);
  statusTag.innerText = style.label;
  statusTag.style.background = style.bg;
  statusTag.style.color = style.text;

  document.getElementById("c-price").innerText = formatCurrency(booking.total);
  document.getElementById("c-total").innerText = formatCurrency(booking.total);

  const actionDiv = document.getElementById("action-buttons");
  actionDiv.innerHTML = "";
  if (["booked", "active"].includes(booking.uiStatus)) {
    actionDiv.innerHTML += `<button class="btn-cancel" onclick="cancelBooking(${booking.id})">Hủy đặt</button>`;
  } else {
    actionDiv.innerHTML += `<div style="color:#6b7280;">Không có hành động khả dụng</div>`;
  }

  document.getElementById("checkoutModal").classList.add("show");
}

async function cancelBooking(id) {
  showConfirmDialog("Bạn chắc chắn muốn hủy lịch này?", async () => {
    try {
      await window.api.booking.cancel(id, { reason: "Khách hàng hủy" });
      await refreshBookings();
      closeModal("checkoutModal");
      changeView(currentView);
      showToast("Đã hủy lịch đặt sân");
    } catch (err) {
      console.error(err);
      alert("Không hủy được lịch: " + err.message);
    }
  });
}

async function handlePaymentReturn() {
  try {
    const returnData = await window.PaymentHandler.handlePaymentReturn();
    if (!returnData) return;
    console.log("[handlePaymentReturn] Result:", returnData);

    if (returnData.success) {
      showToast(returnData.message || "Thanh toán thành công! Ô sân đã được cập nhật.");
      if (currentView !== "booking") {
        changeView("booking");
      } else {
        window.renderBookingGrid?.();
      }
      window.scrollTo(0, 0);
    } else {
      showToast(returnData.message || "Thanh toán thất bại. Vui lòng thử lại.");
    }
  } catch (err) {
    console.error("[handlePaymentReturn] Error:", err);
    showToast("Không thể xác nhận thanh toán. Vui lòng thử lại sau.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const view = this.getAttribute("data-view");
      changeView(view);
    });
  });

  const logoutBtn = document.querySelector(".logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      window.api.clearAuth();
      window.api.auth.redirectToLogin();
    });
  }

  bootstrapCustomerView()
    .then(() => handlePaymentReturn())
    .catch((err) => {
      console.error("[bootstrapCustomerView] Error:", err);
    });
});
