// ===================================
// SHARED UTILITIES & CONSTANTS
// ===================================

const START_HOUR = 0;
const END_HOUR = 24;
const DEFAULT_VIEW_HOUR = 8;
const HOURLY_RATE = 50000;
const SAVED_FACILITY = parseInt(localStorage.getItem("soa_facility_id") || "", 10) || null;
const TODAY = new Date().toISOString().split("T")[0];
const MAX_BOOKING_DATE = new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0];
const SAVED_DATE = localStorage.getItem("soa_booking_date") || TODAY;
const SHOULD_PROMPT_SELECTION = !SAVED_FACILITY;
const SLOT_STEP_MINUTES = 60;
const MAX_SLOTS_PER_BOOKING = 4;
const MANAGER_SETTINGS_KEY = "manager_court_settings";

// Global state
let state = {
  courts: [],
  bookings: [],
  occupiedBookings: [],
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
const OCCUPIED_SLOTS_CACHE = new Map();

// Expose state to window for access from other modules
window.state = state;

function parseTimeToMinutes(value) {
  if (!value) return null;
  const parts = value.split(":").map((part) => Number(part));
  if (!parts.length) return null;
  const [hour = 0, minute = 0] = parts;
  if (
    !Number.isFinite(hour) ||
    !Number.isFinite(minute) ||
    hour < 0 ||
    hour > 24 ||
    minute < 0 ||
    minute >= 60
  ) {
    return null;
  }
  return hour * 60 + minute;
}

function toPaddedTime(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  const pad = (num) => String(num).padStart(2, "0");
  return `${pad(h)}:${pad(m)}`;
}

function loadManagerSettings() {
  try {
    const raw = localStorage.getItem(MANAGER_SETTINGS_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return typeof parsed === "object" && parsed !== null ? parsed : {};
  } catch (err) {
    console.warn("[SharedUtils] Invalid manager settings payload", err);
    return {};
  }
}

function normalizeSegmentValue(segment) {
  if (!segment) return null;
  const startMinutes = parseTimeToMinutes(segment.start || "");
  const endMinutes = parseTimeToMinutes(segment.end || "");
  const price = Number(segment.price);
  if (
    startMinutes === null ||
    endMinutes === null ||
    endMinutes <= startMinutes ||
    Number.isNaN(price)
  ) {
    return null;
  }
  return {
    startMinutes,
    endMinutes,
    price,
    startLabel: segment.start || toPaddedTime(startMinutes),
    endLabel: segment.end || toPaddedTime(endMinutes),
  };
}

function getManagerSegmentsForCourt(courtId) {
  if (!courtId) return [];
  const settings = loadManagerSettings();
  const entry = settings[courtId] || settings[String(courtId)] || {};
  if (!entry || !Array.isArray(entry.segments)) return [];
  return entry.segments
    .map(normalizeSegmentValue)
    .filter(Boolean)
    .sort((a, b) => a.startMinutes - b.startMinutes);
}

function getSegmentPriceForMinute(courtId, minuteOfDay) {
  if (minuteOfDay === null || minuteOfDay === undefined) return null;
  const segments = getManagerSegmentsForCourt(courtId);
  for (const segment of segments) {
    if (minuteOfDay >= segment.startMinutes && minuteOfDay < segment.endMinutes) {
      return segment.price;
    }
  }
  return null;
}

function getCourtSlotPrice(courtId, startDate) {
  const baseRate = getCourtHourlyRate(courtId);
  if (!startDate) return baseRate;
  const dateObj = startDate instanceof Date ? startDate : new Date(startDate);
  if (Number.isNaN(dateObj.getTime())) return baseRate;
  const minuteOfDay = dateObj.getHours() * 60 + dateObj.getMinutes();
  const override = getSegmentPriceForMinute(courtId, minuteOfDay);
  return override ?? baseRate;
}

// ===================================
// FORMAT UTILITIES
// ===================================

function formatCurrency(amount = 0) {
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(amount);
}

function formatDateVi(dateObj) {
  if (!dateObj) return "--";
  const d = new Date(dateObj);
  return `${String(d.getDate()).padStart(2, "0")}/${String(d.getMonth() + 1).padStart(2, "0")}/${d.getFullYear()}`;
}

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

function toLocalISOString(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
}

function parseBookingDateTime(datetimeStr) {
  if (!datetimeStr) return null;
  // MySQL returns datetime without timezone, treat it as local time
  // Format: "2025-12-06 14:00:00" -> parse as local timezone
  const cleaned = String(datetimeStr).trim().replace(/[TZ]/g, ' ').trim();
  const parts = cleaned.split(/[-\s:]/);
  if (parts.length < 6) return null;
  
  // Create date in local timezone
  const localDate = new Date(
    parseInt(parts[0]), // year
    parseInt(parts[1]) - 1, // month (0-indexed)
    parseInt(parts[2]), // day
    parseInt(parts[3]), // hour
    parseInt(parts[4]), // minute
    parseInt(parts[5]) || 0 // second
  );
  return localDate;
}

// ===================================
// UI UTILITIES
// ===================================

function showToast(msg) {
  const toast = document.getElementById("toast");
  if (!toast) {
    console.warn("Toast element not found");
    return;
  }
  toast.innerText = msg;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

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

function closeModal(id) {
  document.getElementById(id)?.classList.remove("show");
}

// ===================================
// STATUS MAPPING
// ===================================

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

// ===================================
// DATA MAPPING & UTILITIES
// ===================================

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
  if (Array.isArray(raw.items) && raw.items.length > 1) {
    // console.log(`[normalizeBooking] ✓ Multi-item booking ${raw.booking_id}: returning ${raw.items.length} separate slots`);
    return raw.items.map(item => normalizeBookingItem(raw, item));
  }
  const firstItem = raw.items && raw.items.length ? raw.items[0] : null;
  return normalizeBookingItem(raw, firstItem);
}

function normalizeBookingItem(raw, item) {
  let start = null, end = null;
  
  if (item?.start_time) {
    try {
      start = parseBookingDateTime(item.start_time);
      if (!start || isNaN(start.getTime())) start = null;
    } catch (e) {
      console.warn("Invalid start_time:", item.start_time);
      start = null;
    }
  } else if (item?.startTime) {
    try {
      start = parseBookingDateTime(item.startTime);
      if (!start || isNaN(start.getTime())) start = null;
    } catch (e) {
      console.warn("Invalid startTime:", item.startTime);
      start = null;
    }
  }

  if (item?.end_time) {
    try {
      end = parseBookingDateTime(item.end_time);
      if (!end || isNaN(end.getTime())) end = null;
    } catch (e) {
      console.warn("Invalid end_time:", item.end_time);
      end = null;
    }
  } else if (item?.endTime) {
    try {
      end = parseBookingDateTime(item.endTime);
      if (!end || isNaN(end.getTime())) end = null;
    } catch (e) {
      console.warn("Invalid endTime:", item.endTime);
      end = null;
    }
  }

  const duration = start && end ? (end - start) / (1000 * 60 * 60) : null;
  const inferredRate = getCourtSlotPrice(item?.court_id || item?.courtId, start);
  const uiStatus = mapUiStatus(raw.status, raw.payment_status);
  const paymentRef = raw.payment_reference || raw.paymentReference;
  return {
    id: raw.booking_id || raw.id,
    courtId: item?.court_id || item?.courtId,
    itemId: item?.item_id || item?.itemId || null,
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
    total: item?.price ?? (duration || 1) * (inferredRate || HOURLY_RATE),
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

function getCourtHourlyRate(courtId) {
  const rate = state.courts.find((c) => c.id === courtId)?.hourlyRate;
  const num = typeof rate === "number" ? rate : parseFloat(rate);
  return Number.isFinite(num) ? num : HOURLY_RATE;
}

// ===================================
// SELECTION MANAGEMENT
// ===================================

function setSelection(facilityId, dateStr) {
  state.selectedFacilityId = facilityId;
  state.selectedDate = dateStr;
  state.selectedSlots = [];
  localStorage.setItem("soa_facility_id", facilityId || "");
  localStorage.setItem("soa_booking_date", dateStr || "");
}

// ===================================
// AUTH & USER
// ===================================

function getAuthOrRedirect() {
  const auth = window.api?.getAuth() || {};
  if (!auth.token) {
    window.api?.auth.redirectToLogin();
    return null;
  }
  return auth;
}

function buildProfileFromAuth(user = {}) {
  let rank = "Khách hàng";
  if (user.role === "manager") rank = "Quản lý";
  else if (user.role === "staff") rank = "Nhân viên";
  
  return {
    id: user.user_id || user.id || null,
    name: user.fullname || user.name || "Khách hàng",
    phone: user.phone || "Chưa cập nhật",
    email: user.email || "",
    balance: user.balance || 0,
    rank: rank,
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

// ===================================
// DATA REFRESH
// ===================================

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
    // Don't load all bookings on page load - too slow!
    // Only load user's own bookings
    const data = await window.api.booking.list({}, { forceRefresh });
    state.bookings = data.flatMap(normalizeBooking);
  } catch (err) {
    console.error("Booking list error:", err);
    // Don't show toast - fail silently for better UX
  }
}

async function refreshOccupiedBookings(options = {}) {
  const {
    forceRefresh = false,
    facilityId = state.selectedFacilityId,
    date = state.selectedDate,
  } = options;

  if (!facilityId) {
    console.warn("[SharedUtils] Missing facility for occupied bookings refresh.");
    return state.occupiedBookings;
  }

  const cacheKey = `${facilityId}-${date || ""}`;
  if (forceRefresh) {
    OCCUPIED_SLOTS_CACHE.delete(cacheKey);
  } else if (OCCUPIED_SLOTS_CACHE.has(cacheKey)) {
    state.occupiedBookings = OCCUPIED_SLOTS_CACHE.get(cacheKey);
    return state.occupiedBookings;
  }

  try {
    const data = await window.api.booking.occupiedSlots(facilityId, date);
    const normalized = data.flatMap(normalizeBooking);
    state.occupiedBookings = normalized;
    OCCUPIED_SLOTS_CACHE.set(cacheKey, normalized);
    return normalized;
  } catch (err) {
    console.error("[SharedUtils] Failed to fetch occupied bookings:", err);
    return state.occupiedBookings;
  }
}

// ===================================
// EXPORT TO WINDOW
// ===================================

window.SharedUtils = {
  // Constants
  START_HOUR,
  END_HOUR,
  DEFAULT_VIEW_HOUR,
  HOURLY_RATE,
  TODAY,
  MAX_BOOKING_DATE,
  SLOT_STEP_MINUTES,
  MAX_SLOTS_PER_BOOKING,
  
  // Format functions
  formatCurrency,
  formatDateVi,
  formatTimeFromMinutes,
  formatTimeLabel,
  formatSlotRangeLabel,
  toLocalISOString,
  parseBookingDateTime,
  
  // UI functions
  showToast,
  showConfirmDialog,
  closeModal,
  
  // Status functions
  getStatusStyle,
  mapUiStatus,
  
  // Data functions
  mapCourt,
  isSameDate,
  normalizeBooking,
  normalizeBookingItem,
  getCourtName,
  getFacilityName,
  getFacilityInfo,
  getFacilityCode,
  getCourtHourlyRate,
  getManagerSegmentsForCourt,
  getCourtSlotPrice,
  
  // Selection
  setSelection,
  
  // Auth
  getAuthOrRedirect,
  buildProfileFromAuth,
  setAvatarInitials,
  
  // Data refresh
  refreshCourts,
  refreshFacilities,
  refreshBookings,
  refreshOccupiedBookings,
};

// Export individual functions to window for backward compatibility
window.formatCurrency = formatCurrency;
window.formatDateVi = formatDateVi;
window.showToast = showToast;
window.refreshBookings = refreshBookings;
window.getCourtSlotPrice = getCourtSlotPrice;
window.getManagerSegmentsForCourt = getManagerSegmentsForCourt;
window.refreshOccupiedBookings = refreshOccupiedBookings;
