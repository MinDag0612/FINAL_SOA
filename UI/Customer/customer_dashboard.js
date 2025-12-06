// ===================================
// CUSTOMER DASHBOARD MODULE
// ===================================

const CustomerDashboard = (() => {
  const { 
    formatCurrency, formatDateVi, getStatusStyle, 
    getFacilityName, getCourtName, isSameDate,
    showToast
  } = window.SharedUtils;

  // ===================================
  // PROFILE FUNCTIONS
  // ===================================

  function renderProfile() {
    const dynamicContent = document.getElementById("dynamic-content");
    if (!dynamicContent) return;

    const profileHtml = `
      <div class="profile-grid">
        <div class="card profile-card">
          <div class="card-header-simple">
            <h3>Thông tin cá nhân</h3>
            <button class="btn-icon" onclick="CustomerDashboard.openEditModal()"><i class="fa-solid fa-pen-to-square"></i></button>
          </div>
          <div class="profile-details">
            <div class="profile-avatar-large">${(window.state.userProfile.name[0] || "K").toUpperCase()}</div>
            <h2 id="user-name">${window.state.userProfile.name}</h2>
            <p id="user-rank" class="rank-badge">${window.state.userProfile.rank}</p>
            <div class="detail-row"><i class="fa-solid fa-phone"></i> <span id="user-phone">${window.state.userProfile.phone}</span></div>
            <div class="detail-row"><i class="fa-solid fa-envelope"></i> <span id="user-email">${window.state.userProfile.email}</span></div>
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
    document.getElementById("edit-name").value = window.state.userProfile.name;
    document.getElementById("edit-phone").value = window.state.userProfile.phone;
    document.getElementById("edit-email").value = window.state.userProfile.email;
    document.getElementById("editModal").classList.add("show");
  }

  function saveProfile() {
    window.state.userProfile.name = document.getElementById("edit-name").value;
    window.state.userProfile.phone = document.getElementById("edit-phone").value;
    window.state.userProfile.email = document.getElementById("edit-email").value;
    renderProfile();
    window.SharedUtils.closeModal("editModal");
    showToast("Cập nhật hồ sơ thành công!");
  }

  // ===================================
  // DASHBOARD FUNCTIONS
  // ===================================

  function renderDashboard() {
    const dynamicContent = document.getElementById("dynamic-content");
    if (!dynamicContent) return;

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
            <div class="selection-line">${getFacilityName(window.state.selectedFacilityId)} · ${window.state.selectedDate || new Date().toISOString().split("T")[0]}</div>
            <button class="btn-outline" onclick="CustomerBooking.openSelectionModal()">Đổi lựa chọn</button>
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
      const filteredCourts = window.state.selectedFacilityId
        ? window.state.courts.filter((c) => c.facilityId === window.state.selectedFacilityId)
        : window.state.courts;
      const counts = {
        total: filteredCourts.length,
        blank: 0,
        active: 0,
        booked: 0,
      };
      filteredCourts.forEach((c) => {
        const booking = window.state.bookings.find(
          (b) =>
            b.courtId === c.id &&
            (b.facilityId ? b.facilityId === c.facilityId : true) &&
            (!window.state.selectedDate || (b.start && isSameDate(new Date(window.state.selectedDate), b.start.toISOString()))) &&
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

      const filteredCourts = window.state.selectedFacilityId
        ? window.state.courts.filter((c) => c.facilityId === window.state.selectedFacilityId)
        : window.state.courts;

      const combinedCourts = filteredCourts.map((c) => {
        const booking = window.state.bookings.find(
          (b) =>
            b.courtId === c.id &&
            (b.facilityId ? b.facilityId === c.facilityId : true) &&
            (!window.state.selectedDate || (b.start && isSameDate(new Date(window.state.selectedDate), b.start.toISOString()))) &&
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
                <button class="btn-outline" onclick="CustomerDashboard.openCheckoutModal(${c.booking.id})">Chi tiết</button>
              </div>`;
          } else {
            content = `
              <div class="card-content-empty-modern">
                <div class="empty-icon"><i class="fa-solid fa-plus"></i></div>
                <div class="empty-text">Sân trống</div>
              </div>
              <div class="court-card-actions">
                <button class="btn-primary" onclick="window.changeView && window.changeView('booking')">Đặt ngay</button>
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

  function openCheckoutModal(bookingId) {
    const booking = window.state.bookings.find((b) => b.id === bookingId);
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
      actionDiv.innerHTML += `<button class="btn-cancel" onclick="CustomerDashboard.cancelBooking(${booking.id})">Hủy đặt</button>`;
    } else {
      actionDiv.innerHTML += `<div style="color:#6b7280;">Không có hành động khả dụng</div>`;
    }

    document.getElementById("checkoutModal").classList.add("show");
  }

  async function cancelBooking(id) {
    window.SharedUtils.showConfirmDialog("Bạn chắc chắn muốn hủy lịch này?", async () => {
      try {
        await window.api.booking.cancel(id, { reason: "Khách hàng hủy" });
        await window.SharedUtils.refreshBookings();
        window.SharedUtils.closeModal("checkoutModal");
        if (typeof window.changeView === 'function') {
          window.changeView(window.currentView || 'dashboard');
        }
        showToast("Đã hủy lịch đặt sân");
      } catch (err) {
        console.error(err);
        alert("Không hủy được lịch: " + err.message);
      }
    });
  }

  // ===================================
  // EXPORT API
  // ===================================

  return {
    renderDashboard,
    renderProfile,
    openEditModal,
    saveProfile,
    openCheckoutModal,
    cancelBooking,
  };
})();

// Export to window
window.CustomerDashboard = CustomerDashboard;
window.openEditModal = CustomerDashboard.openEditModal;
window.saveProfile = CustomerDashboard.saveProfile;
window.openCheckoutModal = CustomerDashboard.openCheckoutModal;
window.cancelBooking = CustomerDashboard.cancelBooking;
