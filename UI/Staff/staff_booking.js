const ManagerBooking = (() => {
  const getCourtSlotPrice = window.SharedUtils?.getCourtSlotPrice;
  const calculateSlotRangePrice = (courtId, date, startHour, endHour) => {
    if (!courtId || !date || startHour >= endHour) return null;
    const court = window.state?.courts?.find((c) => (c.id || c.court_id) === courtId);
    const baseRate = court?.hourly_rate || court?.price || 100000;
    let sum = 0;
    for (let hour = startHour; hour < endHour; hour += 1) {
      const slotStart = new Date(`${date}T${String(hour).padStart(2, "0")}:00:00`);
      const slotRate = getCourtSlotPrice ? getCourtSlotPrice(courtId, slotStart) : null;
      sum += Number.isFinite(slotRate) ? slotRate : baseRate;
    }
    return sum;
  };

  let bookingLogsMap = {};

  const setBookingLogs = (logs = []) => {
    bookingLogsMap = {};
    (logs || []).forEach((log) => {
      const id = log.booking_id;
      if (!id) return;
      if (!bookingLogsMap[id]) {
        bookingLogsMap[id] = log;
      }
    });
  };

  const getHistoryForBooking = (bookingId) => {
    if (!bookingId) return null;
    return bookingLogsMap[bookingId] || null;
  };

  const formatHistoryBadge = (entry, booking, startDate) => {
    const actionLabel = entry
      ? entry.action === "cancelled"
        ? "Manager đã hủy"
        : `Manager ${entry.action || "đã cập nhật"}`
      : booking?.note?.includes("[Walk-in]")
        ? "Manager Walk-in"
        : "Khách booking online";
    const timestamp = entry ? new Date(entry.created_at) : startDate;
    const formatted = timestamp && !Number.isNaN(timestamp.getTime())
      ? timestamp.toLocaleString("vi-VN", {
          hour: "2-digit",
          minute: "2-digit",
          day: "2-digit",
          month: "2-digit",
        })
      : "Không xác định";
    const detail = entry?.note ? ` (${entry.note})` : "";
    return `
      <div style="font-size:12px; color:#0f172a;">
        <strong>${actionLabel}${detail}</strong><br />
        <span class="muted">${formatted}</span>
      </div>
    `;
  };
 
  const fetchBookingLogs = async (facilityId, dateStr) => {
    if (!facilityId) return;
    try {
      const logs = await window.api.booking.logsByFacility(facilityId, dateStr);
      setBookingLogs(Array.isArray(logs) ? logs : []);
    } catch (err) {
      console.error("[ManagerBooking] Failed to fetch booking logs:", err);
      setBookingLogs([]);
    }
  };

  const parseBookingDate = (source) => {
    if (!source) return null;
    if (source instanceof Date) return source;
    const parser = window.SharedUtils?.parseBookingDateTime;
    if (typeof source === "string") {
      const normalized = parser ? parser(source) : new Date(source);
      if (normalized instanceof Date && !Number.isNaN(normalized.getTime())) return normalized;
      return new Date(source);
    }
    return null;
  };

  const resolveBookingSlot = (booking) => {
    if (!booking) return { start: null, end: null };
    const item = Array.isArray(booking.items) && booking.items.length > 0 ? booking.items[0] : null;
    const sources = [
      booking.start,
      booking.start_time,
      item?.start,
      item?.start_time,
      booking.startTime,
      booking.start_time_local,
    ];
    const ends = [
      booking.end,
      booking.end_time,
      item?.end,
      item?.end_time,
      booking.endTime,
      booking.end_time_local,
    ];
    const start = sources.map(parseBookingDate).find((date) => date && !Number.isNaN(date.getTime())) || null;
    const end = ends.map(parseBookingDate).find((date) => date && !Number.isNaN(date.getTime())) || null;
    return { start, end };
  };

  const renderBookingTable = (bookings, courts) => {
    if (!bookings || bookings.length === 0) {
      return `
        <div class="empty-state">
          <i class="fa-solid fa-inbox"></i>
          <p>Không có booking</p>
        </div>
      `;
    }

    const courtMap = {};
    (courts || []).forEach(c => {
      courtMap[c.id || c.court_id] = c.name || c.courtName;
    });

    let html = `
      <div class="bookings-table-wrapper">
        <table class="bookings-table">
          <thead>
            <tr>
              <th>STT</th>
              <th>Sân</th>
              <th>Ngày</th>
              <th>Giờ</th>
              <th>Lịch Sử</th>
              <th>Hành Động</th>
            </tr>
          </thead>
          <tbody>
    `;

    bookings.forEach((booking, bookingIndex) => {
      const courtName = courtMap[booking.courtId || booking.court_id] || `Sân #${booking.courtId || booking.court_id}`;
      const { start, end } = resolveBookingSlot(booking);
      const date = start ? start.toLocaleDateString('vi-VN') : 'Không xác định';
      const safeHours = (value) => (value instanceof Date ? String(value.getHours()).padStart(2, '0') : '??');
      const time =
        start && end ? `${safeHours(start)}:00 - ${safeHours(end)}:00` : 'Không xác định';
      const status = booking.status || booking.uiStatus || 'pending';
      const historyEntry = getHistoryForBooking(booking.id || booking.booking_id);
      const historyHtml = formatHistoryBadge(historyEntry, booking, start);
      const historyColumnHtml = `
        <div class="history-status-row" style="margin-bottom:4px;">${getStatusBadge(status)}</div>
        <div>${historyHtml}</div>
      `;

      html += `
        <tr>
          <td>${bookingIndex + 1}</td>
          <td>${courtName}</td>
          <td>${date}</td>
          <td>${time}</td>
          <td>${historyColumnHtml}</td>
          <td>
            <button class="btn-icon-small" onclick="ManagerBooking.deleteBooking(${booking.id || booking.booking_id})" title="Hủy">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        </tr>
      `;
    });

    html += `
          </tbody>
        </table>
      </div>
    `;

    return html;
  };

  const getStatusBadge = (status) => {
    const badges = {
      'pending': '<span class="badge badge-warning">Chờ Xác Nhận</span>',
      'confirmed': '<span class="badge badge-success">Đã Xác Nhận</span>',
      'cancelled': '<span class="badge badge-danger">Đã Hủy</span>',
      'completed': '<span class="badge badge-info">Hoàn Thành</span>',
    };
    return badges[status] || `<span class="badge badge-secondary">${status}</span>`;
  };

  const getPaymentBadge = (paymentStatus) => {
    const badges = {
      'paid': '<span class="badge badge-success">Đã Thanh Toán</span>',
      'unpaid': '<span class="badge badge-warning">Chưa Thanh Toán</span>',
      'failed': '<span class="badge badge-danger">Thất Bại</span>',
    };
    return badges[paymentStatus] || `<span class="badge badge-secondary">${paymentStatus}</span>`;
  };

  const renderTimeRangeFilter = () => {
    return `
      <div class="history-banner" style="background:#c2d9ff;padding:16px;border-radius:12px;margin-bottom:16px;font-size:14px;line-height:1.6;">
        <strong>Lịch sử Booking</strong>
      </div>
    `;
  };

  const renderWalkInForm = () => {
    return ``; // Removed walk-in form from history view
  };

  const renderBookingHistory = (logs = []) => {
    if (!logs || logs.length === 0) {
      return `
        <div class="empty-state" style="text-align: center; padding: 60px 20px; color: #94a3b8;">
          <i class="fa-solid fa-inbox" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
          <p style="font-size: 16px; margin: 0;">Chưa có lịch sử thay đổi nào</p>
          <p style="font-size: 14px; margin: 8px 0 0 0;">Các hành động booking sẽ được ghi lại tại đây</p>
        </div>
      `;
    }

    const formatActionType = (type) => {
      const icons = {
        'created': '<i class="fa-solid fa-plus-circle" style="color: #22c55e;"></i>',
        'updated': '<i class="fa-solid fa-pen-to-square" style="color: #3b82f6;"></i>',
        'cancelled': '<i class="fa-solid fa-ban" style="color: #ef4444;"></i>',
        'status_changed': '<i class="fa-solid fa-arrow-right-arrow-left" style="color: #f59e0b;"></i>',
        'payment_updated': '<i class="fa-solid fa-credit-card" style="color: #8b5cf6;"></i>'
      };
      const labels = {
        'created': 'Tạo Booking',
        'updated': 'Cập Nhật',
        'cancelled': 'Hủy Booking',
        'status_changed': 'Đổi Trạng Thái',
        'payment_updated': 'Thanh Toán'
      };
      return `${icons[type] || '<i class="fa-solid fa-circle"></i>'} ${labels[type] || type}`;
    };

    const formatRole = (role) => {
      const badges = {
        'customer': '<span style="background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">KHÁCH HÀNG</span>',
        'manager': '<span style="background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">QUẢN LÝ</span>',
        'staff': '<span style="background: #e0e7ff; color: #3730a3; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">NHÂN VIÊN</span>',
        'system': '<span style="background: #f3f4f6; color: #374151; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">HỆ THỐNG</span>'
      };
      return badges[role] || badges['system'];
    };

    const timelineHtml = logs.map(log => {
      const timestamp = new Date(log.created_at);
      const timeStr = timestamp.toLocaleString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });

      const statusChange = log.old_status && log.new_status
        ? `<div style="margin-top: 4px; font-size: 13px;"><strong>Trạng thái:</strong> <code style="background: #fee; padding: 2px 6px; border-radius: 3px;">${log.old_status}</code> → <code style="background: #efe; padding: 2px 6px; border-radius: 3px;">${log.new_status}</code></div>`
        : '';

      const paymentChange = log.old_payment_status && log.new_payment_status
        ? `<div style="margin-top: 4px; font-size: 13px;"><strong>Thanh toán:</strong> <code style="background: #fee; padding: 2px 6px; border-radius: 3px;">${log.old_payment_status}</code> → <code style="background: #efe; padding: 2px 6px; border-radius: 3px;">${log.new_payment_status}</code></div>`
        : '';

      return `
        <div class="timeline-item" style="position: relative; padding-left: 32px; padding-bottom: 24px; border-left: 2px solid #e2e8f0;">
          <div style="position: absolute; left: -9px; top: 4px; width: 16px; height: 16px; background: white; border: 2px solid #0ea5e9; border-radius: 50%;"></div>
          <div class="card" style="padding: 16px; margin-left: 16px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
              <div style="font-size: 15px; font-weight: 600; color: #0f172a;">
                ${formatActionType(log.action_type)}
              </div>
              <div style="text-align: right;">
                ${formatRole(log.changed_by_role || 'system')}
              </div>
            </div>
            <div style="margin-bottom: 8px;">
              <div style="font-size: 14px; color: #64748b;"><strong>Booking ID:</strong> #${log.booking_id}</div>
              <div style="font-size: 13px; color: #64748b; margin-top: 4px;"><i class="fa-solid fa-user"></i> ${log.customer_name || 'N/A'} • <i class="fa-solid fa-phone"></i> ${log.customer_phone || 'N/A'}</div>
            </div>
            ${statusChange}
            ${paymentChange}
            ${log.reason ? `<div style="margin-top: 8px; padding: 8px; background: #f8fafc; border-radius: 4px; font-size: 13px; color: #475569;"><i class="fa-solid fa-comment"></i> ${log.reason}</div>` : ''}
            <div style="margin-top: 12px; font-size: 12px; color: #94a3b8;">
              <i class="fa-solid fa-clock"></i> ${timeStr}
            </div>
          </div>
        </div>
      `;
    }).join('');

    return `
      <div class="booking-history-timeline" style="padding: 20px 0;">
        ${timelineHtml}
      </div>
    `;
  };

  const submitWalkIn = async () => {
    const name = document.getElementById("walkin-name")?.value.trim();
    const phone = document.getElementById("walkin-phone")?.value.trim();
    const email = document.getElementById("walkin-email")?.value.trim();
    const courtId = parseInt(document.getElementById("walkin-court")?.value || "", 10);
    const date = document.getElementById("walkin-date")?.value;
    const startHour = parseInt(document.getElementById("walkin-start-hour")?.value || "", 10);
    const endHour = parseInt(document.getElementById("walkin-end-hour")?.value || "", 10);
    const status = document.getElementById("walkin-status")?.value || "pending";
    const note = document.getElementById("walkin-note")?.value.trim();

    if (!name || !phone || !courtId || !date || startHour == null || endHour == null) {
      alert("Vui lòng điền đủ thông tin (*) bắt buộc");
      return;
    }

    if (endHour <= startHour) {
      alert("Giờ kết thúc phải lớn hơn giờ bắt đầu");
      return;
    }

    try {
      const startTime = new Date(`${date}T${String(startHour).padStart(2, '0')}:00:00`);
      const endTime = new Date(`${date}T${String(endHour).padStart(2, '0')}:00:00`);
      const court = window.state?.courts?.find((c) => (c.id || c.court_id) === courtId);

      const totalHours = endHour - startHour;
      const computedPrice = calculateSlotRangePrice(courtId, date, startHour, endHour);
      const fallbackRate = court?.hourly_rate || court?.price || 100000;
      const price = Number.isFinite(computedPrice) ? computedPrice : totalHours * fallbackRate;

      // Get facility ID from manager state
      const managerState = window.ManagerApp?.getState();
      const facilityId = managerState?.managerFacilityId;
      
      // console.log("[submitWalkIn] Manager state:", managerState);
      // console.log("[submitWalkIn] Facility ID:", facilityId);
      
      if (!facilityId) {
        alert("Vui lòng chọn cơ sở quản lý trước khi tạo booking.");
        return;
      }

      const toLocal = window.SharedUtils?.toLocalISOString;
      const localizedStart = toLocal ? toLocal(startTime) : startTime.toISOString();
      const localizedEnd = toLocal ? toLocal(endTime) : endTime.toISOString();

      const payload = {
        facility_id: facilityId,
        status: status,
        customer_name: name,
        customer_phone: phone,
        customer_email: email || null,
        items: [{
          court_id: courtId,
          start_time: localizedStart,
          end_time: localizedEnd,
          price: price,
        }],
        note: note ? `[Walk-in] ${note}` : '[Walk-in]',
      };

      // console.log("[submitWalkIn] Creating booking:", payload);

      const res = await window.api.booking.create(payload);
      if (!res || !res.data) {
        throw new Error("Không tạo được booking");
      }

      const bookingData = res.data;
      
      window.showToast("  Booking #" + bookingData.booking_id + " tạo thành công!");
      resetWalkInForm();
      
      // Update manager date to match the booking date
      if (window.ManagerApp) {
        const managerState = window.ManagerApp.getState();
        
        // If dates don't match, update manager date
        if (managerState.managerDate !== date) {
          // console.log("[submitWalkIn] Updating manager date to match booking...");
          managerState.managerDate = date;
          
          // Update the date input
          const dateInput = document.getElementById('mgr-date-select-global');
          if (dateInput) {
            dateInput.value = date;
          }
        }
        
        const currentTab = window.ManagerApp.getCurrentTab();
        
        // If not on courts tab, switch to it
        if (currentTab !== 'courts') {
          window.ManagerApp.switchTab('courts');
          await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        // Clear cache and refresh immediately
        if (window.ManagerApp.clearCache) {
          window.ManagerApp.clearCache();
        }
        
        // Refresh courts tab with force refresh
        await window.ManagerApp.refreshCourtsTab(true);
        
        window.showToast("  Đã cập nhật timeline!");
      } else {
        console.error("[submitWalkIn] ManagerApp not available!");
      }
    } catch (err) {
      console.error("[submitWalkIn] Error:", err);
      alert("Lỗi tạo booking: " + err.message);
    }
  };

  const resetWalkInForm = () => {
    document.getElementById("walkin-name").value = "";
    document.getElementById("walkin-phone").value = "";
    document.getElementById("walkin-email").value = "";
    document.getElementById("walkin-court").value = "";
    document.getElementById("walkin-start-hour").value = "8";
    document.getElementById("walkin-end-hour").value = "9";
    document.getElementById("walkin-status").value = "pending";
    document.getElementById("walkin-note").value = "";
  };

  const updateBookingStatus = async (bookingId, newStatus) => {
    try {
      // console.log(`[updateBookingStatus] Updating booking ${bookingId} to status: ${newStatus}`);
      
      // Call API to update booking status
      const res = await window.api.booking.updateStatus(bookingId, newStatus);
      
      // console.log("[updateBookingStatus] Result:", res);
      
      const statusMessages = {
        'pending': 'Booking đã chuyển sang trạng thái: Chờ Xác Nhận',
        'confirmed': 'Booking đã được Xác Nhận!',
        'cancelled': 'Booking đã bị Hủy!'
      };
      
      window.showToast(statusMessages[newStatus] || 'Cập nhật trạng thái thành công!');
      // Small delay to ensure DB is updated
      await new Promise(resolve => setTimeout(resolve, 300));
      await refreshManagerViews();
    } catch (err) {
      console.error("[updateBookingStatus] Error:", err);
      alert("Lỗi cập nhật trạng thái: " + err.message);
      // Refresh to revert the dropdown
      await refreshManagerViews();
    }
  };

  const deleteBooking = async (bookingId) => {
    if (!confirm("Bạn chắc chắn muốn hủy booking này?")) {
      return;
    }

    try {
      // console.log("[deleteBooking] Cancelling booking:", bookingId);
      
      const res = await window.api.booking.cancel(bookingId, {
        reason: "Manager hủy tại chỗ",
      });

      // console.log("[deleteBooking] Result:", res);
      
      window.showToast("Booking đã được hủy!");
      await refreshManagerViews();
    } catch (err) {
      console.error("[deleteBooking] Error:", err);
      alert("Lỗi hủy booking: " + err.message);
    }
  };

  const refreshManagerViews = async () => {
    if (!window.ManagerApp) return;
    if (typeof window.ManagerApp.clearCache === "function") {
      window.ManagerApp.clearCache();
    }
    const tasks = [];
    if (typeof window.ManagerApp.refreshCourtsTab === "function") {
      tasks.push(window.ManagerApp.refreshCourtsTab(true));
    }
    if (typeof window.ManagerApp.refreshBookingsTab === "function") {
      tasks.push(window.ManagerApp.refreshBookingsTab(true));
    }
    await Promise.all(tasks);
  };

  const showBookingDetailModal = async (bookingId) => {
    // console.log("[showBookingDetailModal] Loading booking details for:", bookingId);
    
    try {
      // Tìm booking từ state hoặc gọi API
      let booking = null;
      if (window.state && window.state.bookings) {
        booking = window.state.bookings.find(b => (b.id || b.booking_id) === bookingId);
      }
      
      if (!booking) {
        // Nếu không tìm thấy trong state, gọi API để lấy chi tiết
        const response = await window.api.booking.get(bookingId);
        booking = response.data || response;
      }
      
      if (!booking) {
        window.showToast("   Không tìm thấy thông tin booking");
        return;
      }
      
      // Parse booking data
      const courtId = booking.courtId || booking.court_id || booking.items?.[0]?.court_id;
      const courtName = getCourtNameFromId(courtId);
      
      // Handle both normalized and raw booking formats
      let { start, end } = resolveBookingSlot(booking);
      let customer, phone, email;
      
      // Get customer info from new fields, fallback to parsing note for old data
      customer = booking.customer_name || booking.customer || 'N/A';
      phone = booking.customer_phone || booking.phone || 'N/A';
      email = booking.customer_email || booking.email || 'N/A';
      
      // Fallback: parse from note for old bookings (backward compatibility)
      if (customer === 'N/A' && booking.note) {
        const noteMatch = booking.note.match(/Khách: (.+?)\s*\|/);
        if (noteMatch) customer = noteMatch[1];
        
        const phoneMatch = booking.note.match(/SDT: (.+?)\s*\|/);
        if (phoneMatch) phone = phoneMatch[1];
        
        const emailMatch = booking.note.match(/Email: (.+?)\s*\|/);
        if (emailMatch) email = emailMatch[1];
      }
      
      const date = start ? start.toLocaleDateString('vi-VN') : 'Không xác định';
      const safeHours = (value) => (value instanceof Date ? String(value.getHours()).padStart(2, '0') : '??');
      const time = start && end
        ? `${safeHours(start)}:00 - ${safeHours(end)}:00`
        : 'Không xác định';
      const status = booking.status || booking.uiStatus || 'pending';
      const total = booking.total || booking.items?.[0]?.price || '0';
      const source = booking.note?.includes('[Walk-in]') ? 'Manager (tại chỗ)' : 'Customer (online)';
      
      // Tạo modal HTML với thông tin đầy đủ và các hành động
      const canCancel = status !== 'cancelled';
      const modalHtml = `
        <div id="bookingDetailModal" class="modal show" style="display: flex !important;">
          <div class="modal-content" style="max-width: 550px;">
            <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 2px solid #e2e8f0;">
              <h3 style="margin: 0; color: #0f172a; font-size: 20px;">
                <i class="fa-solid fa-calendar-check" style="color: #0ea5e9; margin-right: 8px;"></i>
                Chi Tiết Booking #${bookingId}
              </h3>
              <span class="close-btn" onclick="document.getElementById('bookingDetailModal').remove()" style="cursor: pointer; font-size: 24px; color: #64748b;">&times;</span>
            </div>
            <div class="modal-body" style="padding: 24px;">
              <div class="booking-detail-grid" style="display: grid; gap: 16px;">
                <div class="detail-section" style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 4px solid #0ea5e9;">
                  <h4 style="margin: 0 0 12px 0; color: #475569; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <i class="fa-solid fa-user"></i> Thông Tin Khách Hàng
                  </h4>
                  <div style="display: grid; gap: 8px;">
                    <div><strong>Tên:</strong> ${customer}</div>
                    <div><strong>SĐT:</strong> ${phone}</div>
                    <div><strong>Email:</strong> ${email}</div>
                  </div>
                </div>
                
                <div class="detail-section" style="background: #f0fdf4; padding: 16px; border-radius: 8px; border-left: 4px solid #22c55e;">
                  <h4 style="margin: 0 0 12px 0; color: #475569; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <i class="fa-solid fa-map-marker-alt"></i> Thông Tin Đặt Sân
                  </h4>
                  <div style="display: grid; gap: 8px;">
                    <div><strong>Sân:</strong> ${courtName}</div>
                    <div><strong>Ngày:</strong> ${date}</div>
                    <div><strong>Giờ:</strong> ${time}</div>
                    <div><strong>Nguồn:</strong> <span style="color: #0ea5e9; font-weight: 600;">${source}</span></div>
                  </div>
                </div>
                
                <div class="detail-section" style="background: #fef9c3; padding: 16px; border-radius: 8px; border-left: 4px solid #eab308;">
                  <h4 style="margin: 0 0 12px 0; color: #475569; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <i class="fa-solid fa-money-bill"></i> Thanh Toán
                  </h4>
                  <div style="display: grid; gap: 8px;">
                    <div><strong>Tổng tiền:</strong> <span style="font-weight: 700; color: #16a34a; font-size: 18px;">${window.formatCurrency(total)}</span></div>
                  </div>
                </div>
                
                <div class="detail-section" style="background: #ede9fe; padding: 16px; border-radius: 8px; border-left: 4px solid #a855f7;">
                  <h4 style="margin: 0 0 12px 0; color: #475569; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <i class="fa-solid fa-check-circle"></i> Trạng Thái & Hành Động
                  </h4>
                  <div style="display: grid; gap: 8px;">
                    <div><strong>Trạng thái hiện tại:</strong> ${getStatusBadge(status)}</div>
                    <div style="margin-top: 8px;">
                      <label for="modal-status-select" style="display: block; margin-bottom: 6px; color: #64748b; font-weight: 600;">Thay đổi trạng thái:</label>
                      <select id="modal-status-select" style="width: 100%; padding: 10px; border-radius: 8px; border: 2px solid #cbd5e1; font-size: 14px; background: white; cursor: pointer;">
                        <option value="pending" ${status === 'pending' ? 'selected' : ''}>Chờ Xác Nhận</option>
                        <option value="confirmed" ${status === 'confirmed' ? 'selected' : ''}>  Xác Nhận</option>
                        <option value="cancelled" ${status === 'cancelled' ? 'selected' : ''}>   Hủy</option>
                      </select>
                    </div>
                  </div>
                </div>
                
              </div>
            </div>
            <div class="modal-footer" style="display: flex; gap: 10px; justify-content: space-between; padding: 16px; border-top: 1px solid #e2e8f0; background: #f8fafc;">
              <button class="btn-outline" onclick="document.getElementById('bookingDetailModal').remove()" style="padding: 10px 20px; border: 2px solid #cbd5e1; background: white; border-radius: 8px; font-weight: 600; cursor: pointer;">
                <i class="fa-solid fa-times"></i> Đóng
              </button>
              <button class="btn-primary" onclick="ManagerBooking.updateStatusFromModal(${bookingId})" style="padding: 10px 20px; border: none; background: #0ea5e9; color: white; border-radius: 8px; font-weight: 600; cursor: pointer;">
                <i class="fa-solid fa-save"></i> Cập Nhật Trạng Thái
              </button>
            </div>
          </div>
        </div>
      `;
      
      // Xóa modal cũ nếu có
      const existingModal = document.getElementById('bookingDetailModal');
      if (existingModal) existingModal.remove();
      
      // Thêm modal mới vào body
      document.body.insertAdjacentHTML('beforeend', modalHtml);
      
    } catch (err) {
      console.error("[showBookingDetailModal] Error:", err);
      window.showToast("   Lỗi tải thông tin booking: " + err.message);
    }
  };
  
  const getCourtNameFromId = (courtId) => {
    if (window.state && window.state.courts) {
      const court = window.state.courts.find(c => (c.id || c.court_id) === courtId);
      if (court) return court.name || court.courtName || `Sân #${courtId}`;
    }
    return `Sân #${courtId}`;
  };

  const cancelBookingFromModal = async (bookingId) => {
    const confirmed = confirm("Bạn có chắc muốn hủy booking này không?");
    if (!confirmed) return;
    
    try {
      await updateBookingStatus(bookingId, 'cancelled');
      
      // Close modal
      const modal = document.getElementById('bookingDetailModal');
      if (modal) modal.remove();
      
      window.showToast("  Đã hủy booking thành công");
    } catch (err) {
      console.error("[cancelBookingFromModal] Error:", err);
      window.showToast("   Lỗi hủy booking: " + err.message);
    }
  };

  const updateStatusFromModal = async (bookingId) => {
    const selectElement = document.getElementById('modal-status-select');
    if (!selectElement) {
      console.error("[updateStatusFromModal] Select element not found");
      return;
    }
    
    const newStatus = selectElement.value;
    
    try {
      // console.log(`[updateStatusFromModal] Updating booking ${bookingId} to status: ${newStatus}`);
      
      // Call API to update booking status
      const res = await window.api.booking.updateStatus(bookingId, newStatus);
      
      // console.log("[updateStatusFromModal] Result:", res);
      
      const statusMessages = {
        'pending': 'Booking đã chuyển sang trạng thái: Chờ Xác Nhận',
        'confirmed': '  Booking đã được Xác Nhận!',
        'cancelled': '   Booking đã bị Hủy!'
      };
      
      window.showToast(statusMessages[newStatus] || 'Cập nhật trạng thái thành công!');

      // Small delay to ensure DB is updated
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const modal = document.getElementById('bookingDetailModal');
      if (modal) modal.remove();

      await refreshManagerViews();
    } catch (err) {
      console.error("[updateStatusFromModal] Error:", err);
      window.showToast("   Lỗi cập nhật trạng thái: " + err.message);
    }
  };

  const logManagerAction = ({ bookingId = null, action, detail = "", contextId = null }) => {
    if (!action || !bookingId) return;
    const facilityId = window.ManagerApp?.getState()?.managerFacilityId;
    const dateStr = window.ManagerApp?.getState()?.managerDate;
    window.api.booking
      .logAction(bookingId, { action, note: detail })
      .then(() => fetchBookingLogs(facilityId, dateStr))
      .catch((err) => console.error("[ManagerBooking] logManagerAction error:", err));
  };

  const refreshBookingLogs = async (facilityId, dateStr) => {
    await fetchBookingLogs(facilityId, dateStr);
  };

  const getBookingLogs = () => {
    return Object.values(bookingLogsMap || {});
  };

  return {
    renderBookingTable,
    renderWalkInForm,
    renderBookingHistory,
    renderTimeRangeFilter,
    submitWalkIn,
    resetWalkInForm,
    updateBookingStatus,
    deleteBooking,
    showBookingDetailModal,
    cancelBookingFromModal,
    updateStatusFromModal,
    logManagerAction,
    refreshBookingLogs,
    getBookingLogs,
  };
})();

window.ManagerBooking = ManagerBooking;
