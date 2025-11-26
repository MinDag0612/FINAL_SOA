const ManagerBooking = (() => {
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
              <th>Khách</th>
              <th>SDT</th>
              <th>Email</th>
              <th>Sân</th>
              <th>Ngày</th>
              <th>Giờ</th>
              <th>Trạng Thái</th>
              <th>Thanh Toán</th>
              <th>Tổng Tiền</th>
              <th>Hành Động</th>
            </tr>
          </thead>
          <tbody>
    `;

    bookings.forEach(booking => {
      const courtName = courtMap[booking.courtId || booking.court_id] || `Sân #${booking.courtId || booking.court_id}`;
      // Handle both normalized booking (start/end as Date objects) and raw booking (start_time/end_time as strings)
      const start = booking.start instanceof Date ? booking.start : new Date(booking.start_time || booking.start);
      const end = booking.end instanceof Date ? booking.end : new Date(booking.end_time || booking.end);
      const date = start.toLocaleDateString('vi-VN');
      const time = `${String(start.getHours()).padStart(2, '0')}:00 - ${String(end.getHours()).padStart(2, '0')}:00`;
      const status = booking.status || booking.uiStatus || 'pending';
      const paymentStatus = booking.payment_status || booking.paymentStatus || 'unpaid';
      const total = booking.total || '0';
      
      let customer = booking.customer || booking.customer_name || 'N/A';
      let phone = booking.phone || booking.customer_phone || 'N/A';
      let email = booking.email || booking.customer_email || 'N/A';
      
      if (customer === 'N/A' && booking.note) {
        const noteMatch = booking.note.match(/Khách: (.+?)\s*\|/);
        if (noteMatch) customer = noteMatch[1];
        
        const phoneMatch = booking.note.match(/SDT: (.+?)\s*\|/);
        if (phoneMatch) phone = phoneMatch[1];
        
        const emailMatch = booking.note.match(/Email: (.+?)\s*\|/);
        if (emailMatch) email = emailMatch[1];
      }

      const statusBadge = getStatusBadge(status);
      const paymentBadge = getPaymentBadge(paymentStatus);

      html += `
        <tr>
          <td><strong>${customer}</strong></td>
          <td>${phone}</td>
          <td>${email}</td>
          <td>${courtName}</td>
          <td>${date}</td>
          <td>${time}</td>
          <td>${statusBadge}</td>
          <td>${paymentBadge}</td>
          <td>${window.formatCurrency(total)}</td>
          <td>
            <button class="btn-icon-small" onclick="ManagerBooking.deleteBooking(${booking.id})" title="Hủy">
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

  const renderWalkInForm = (courts) => {
    // Use manager selected date, fallback to today
    const selectedDate = window.state?.managerDate || new Date().toISOString().split('T')[0];
    
    return `
      <div class="walkin-form">
        <h4>Tạo Booking Tại Chỗ</h4>
        <div class="form-grid">
          <div class="form-group">
            <label>Tên Khách *</label>
            <input type="text" id="walkin-name" placeholder="Nhập tên khách" />
          </div>
          <div class="form-group">
            <label>Số Điện Thoại *</label>
            <input type="text" id="walkin-phone" placeholder="Nhập SDT" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" id="walkin-email" placeholder="Email (tùy chọn)" />
          </div>
          <div class="form-group">
            <label>Sân *</label>
            <select id="walkin-court">
              <option value="">Chọn sân</option>
              ${(courts || []).map(c => `<option value="${c.id || c.court_id}">${c.name || c.courtName}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Ngày *</label>
            <input type="date" id="walkin-date" value="${selectedDate}" />
          </div>
          <div class="form-group">
            <label>Giờ Bắt Đầu *</label>
            <select id="walkin-start-hour">
              ${Array.from({length: 24}, (_, i) => i).map(h => `<option value="${h}">${String(h).padStart(2, '0')}:00</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Giờ Kết Thúc *</label>
            <select id="walkin-end-hour">
              ${Array.from({length: 24}, (_, i) => i + 1).map(h => `<option value="${h}">${String(h).padStart(2, '0')}:00</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Ghi Chú</label>
            <textarea id="walkin-note" placeholder="Ghi chú thêm (tùy chọn)" rows="2"></textarea>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn-primary" onclick="ManagerBooking.submitWalkIn()">Tạo Booking</button>
          <button class="btn-outline" onclick="ManagerBooking.resetWalkInForm()">Nhập Lại</button>
        </div>
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

      const totalHours = endHour - startHour;
      const price = totalHours * 100000;

      const facilityId = window.state?.managerFacilityId || window.state?.selectedFacilityId;
      if (!facilityId) {
        alert("Vui lòng chọn cơ sở quản lý trước khi tạo booking.");
        return;
      }

      const payload = {
        facility_id: facilityId,
        items: [{
          court_id: courtId,
          start_time: startTime.toISOString(),
          end_time: endTime.toISOString(),
          price: price,
        }],
        note: `[Walk-in] Khách: ${name} | SDT: ${phone} | Email: ${email || 'N/A'} | ${note || ''}`,
      };

      console.log("[submitWalkIn] Creating booking:", payload);

      const res = await window.api.booking.create(payload);
      if (!res || !res.data) {
        throw new Error("Không tạo được booking");
      }

      console.log("[submitWalkIn] Booking created:", res.data);
      
      window.showToast("Booking tại chỗ tạo thành công!");
      resetWalkInForm();
      
      // Small delay to ensure database transaction is committed
      await new Promise(resolve => setTimeout(resolve, 500));
      
      console.log("[submitWalkIn] Refreshing manager view...");
      if (typeof window.refreshManagerView === "function") {
        console.log("[submitWalkIn] Calling window.refreshManagerView");
        await window.refreshManagerView();
        console.log("[submitWalkIn] Refresh completed");
      } else if (typeof window.refreshManagerBookings === "function") {
        console.log("[submitWalkIn] Calling window.refreshManagerBookings");
        await window.refreshManagerBookings();
        console.log("[submitWalkIn] Refresh completed");
      } else {
        console.error("[submitWalkIn] No refresh function available!");
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
    document.getElementById("walkin-note").value = "";
  };

  const deleteBooking = async (bookingId) => {
    if (!confirm("Bạn chắc chắn muốn hủy booking này?")) {
      return;
    }

    try {
      console.log("[deleteBooking] Cancelling booking:", bookingId);
      
      const res = await window.api.booking.cancel(bookingId, {
        reason: "Manager hủy tại chỗ",
      });

      console.log("[deleteBooking] Result:", res);
      
      window.showToast("Booking đã được hủy!");

      console.log("[deleteBooking] Refreshing manager view...");
      if (typeof window.refreshManagerView === "function") {
        await window.refreshManagerView();
      } else if (typeof window.refreshManagerBookings === "function") {
        await window.refreshManagerBookings();
      } else {
        console.error("[deleteBooking] No refresh function available!");
      }
    } catch (err) {
      console.error("[deleteBooking] Error:", err);
      alert("Lỗi hủy booking: " + err.message);
    }
  };

  return {
    renderBookingTable,
    renderWalkInForm,
    submitWalkIn,
    resetWalkInForm,
    deleteBooking,
  };
})();

window.ManagerBooking = ManagerBooking;
