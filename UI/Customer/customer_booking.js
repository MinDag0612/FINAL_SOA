// ===================================
// CUSTOMER BOOKING MODULE
// ===================================

const CustomerBooking = (() => {
  const { 
    START_HOUR, END_HOUR, DEFAULT_VIEW_HOUR, SLOT_STEP_MINUTES, MAX_SLOTS_PER_BOOKING,
    TODAY, MAX_BOOKING_DATE,
    formatCurrency, formatDateVi, formatTimeLabel, formatSlotRangeLabel, toLocalISOString,
    isSameDate, getCourtName, getFacilityCode, getFacilityInfo, getCourtSlotPrice,
    setSelection, showToast
  } = window.SharedUtils;

  let hasAutoScrolled = false;

  function queueOccupiedRefresh(forceRefresh = false) {
    if (!window.SharedUtils?.refreshOccupiedBookings) return Promise.resolve();
    if (!window.state.selectedFacilityId) return Promise.resolve();
    return window.SharedUtils.refreshOccupiedBookings({
      forceRefresh,
      facilityId: window.state.selectedFacilityId,
      date: window.state.selectedDate,
    });
  }

  function ensureOccupiedSlots(forceRefresh = false) {
    return queueOccupiedRefresh(forceRefresh).catch((err) => {
      console.error("[CustomerBooking] Occupied slots refresh failed:", err);
    });
  }

  // ===================================
  // SLOT SELECTION LOGIC
  // ===================================

  function toggleSelectedSlot(courtId, startDate) {
    if (!startDate || Number.isNaN(startDate.getTime())) return;
    const end = new Date(startDate.getTime() + 60 * 60 * 1000);
    const key = `${courtId}-${toLocalISOString(startDate)}`;
    const existingIndex = window.state.selectedSlots.findIndex((s) => `${s.courtId}-${toLocalISOString(s.start)}` === key);

    // console.log(`[toggleSelectedSlot] Court ${courtId}, Key: ${key}`);
    // console.log(`[toggleSelectedSlot] Current selectedSlots:`, window.state.selectedSlots.map(s => `${s.courtId}-${toLocalISOString(s.start)}`));

    if (existingIndex >= 0) {
      // console.log(`[toggleSelectedSlot] REMOVING slot at index ${existingIndex}`);
      window.state.selectedSlots.splice(existingIndex, 1);
    } else {
      if (window.state.selectedSlots.length >= MAX_SLOTS_PER_BOOKING) {
        showToast(`Bạn chỉ có thể chọn tối đa ${MAX_SLOTS_PER_BOOKING} giờ trong một lần đặt!`);
        return;
      }
      // console.log(`[toggleSelectedSlot] ADDING slot`);
      window.state.selectedSlots.push({ courtId, start: startDate, end });
    }

    window.state.selectedSlots.sort((a, b) => a.start.getTime() - b.start.getTime());
    updateSelectionBar();
    
    const body = document.getElementById("timeline-body-grid");
    if (body) {
      body.querySelectorAll(".timeline-cell.active").forEach((c) => {
        c.classList.remove("active");
      });
      window.state.selectedSlots.forEach((slot) => {
        const cell = body.querySelector(`.timeline-cell[data-court="${slot.courtId}"][data-start="${toLocalISOString(slot.start)}"]`);
        if (cell) cell.classList.add("active");
      });
    }
  }

  function summarizeSelectionPricing(slots) {
    if (!slots || !slots.length) return { total: 0, hours: 0, priceLabel: "--", rates: [] };
    const infos = slots.map((slot) => {
      const hours = (slot.end - slot.start) / (1000 * 60 * 60) || 1;
      const rate = getCourtSlotPrice(slot.courtId, slot.start);
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
    const key = `${courtId}-${toLocalISOString(startDate)}`;
    const isSelected = window.state.selectedSlots.some((s) => `${s.courtId}-${toLocalISOString(s.start)}` === key);
    if (isSelected) {
      // console.log(`[isSlotSelected] Court ${courtId} at ${toLocalISOString(startDate)} IS SELECTED`);
    }
    return isSelected;
  }

  function updateSelectionBar() {
    const textEl = document.getElementById("selection-text");
    const totalEl = document.getElementById("selection-total");
    const nextBtn = document.getElementById("btn-next");
    if (!textEl || !totalEl || !nextBtn) return;
    if (!window.state.selectedSlots.length) {
      textEl.innerText = "Chưa chọn";
      totalEl.innerText = "0 đ";
      nextBtn.disabled = true;
      return;
    }
    const { total } = summarizeSelectionPricing(window.state.selectedSlots);
    const first = window.state.selectedSlots[0];
    const label = first
      ? `${getCourtName(first.courtId)} · ${first.start.getHours()}:${String(first.start.getMinutes()).padStart(2, "0")} - ${first.end
          .getHours()
          .toString()
          .padStart(2, "0")}:${String(first.end.getMinutes()).padStart(2, "0")}`
      : "Đã chọn";
    const suffix = window.state.selectedSlots.length > 1 ? `  +${window.state.selectedSlots.length - 1} ô khác` : "";
    textEl.innerText = `${label}${suffix}`;
    totalEl.innerText = formatCurrency(total);
    nextBtn.disabled = false;
  }

  // ===================================
  // CHECKOUT MODAL
  // ===================================

  function openQuickCheckout() {
    if (!window.state.selectedSlots.length) {
      showToast("Vui lòng chọn khung giờ trước.");
      return;
    }
    const modal = document.getElementById("quickCheckoutModal");
    if (!modal) return;
    const facility = getFacilityInfo(window.state.selectedFacilityId);
    const branchCode = getFacilityCode(window.state.selectedFacilityId);
    const pricing = summarizeSelectionPricing(window.state.selectedSlots);
    const firstSlotRate = getCourtSlotPrice(
      window.state.selectedSlots[0].courtId,
      window.state.selectedSlots[0].start
    );
    const totalHours = pricing.hours;
    const total = pricing.total;

    const slotText = window.state.selectedSlots
      .map((slot) => {
        const timeRange = `${formatTimeLabel(slot.start)} - ${formatTimeLabel(slot.end)}`;
        return `<div class="slot-line">• ${getCourtName(slot.courtId)}: ${timeRange} (${formatDateVi(slot.start)} - ${branchCode})</div>`;
      })
      .join("");

    const summaryFields = {
      "qc-branch": `CN ${branchCode} ${facility.name ? "- " + facility.name : ""}`,
      "qc-address": facility.address || facility.location || "Đang cập nhật địa chỉ",
      "qc-slot": slotText || "--",
      "qc-price-hour": window.state.selectedSlots.length > 1 ? pricing.priceLabel : formatCurrency(firstSlotRate),
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
    if (nameInput) nameInput.value = window.state.userProfile.name || "";
    if (phoneInput) phoneInput.value = window.state.userProfile.phone || "";
    if (emailInput) emailInput.value = window.state.userProfile.email || "";

    modal.classList.add("show");
  }

  async function submitQuickCheckout() {
    if (!window.state.selectedSlots.length) {
      alert("Vui lòng chọn khung giờ trước.");
      return;
    }
    
    if (window.state.selectedSlots.length > MAX_SLOTS_PER_BOOKING) {
      alert(`Bạn chỉ có thể đặt tối đa ${MAX_SLOTS_PER_BOOKING} giờ trong một lần booking!`);
      return;
    }
    
    const name = document.getElementById("qc-name")?.value.trim();
    const phone = document.getElementById("qc-phone")?.value.trim();
    const email = document.getElementById("qc-email")?.value.trim();
    const coupon = document.getElementById("qc-coupon")?.value.trim();
    
    if (!name || !phone || !email) {
      showToast("   Vui lòng nhập đủ tên, số điện thoại và email.");
      return;
    }
    
    if (!window.state.selectedFacilityId) {
      showToast("   Vui lòng chọn cơ sở trước.");
      return;
    }

    // console.log('[submitQuickCheckout] Starting checkout process...');

    try {
      const bookingData = {
        facility_id: window.state.selectedFacilityId,
        items: window.state.selectedSlots.map((slot) => ({
          court_id: slot.courtId,
          start_time: toLocalISOString(slot.start),
          end_time: toLocalISOString(slot.end),
          price: getCourtSlotPrice(slot.courtId, slot.start),
        })),
        customer_name: name,
        customer_phone: phone,
        customer_email: email,
        coupon: coupon || null,
        user_id: window.state.userProfile.userId || window.state.userProfile.user_id || window.state.userProfile.id,
      };

      const backendBase = window.api?.base || window.CONFIG?.BACKEND_PUBLIC_URL || window.location.origin;
      // console.log('[submitQuickCheckout] Saving booking data to localStorage:', bookingData, 'backendBase:', backendBase);
      localStorage.setItem('pendingBookingData', JSON.stringify(bookingData));
      localStorage.setItem('pendingBookingBase', backendBase);
      
      const total = bookingData.items.reduce((sum, item) => sum + item.price, 0);
      
      const customerHomePath = "/ui/Customer/index.html";
      const paymentUrl = `/ui/Homepage/mock_payment.html?` +
        `amount=${total}&` +
        `description=${encodeURIComponent(`Đặt ${bookingData.items.length} slots`)}&` +
        `orderCode=pending-booking-${Date.now()}&` +
        `returnUrl=${encodeURIComponent(customerHomePath)}&` +
        `cancelUrl=${encodeURIComponent(customerHomePath)}`;
      
      // console.log('[submitQuickCheckout] Redirecting to payment:', paymentUrl);
      // console.log('[submitQuickCheckout] Full payment URL:', window.location.origin + paymentUrl);
      
      // Close modal before redirect
      window.SharedUtils.closeModal('quickCheckoutModal');
      
      // Redirect to payment page
      window.location.href = paymentUrl;
    } catch (err) {
      console.error("[submitQuickCheckout] Error:", err);
      showToast("   Không thể chuyển hướng thanh toán: " + err.message);
    }
  }

  // ===================================
  // SELECTION MODAL
  // ===================================

  function openSelectionModal() {
    const modal = document.getElementById("selectionModal");
    if (!modal) return;
    const select = document.getElementById("facility-select");
    const dateInput = document.getElementById("facility-date");
    if (select) {
      select.innerHTML = window.state.facilities
        .map((f) => `<option value="${f.facility_id || f.id}">${f.name}</option>`)
        .join("");
      if (window.state.selectedFacilityId) select.value = window.state.selectedFacilityId;
    }
    if (dateInput) {
      dateInput.value = window.state.selectedDate || new Date().toISOString().split("T")[0];
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
    window.SharedUtils.refreshBookings().then(() => {
      if (typeof window.changeView === 'function') {
        window.changeView(window.currentView || 'booking');
      }
    });
  }

  // ===================================
  // RENDER BOOKING VIEW
  // ===================================

  function renderBooking() {
    const dynamicContent = document.getElementById("dynamic-content");
    if (!dynamicContent) return;

    hasAutoScrolled = false;
    const slots = Array.from({ length: ((END_HOUR - START_HOUR) * 60) / SLOT_STEP_MINUTES }, (_, i) => START_HOUR * 60 + i * SLOT_STEP_MINUTES);
    const today = new Date();
    const defaultDate = today.toISOString().split("T")[0];
    
    let activeDate = window.state.selectedDate || defaultDate;
    if (activeDate < defaultDate) {
      activeDate = defaultDate;
      window.state.selectedDate = defaultDate;
      localStorage.setItem("soa_booking_date", defaultDate);
    }
    
    const columnStyle = `style="grid-template-columns: repeat(${slots.length}, 140px);"`;

    const bookingHtml = `
      <section class="booking-shell">
        <div class="booking-header-hero">
          <div class="hero-left">
            <p class="eyebrow">Đặt sân theo giờ</p>
            <h1 class="page-hero">BSport</h1>
            <a class="guide-link" href="#">Xem giá, hướng dẫn</a>
          </div>
          <div class="hero-center">
            <label class="date-label">Chọn cơ sở</label>
            <select id="facility-select" class="facility-dropdown">
              ${
                window.state.facilities.length
                  ? window.state.facilities
                      .map(
                        (f) => `
              <option value="${f.facility_id || f.id}" ${
                          f.facility_id === window.state.selectedFacilityId || f.id === window.state.selectedFacilityId ? "selected" : ""
                        }>${f.name}</option>`
                      )
                      .join("")
                  : '<option value="">Chưa có cơ sở</option>'
              }
            </select>
          </div>
          <div class="hero-right">
            <label class="date-label">Chọn ngày</label>
            <div class="date-input-pill">
              <input type="date" id="booking-date" value="${activeDate}" min="${TODAY}" max="${MAX_BOOKING_DATE}" />
            </div>
          </div>
          <div class="hero-logout">
            <button class="btn-logout" onclick="window.location.href='../Login/login.html'">
              <i class="fa-solid fa-arrow-right-from-bracket"></i> Đăng xuất
            </button>
          </div>
        </div>

        <div class="booking-legend">
          <div class="legend-item"><span class="legend-box blank"></span>Trống (FREE)</div>
          <div class="legend-item"><span class="legend-box booked"></span>Đã đặt (BOOKED)</div>
          <div class="legend-item"><span class="legend-box active"></span>Đang chọn (SELECTED)</div>
          <div class="legend-item"><span class="legend-box past"></span>Hết hạn (EXPIRED)</div>
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
      if (window.state.selectedSlots.length) {
        openQuickCheckout();
      }
    };

    setupEventListeners();
    renderGrid();
    updateSelectionBar();
    ensureOccupiedSlots().then(() => {
      renderGrid();
      updateSelectionBar();
    });
    window.renderBookingGrid = renderGrid;
  }

  function setupEventListeners() {
    document.getElementById("booking-date")?.addEventListener("change", async (e) => {
      const selectedDate = e.target.value;
      const today = new Date().toISOString().split("T")[0];
      const maxDate = new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0];
      
      if (selectedDate < today || selectedDate > maxDate) {
        showToast("   Chỉ được đặt sân từ hôm nay đến 7 ngày tới!");
        e.target.value = today;
        return;
      }
      
      setSelection(window.state.selectedFacilityId, selectedDate);
      renderGrid();
      updateSelectionBar();
      await ensureOccupiedSlots(true);
      renderGrid();
      updateSelectionBar();
    });

    const facilitySelect = document.getElementById("facility-select");
    if (facilitySelect) {
      facilitySelect.addEventListener("change", (e) => {
        const facilityId = parseInt(e.target.value, 10);
        setSelection(facilityId, document.getElementById("booking-date")?.value || window.state.selectedDate);
        window.SharedUtils.refreshBookings().then(() => renderBooking());
      });
    }

    document.getElementById("timeline-body-grid")?.addEventListener("click", (e) => {
      const cell = e.target.closest(".timeline-cell");
      if (!cell) return;
      
      if (cell.classList.contains("booked")) {
        const rawId = cell.dataset.bookingId;
        const bookingId = rawId ? Number(rawId) : NaN;
        if (Number.isFinite(bookingId) && bookingId > 0 && window.CustomerDashboard?.openCheckoutModal) {
          window.CustomerDashboard.openCheckoutModal(bookingId);
          return;
        }
        showToast("Ô này đã được đặt!");
        return;
      }
      if (cell.classList.contains("past")) {
        showToast("Không thể đặt sân trong quá khứ!");
        return;
      }
      
      const courtId = parseInt(cell.dataset.court, 10);
      const start = new Date(cell.dataset.start);
      
      toggleSelectedSlot(courtId, start);
      renderGrid();
    });
  }

  function renderGrid() {
    const selectedDate = document.getElementById("booking-date")?.value || window.state.selectedDate;
    // console.log("[renderGrid] All bookings:", window.state.bookings.length);
    // console.log("[renderGrid] Selected date:", selectedDate);
    const bookingCandidates = [
      ...(window.state.occupiedBookings || []),
      ...(window.state.bookings || []),
    ];
    const filteredBookings = bookingCandidates.filter((b) => {
      const bookingStatus = (b.status || b.uiStatus || "").toLowerCase();
      const isActiveBooking = bookingStatus === "confirmed";
      return (
        isActiveBooking &&
        (!window.state.selectedFacilityId || !b.facilityId || b.facilityId === window.state.selectedFacilityId) &&
        (!selectedDate || (b.start && isSameDate(b.start, selectedDate)))
      );
    });
    // console.log("[renderGrid] Filtered bookings:", filteredBookings.length, filteredBookings);
    const courts = window.state.courts.filter((c) => !window.state.selectedFacilityId || c.facilityId === window.state.selectedFacilityId);
    const slots = Array.from({ length: ((END_HOUR - START_HOUR) * 60) / SLOT_STEP_MINUTES }, (_, i) => START_HOUR * 60 + i * SLOT_STEP_MINUTES);
    const body = document.getElementById("timeline-body-grid");
    const courtList = document.getElementById("court-list");
    if (!body) return;
    
    const columnStyle = `style="grid-template-columns: repeat(${slots.length}, 140px);"`;
    
    if (courtList) {
      courtList.innerHTML = courts
        .map(
          (c) => `
          <div class="court-item">
            <div class="court-code">${getFacilityCode(window.state.selectedFacilityId)}</div>
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
            
            const now = new Date();
            const isPast = start < now;
            
            const booking = filteredBookings.find((b) => {
              const matches = b.courtId === c.id && b.start && b.end && b.start <= start && b.end > start;
              return matches;
            });
            const bookingId = booking?.id || booking?.booking_id || "";
            let status = "blank";
            if (isPast) {
              status = "past";
            } else if (booking) {
              const bookingStatus = booking.status || booking.uiStatus;
              // console.log(`[renderGrid] Slot ${start.toISOString()} court ${c.id}: booking status="${bookingStatus}", will show as "${bookingStatus === 'confirmed' ? 'BOOKED (RED)' : 'BLANK (WHITE)'}"`);
              if (bookingStatus === "confirmed") {
                status = "booked";
              } else if (["cancelled", "expired", "pending"].includes(bookingStatus)) {
                status = "blank";
              } else {
                status = "blank";
              }
            } else if (isSlotSelected(c.id, start)) {
              status = "active";
            }
            
            const slotPrice = getCourtSlotPrice(c.id, start);
            const endTime = new Date(start);
            endTime.setHours(endTime.getHours() + 1);
            const tooltipTime = `${formatTimeLabel(start)} - ${formatTimeLabel(endTime)}`;
            const priceLabel = formatCurrency(slotPrice);
            const tooltipParts = [tooltipTime, `Giá: ${priceLabel}`];
            if (booking) {
              tooltipParts.unshift(booking.customer || "Khách hàng");
            }
            const tooltip = tooltipParts.join(" · ");
            const bookingAttribute = bookingId ? ` data-booking-id="${bookingId}"` : "";
            return `<div class="timeline-cell ${status}" title="${tooltip}" data-court="${c.id}" data-start="${toLocalISOString(start)}"${bookingAttribute}></div>`;
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
  }

  // ===================================
  // EXPORT API
  // ===================================

  return {
    renderBooking,
    openQuickCheckout,
    submitQuickCheckout,
    openSelectionModal,
    confirmSelection,
    updateSelectionBar,
  };
})();

// Export to window
window.CustomerBooking = CustomerBooking;
window.openQuickCheckout = CustomerBooking.openQuickCheckout;
window.submitQuickCheckout = CustomerBooking.submitQuickCheckout;
window.openSelectionModal = CustomerBooking.openSelectionModal;
window.confirmSelection = CustomerBooking.confirmSelection;
