// ===================================
// STAFF MAIN APPLICATION
// ===================================

const StaffApp = (() => {
  const {
    getAuthOrRedirect, buildProfileFromAuth,
    refreshFacilities, showToast, formatDateVi, normalizeBooking, mapCourt
  } = window.SharedUtils;

  let currentTab = "courts";
  let assignedCourts = []; // Danh sách sân được phân công cho staff
  const managerState = {
    managerFacilityId: null,
    managerDate: new Date().toISOString().split("T")[0],
  };
  let cachedCourts = [];
  let cachedBookings = [];
  const dataCache = {
    courts: new Map(),
    bookings: new Map(),
  };
  const courtHourFilter = {
    startHour: 0,
    endHour: 23,
    enabled: false,
  };
  const getCacheKey = (facilityId, dateStr) => `${facilityId}-${dateStr}`;
  const showManagerLoader = (visible) => {
    const loader = document.getElementById("staff-loading");
    if (!loader) return;
    loader.classList.toggle("hidden", !visible);
  };

  const buildHourOptions = () =>
    Array.from({ length: 24 }, (_, hour) => `<option value="${hour}">${String(hour).padStart(2, "0")}:00</option>`).join("");

  // ===================================
  // INITIALIZATION
  // ===================================

  async function initialize() {
    const auth = getAuthOrRedirect();
    if (!auth) return;

    // Check if user is staff
    if (auth.user.role !== 'staff') {
      alert('Bạn không có quyền truy cập trang này. Chỉ nhân viên mới có thể truy cập.');
      window.location.href = '../Login/login.html';
      return;
    }

    window.state.userProfile = buildProfileFromAuth(auth.user);
    
    // Get assigned courts from user data (mocked for now)
    // TODO: Backend should return assigned_courts in user token
    assignedCourts = auth.user.assigned_courts || [1, 2]; // Default: sân 1, 2
    console.log('[Staff] Assigned courts:', assignedCourts);

    // Set default date to current date
    updateCurrentDate();

    // Set up tab switching
    setupTabs();

    // Set up event listeners
    setupEventListeners();

    // Show UI immediately with loading state
    showSkeletonUI();

    // Load facilities in background
    refreshFacilities().then(() => {
      // Set default facility
      if (window.state.facilities.length > 0) {
        managerState.managerFacilityId = window.state.facilities[0].facility_id || window.state.facilities[0].id;
      }

      // Populate facility dropdowns
      populateFacilityDropdowns();

      // Load default tab (courts) after facilities are loaded
      switchTab("courts");
    }).catch(err => {
      console.error("Failed to load facilities:", err);
      showManagerLoadError("Không thể tải danh sách cơ sở");
    });

    // Update date every minute to keep it current
    setInterval(updateCurrentDate, 60000);
  }

  function showSkeletonUI() {
    // Show skeleton/loading state for stats
    const statsContainer = document.getElementById("courts-stats");
    if (statsContainer) {
      statsContainer.innerHTML = `
        <div class="stat-card">
          <div class="skeleton-loader" style="width: 60%; height: 20px; margin-bottom: 8px;"></div>
          <div class="skeleton-loader" style="width: 40%; height: 32px;"></div>
        </div>
        <div class="stat-card">
          <div class="skeleton-loader" style="width: 60%; height: 20px; margin-bottom: 8px;"></div>
          <div class="skeleton-loader" style="width: 40%; height: 32px;"></div>
        </div>
        <div class="stat-card">
          <div class="skeleton-loader" style="width: 60%; height: 20px; margin-bottom: 8px;"></div>
          <div class="skeleton-loader" style="width: 40%; height: 32px;"></div>
        </div>
      `;
    }
  }

  // Update current date (using local timezone)
  function updateCurrentDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const today = `${year}-${month}-${day}`;
    
    managerState.managerDate = today;
    const dateInput = document.getElementById("staff-date-select-global");
    if (dateInput && dateInput.value !== today) {
      dateInput.value = today;
      // Refresh courts tab if it's active and date changed
      if (currentTab === "courts") {
        refreshCourtsTab();
      }
    }
  }

  // ===================================
  // FACILITY DROPDOWN
  // ===================================

  function populateFacilityDropdowns() {
    const dropdown = document.getElementById("staff-facility-select-global");

    const options = window.state.facilities.length
      ? window.state.facilities
          .map(
            (f) =>
              `<option value="${f.facility_id || f.id}" ${
                (f.facility_id === managerState.managerFacilityId || f.id === managerState.managerFacilityId) ? "selected" : ""
              }>${f.name}</option>`
          )
          .join("")
      : '<option value="">Chưa có cơ sở</option>';

    if (dropdown) {
      dropdown.innerHTML = options;
    }
  }

  // ===================================
  // TAB SWITCHING
  // ===================================

  function setupTabs() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    tabButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const tabName = btn.getAttribute("data-tab");
        switchTab(tabName);
      });
    });
  }

  function switchTab(tabName) {
    currentTab = tabName;

    // Update active button
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.classList.remove("active");
    });
    document.querySelector(`.tab-btn[data-tab="${tabName}"]`)?.classList.add("active");

    // Show active content
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.classList.remove("active");
    });
    document.getElementById(`tab-${tabName}`)?.classList.add("active");

    // Load tab data
    if (tabName === "courts") {
      refreshCourtsTab();
    } else if (tabName === "bookings") {
      refreshBookingsTab();
    } else if (tabName === "reports") {
      refreshReportsTab();
    }
    // No settings tab for staff
  }

  const renderCourtsView = (courts, bookings, dateStr) => {
    const statsHtml = window.ManagerCourts.renderCourtsStats(courts, bookings, dateStr, courtHourFilter);
    const statsContainer = document.getElementById("courts-stats");
    if (statsContainer) statsContainer.innerHTML = statsHtml;

    renderCourtFilterBar();

    const courtsContainer = document.getElementById("courts-list");
    if (courtsContainer) {
      const courtsHtml = window.ManagerCourts.renderCourtsSection(courts, bookings, dateStr, courtHourFilter);
      courtsContainer.innerHTML = courtsHtml;
    }
  };

  function applyCourtFilter() {
    const startInput = document.getElementById("courts-filter-start");
    const endInput = document.getElementById("courts-filter-end");
    if (!startInput || !endInput) return;
    const startHour = Number(startInput.value);
    const endHour = Number(endInput.value);
    if (Number.isNaN(startHour) || Number.isNaN(endHour)) return;
    if (startHour > endHour) {
      showToast("Giờ bắt đầu phải nhỏ hơn giờ kết thúc.");
      return;
    }
    courtHourFilter.startHour = startHour;
    courtHourFilter.endHour = endHour;
    courtHourFilter.enabled = !(startHour === 0 && endHour === 23);
    renderCourtsView(cachedCourts, cachedBookings, managerState.managerDate);
  }

  function resetCourtFilter() {
    courtHourFilter.startHour = 0;
    courtHourFilter.endHour = 23;
    courtHourFilter.enabled = false;
    renderCourtsView(cachedCourts, cachedBookings, managerState.managerDate);
  }

  function renderCourtFilterBar() {
    const container = document.getElementById("courts-filter-bar");
    if (!container) return;
    const options = buildHourOptions();
    container.innerHTML = `
      <div class="courts-filter-panel">
        <div class="courts-filter-control">
          <strong>Lọc theo ca làm</strong>
          <span class="muted">Chỉ hiển thị sân đã có booking trong khung giờ được chọn.</span>
        </div>
        <div class="courts-filter-control">
          <label for="courts-filter-start">Từ</label>
          <select id="courts-filter-start">${options}</select>
          <span>đến</span>
          <label for="courts-filter-end">Đến</label>
          <select id="courts-filter-end">${options}</select>
        </div>
        <div class="courts-filter-actions">
          <button type="button" class="btn-primary" id="courts-filter-apply">Áp dụng</button>
          <button type="button" class="btn-secondary" id="courts-filter-reset">Xóa filter</button>
        </div>
      </div>
    `;
    document.getElementById("courts-filter-start").value = String(courtHourFilter.startHour);
    document.getElementById("courts-filter-end").value = String(courtHourFilter.endHour);
    document.getElementById("courts-filter-apply")?.addEventListener("click", applyCourtFilter);
    document.getElementById("courts-filter-reset")?.addEventListener("click", resetCourtFilter);
  }

  const loadManagerBookingLogs = () => {
    if (window.ManagerBooking?.refreshBookingLogs) {
      return window.ManagerBooking.refreshBookingLogs(managerState.managerFacilityId, managerState.managerDate);
    }
    return Promise.resolve();
  };

  // ===================================
  // COURTS TAB
  // ===================================

  async function refreshCourtsTab(forceRefresh = false) {
    const facilityId = managerState.managerFacilityId;
    const dateStr = managerState.managerDate;

    if (!facilityId) {
      showManagerLoadError("Vui lòng chọn cơ sở để xem sân.");
      return;
    }

    const cacheKey = getCacheKey(facilityId, dateStr);
    const cached = dataCache.courts.get(cacheKey);
    if (cached && !forceRefresh) {
      cachedCourts = cached.courts;
      cachedBookings = cached.bookings;
      renderCourtsView(cachedCourts, cachedBookings, dateStr);
      loadManagerBookingLogs();
      return;
    }

    // Show cached courts immediately while loading new data
    if (cachedCourts.length > 0 && !forceRefresh) {
      renderCourtsView(cachedCourts, [], dateStr);
      loadManagerBookingLogs();
    } else {
      showManagerLoader(true);
    }

    try {
      // Load courts first (usually faster)
      const courtsData = await window.api.court.listByFacility(facilityId);
      const courtsArray = Array.isArray(courtsData) ? courtsData : courtsData?.data || [];
      let courts = courtsArray.map(mapCourt);
      
      // [STAFF FILTER] Only show assigned courts
      if (assignedCourts.length > 0) {
        courts = courts.filter(c => assignedCourts.includes(c.id || c.court_id));
        console.log('[Staff] Filtered courts:', courts.length, 'from', courtsArray.length);
      }
      
      // Render courts immediately and hide loader
      cachedCourts = courts;
      renderCourtsView(courts, [], dateStr);
      showManagerLoader(false); // Hide loader NOW, don't wait for bookings
      
      // Load bookings in background (non-blocking)
      const bookingsData = await window.api.booking.managerList(facilityId, dateStr);
      const bookingsArray = Array.isArray(bookingsData) ? bookingsData : bookingsData?.data || [];
      const bookings = bookingsArray.flatMap(normalizeBooking);
      
      // Update cache and re-render with bookings
      cachedBookings = bookings;
      dataCache.courts.set(cacheKey, { courts, bookings });
      
      // Re-render with bookings data (màu đỏ xuất hiện)
      renderCourtsView(courts, bookings, dateStr);
      loadManagerBookingLogs();
    } catch (err) {
      console.error("[refreshCourtsTab] Error:", err);
      showManagerLoadError(`Không tải được dữ liệu sân: ${err.message}`);
      showManagerLoader(false);
    }
  }

  // ===================================
  // BOOKINGS TAB
  // ===================================

  async function refreshBookingsTab(forceRefresh = false) {
    const facilityId = managerState.managerFacilityId;
    const dateStr = managerState.managerDate;

    if (!facilityId) {
      showManagerLoadError("Vui lòng chọn cơ sở để xem booking.");
      return;
    }

    const cacheKey = getCacheKey(facilityId, dateStr);
    
    // Clear cache if force refresh
    if (forceRefresh) {
      dataCache.courts.delete(cacheKey);
    }
    
    const cached = dataCache.courts.get(cacheKey);
    
    // Show cached data immediately if available
    if (cached && !forceRefresh) {
      const { courts, bookings } = cached;
      
      // Render everything from cache instantly
      const walkinContainer = document.getElementById("bookings-walkin-form");
      if (walkinContainer) {
        walkinContainer.innerHTML = window.ManagerBooking.renderWalkInForm(courts);
      }

      const headerContainer = document.getElementById("bookings-header");
      if (headerContainer) {
        headerContainer.innerHTML = `
          <div class="card" style="margin-bottom: 20px;">
            <h4><i class="fa-solid fa-clock-rotate-left"></i> Lịch Sử Thay Đổi Booking</h4>
            <p class="muted">Ngày: ${formatDateVi(new Date(dateStr))} • Cơ sở: ${window.state.facilities.find(f => (f.facility_id || f.id) === facilityId)?.name || 'N/A'}</p>
          </div>
        `;
        if (window.ManagerBooking && typeof window.ManagerBooking.renderTimeRangeFilter === 'function') {
          headerContainer.innerHTML += window.ManagerBooking.renderTimeRangeFilter();
        }
      }

      // Load and render booking history logs
      const bookingsContainer = document.getElementById("bookings-list");
      console.log("[Manager Cache] Fetching logs for facility:", facilityId, "date:", dateStr);
      window.api.booking.logsByFacility(facilityId, dateStr).then(logsData => {
        console.log("[Manager Cache] Logs received:", logsData);
        const logs = Array.isArray(logsData) ? logsData : (logsData?.data || []);
        console.log("[Manager Cache] Final logs:", logs, "length:", logs.length);
        if (bookingsContainer) {
          bookingsContainer.innerHTML = window.ManagerBooking.renderBookingHistory(logs);
        }
      }).catch(err => {
        console.error("[refreshBookingsTab] Failed to load logs from cache:", err);
        if (bookingsContainer) {
          bookingsContainer.innerHTML = '<div style="padding: 20px; color: #666;">Đang tải lịch sử...</div>';
        }
      });

      window.refreshManagerBookings = () => refreshBookingsTab(true);
      loadManagerBookingLogs();
      return; // Done - no loading needed
    }

    showManagerLoader(true);
    
    try {
      // Load courts first (for walk-in form)
      const courtsData = await window.api.court.listByFacility(facilityId);
      const courtsArray = Array.isArray(courtsData) ? courtsData : courtsData?.data || [];
      const courts = courtsArray.map(mapCourt);

      // Render walk-in form immediately
      const walkinContainer = document.getElementById("bookings-walkin-form");
      if (walkinContainer) {
        walkinContainer.innerHTML = window.ManagerBooking.renderWalkInForm(courts);
      }

      // Render empty table with loading state
      const bookingsContainer = document.getElementById("bookings-list");
      if (bookingsContainer) {
        bookingsContainer.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;">Đang tải danh sách booking...</div>';
      }
      
      showManagerLoader(false); // Hide loader NOW

      // Load bookings in background
      const bookingsData = await window.api.booking.managerList(facilityId, dateStr);
      const bookingsArray = Array.isArray(bookingsData) ? bookingsData : bookingsData?.data || [];
      const bookings = bookingsArray.flatMap(normalizeBooking);

      // Update cache
      dataCache.courts.set(cacheKey, { courts, bookings });

      // Render header with actual data
      const headerContainer = document.getElementById("bookings-header");
      if (headerContainer) {
        headerContainer.innerHTML = `
          <div class="card" style="margin-bottom: 20px;">
            <h4><i class="fa-solid fa-clock-rotate-left"></i> Lịch Sử Thay Đổi Booking</h4>
            <p class="muted">Ngày: ${formatDateVi(new Date(dateStr))} • Cơ sở: ${window.state.facilities.find(f => (f.facility_id || f.id) === facilityId)?.name || 'N/A'}</p>
          </div>
        `;

        if (window.ManagerBooking && typeof window.ManagerBooking.renderTimeRangeFilter === 'function') {
          headerContainer.innerHTML += window.ManagerBooking.renderTimeRangeFilter();
        }
      }

      // Load and render booking history logs
      try {
        console.log("[Manager] Fetching logs for facility:", facilityId, "date:", dateStr);
        const logsData = await window.api.booking.logsByFacility(facilityId, dateStr);
        console.log("[Manager] Logs data received:", logsData);
        console.log("[Manager] Logs data type:", typeof logsData, "isArray:", Array.isArray(logsData));
        
        const logs = Array.isArray(logsData) ? logsData : (logsData?.data || []);
        console.log("[Manager] Final logs array:", logs, "length:", logs.length);
        
        if (bookingsContainer) {
          const historyHtml = window.ManagerBooking.renderBookingHistory(logs);
          bookingsContainer.innerHTML = historyHtml;
        }
      } catch (err) {
        console.error("[refreshBookingsTab] Failed to load logs:", err);
        if (bookingsContainer) {
          bookingsContainer.innerHTML = `
            <div class="error-message" style="padding: 20px; background: #fee; color: #c00; border-radius: 8px; text-align: center;">
              <i class="fa-solid fa-exclamation-triangle"></i> Không thể tải lịch sử: ${err.message}
            </div>
          `;
        }
      }

      // Set up refresh function
      window.refreshManagerBookings = () => refreshBookingsTab(true);
      loadManagerBookingLogs();
    } catch (err) {
      console.error("[refreshBookingsTab] Error:", err);
      showManagerLoadError(`Không tải được dữ liệu booking: ${err.message}`);
      showManagerLoader(false);
    }
  }

  // ===================================
  // REPORTS TAB
  // ===================================

  async function refreshReportsTab() {
    const facilityId = managerState.managerFacilityId;

    if (!facilityId) {
      showManagerLoadError("Vui lòng chọn cơ sở để xem báo cáo.");
      return;
    }

    const today = new Date();
    const startDate = new Date(today);
    startDate.setDate(today.getDate() - 7);
    const startDateStr = startDate.toISOString().split("T")[0];
    const endDateStr = today.toISOString().split("T")[0];

    // Render date range filter
    const filterContainer = document.getElementById("reports-filter");
    if (filterContainer) {
      filterContainer.innerHTML = window.ManagerReport.renderDateRangeFilter(startDateStr, endDateStr);
    }

    try {
      const [bookingsData, courtsData] = await Promise.all([
        window.api.booking.managerList(facilityId),
        window.api.court.listByFacility(facilityId),
      ]);

      const bookingsArray = Array.isArray(bookingsData) ? bookingsData : bookingsData?.data || [];
      const courtsArray = Array.isArray(courtsData) ? courtsData : courtsData?.data || [];

      const bookings = bookingsArray.flatMap(normalizeBooking);
      const courts = courtsArray.map(mapCourt);

      // Render usage stats
      const usageStatsHtml = window.ManagerReportCharts?.renderUsageStats(bookings, courts) || '';

      // Render revenue table
      const reportData = window.ManagerReport.calculateRevenueByCourtId(bookings, courts, startDateStr, endDateStr);
      const dateRange = `${formatDateVi(startDate)} - ${formatDateVi(today)}`;
      const reportHtml = window.ManagerReport.renderReportTable(reportData, dateRange);

      const reportContainer = document.getElementById("report-container");
      if (reportContainer) {
        reportContainer.innerHTML = usageStatsHtml + reportHtml;
      }
    } catch (err) {
      console.error("[refreshReportsTab] Error:", err);
      showManagerLoadError(`Không tải được báo cáo: ${err.message}`);
    }
  }

  // ===================================
  // EVENT LISTENERS
  // ===================================

  function setupEventListeners() {
    // Facility change - Global header
    document.getElementById("staff-facility-select-global")?.addEventListener("change", (e) => {
      managerState.managerFacilityId = parseInt(e.target.value, 10);
      // Refresh current tab
      if (currentTab === "courts") refreshCourtsTab();
      else if (currentTab === "bookings") refreshBookingsTab();
      else if (currentTab === "reports") refreshReportsTab();
    });

    // Date change - Global header (refresh current tab)
    document.getElementById("staff-date-select-global")?.addEventListener("change", (e) => {
      managerState.managerDate = e.target.value;
      if (currentTab === "courts") refreshCourtsTab();
      else if (currentTab === "bookings") refreshBookingsTab(true);
      else if (currentTab === "reports") refreshReportsTab();
    });

    // Logout button
    document.querySelector(".logout-btn-header")?.addEventListener("click", () => {
      window.api.clearAuth();
      window.api.auth.redirectToLogin();
    });
  }

  // ===================================
  // ERROR HANDLING
  // ===================================

  function showManagerLoadError(message) {
    const errorHtml = `
      <div class="error-message" style="padding: 20px; background: #fee; color: #c00; border-radius: 8px;">
        <i class="fa-solid fa-exclamation-triangle"></i> ${message}
      </div>
    `;

    if (currentTab === "courts") {
      const container = document.getElementById("courts-list");
      if (container) container.innerHTML = errorHtml;
    } else if (currentTab === "bookings") {
      const container = document.getElementById("bookings-list");
      if (container) container.innerHTML = errorHtml;
    } else if (currentTab === "reports") {
      const container = document.getElementById("report-container");
      if (container) container.innerHTML = errorHtml;
    }
  }

  // ===================================
  // MODAL MANAGEMENT
  // ===================================

  function openWalkInModal(courtId, courtName, date, hour) {
    const modal = document.getElementById('walkInModal');
    if (!modal) {
      console.error('[openWalkInModal] Modal not found');
      return;
    }

    // Pre-fill readonly fields (shown as text, not editable)
    const modalContent = document.getElementById('walkin-modal-content');
    if (modalContent) {
      const facility = window.state.facilities.find(f => 
        (f.facility_id || f.id) === managerState.managerFacilityId
      );
      const facilityName = facility ? facility.name : 'N/A';

      modalContent.innerHTML = `
        <form id="walkin-form">
          <div class="form-readonly">
            <p><strong>Cơ sở:</strong> ${facilityName}</p>
            <p><strong>Sân:</strong> ${courtName}</p>
            <p><strong>Ngày:</strong> ${window.SharedUtils.formatDateVi(date)}</p>
            <p><strong>Thời gian:</strong> ${String(hour).padStart(2, '0')}:00 - ${String(hour + 1).padStart(2, '0')}:00</p>
          </div>

          <label for="walkin-customer">Tên khách hàng *</label>
          <input type="text" id="walkin-customer" class="input-field" required />

          <label for="walkin-phone">Số điện thoại *</label>
          <input type="tel" id="walkin-phone" class="input-field" required />

          <label for="walkin-email">Email (tùy chọn)</label>
          <input type="email" id="walkin-email" class="input-field" />

          <label for="walkin-note">Ghi chú (tùy chọn)</label>
          <textarea id="walkin-note" class="input-field" rows="3"></textarea>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" onclick="ManagerApp.closeModal('walkInModal')">Hủy</button>
            <button type="submit" class="btn-primary">Xác nhận đặt sân</button>
          </div>
        </form>
      `;

      // Setup form submit handler
      const form = document.getElementById('walkin-form');
      if (form) {
        form.onsubmit = async (e) => {
          e.preventDefault();
          await handleWalkInBooking(courtId, date, hour);
        };
      }
    }

    modal.classList.add('show');
  }

  function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('show');
    }
  }

  async function handleWalkInBooking(courtId, date, hour) {
    const customerName = document.getElementById('walkin-customer').value.trim();
    const phone = document.getElementById('walkin-phone').value.trim();
    const email = document.getElementById('walkin-email').value.trim();
    const note = document.getElementById('walkin-note').value.trim();

    if (!customerName || !phone) {
      window.showToast('   Vui lòng nhập đầy đủ thông tin khách hàng');
      return;
    }

    try {
      const startTime = new Date(date);
      startTime.setHours(hour, 0, 0, 0);
      const endTime = new Date(startTime);
      endTime.setHours(hour + 1, 0, 0, 0);

      const court = window.state.courts.find(c => (c.id || c.court_id) === courtId);
      const hourlyRate = court?.hourly_rate || court?.price || 100000;

      const toLocal = window.SharedUtils?.toLocalISOString;
      const localizedStart = toLocal ? toLocal(startTime) : startTime.toISOString();
      const localizedEnd = toLocal ? toLocal(endTime) : endTime.toISOString();

      const bookingData = {
        user_id: window.state.userProfile.id,
        facility_id: managerState.managerFacilityId,
        payment_method: 'cash',
        note: note || 'Walk-in booking by manager',
        items: [{
          court_id: courtId,
          start_time: localizedStart,
          end_time: localizedEnd,
          price: hourlyRate
        }],
        customer_name: customerName,
        customer_phone: phone,
        customer_email: email || '',
        source: 'MANAGER_WALK_IN'
      };

      // console.log('[handleWalkInBooking] Creating booking:', bookingData);
      
      const result = await window.api.booking.create(bookingData);
      // console.log('[handleWalkInBooking] Booking created:', result);

      window.showToast('  Đặt sân thành công!');
      closeModal('walkInModal');

      // Refresh courts tab to show new booking
      clearCache();
      await refreshCourtsTab(true);
    } catch (err) {
      console.error('[handleWalkInBooking] Error:', err);
      window.showToast(`   Lỗi: ${err.message || 'Không thể tạo booking'}`);
    }
  }

  // ===================================
  // EXPORT API
  // ===================================

  const clearCache = () => {
    dataCache.courts.clear();
    dataCache.bookings.clear();
    cachedCourts = [];
    cachedBookings = [];
  };

  return {
    initialize,
    switchTab,
    refreshCourtsTab,
    refreshBookingsTab,
    refreshReportsTab,
    getState: () => managerState,
    getCurrentTab: () => currentTab,
    getAssignedCourts: () => assignedCourts,
    openWalkInModal,
    closeModal,
    clearCache,
  };
})();

// Expose as global for compatibility
window.ManagerApp = StaffApp;

// ===================================
// GLOBAL HELPER FUNCTIONS
// ===================================

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove("show");
}

// ===================================
// DOM READY
// ===================================

document.addEventListener("DOMContentLoaded", () => {
  StaffApp.initialize().catch((err) => {
    console.error("[StaffApp] Initialization error:", err);
  });
});

// Export to window
window.ManagerApp = ManagerApp;
window.closeModal = closeModal;
