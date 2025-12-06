const ManagerCourts = (() => {
  const { isSameDate, getCourtSlotPrice, getManagerSegmentsForCourt } = window.SharedUtils || {};
  const parseDateSafe = (value) => {
    if (!value) return null;
    const date = value instanceof Date ? value : new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  };
  const isBookingActive = (booking, targetDate) => {
    const start = parseDateSafe(booking.start_time || booking.start);
    if (!start) return false;
    if (targetDate && !isSameDate(start, targetDate)) return false;
    const uiStatus = (booking.uiStatus || booking.status || "").toLowerCase();
    return !["cancelled", "expired"].includes(uiStatus);
  };
  const getActiveBookings = (bookings = [], targetDate) =>
    bookings.filter((booking) => isBookingActive(booking, targetDate));

  const overlapsFilter = (booking, filter) => {
    if (!filter || !filter.enabled) return false;
    const start = parseDateSafe(booking.start_time || booking.start);
    const end = parseDateSafe(booking.end_time || booking.end);
    if (!start || !end) return false;
    const bookingStart = start.getHours() + start.getMinutes() / 60;
    const bookingEnd = end.getHours() + end.getMinutes() / 60;
    const filterStart = Number(filter.startHour);
    const filterEnd = Number(filter.endHour) + 1;
    return bookingStart < filterEnd && bookingEnd > filterStart;
  };

  const isSlotWithinFilter = (hour, filter) => {
    if (!filter || !filter.enabled) return true;
    return hour >= filter.startHour && hour <= filter.endHour;
  };

  const renderCourtsSection = (courts, bookings, selectedDate, timeFilter) => {
    // console.log("[ManagerCourts.renderCourtsSection] courts:", courts.length, "bookings:", bookings.length, "selectedDate:", selectedDate);
    if (!courts || courts.length === 0) {
      return `
        <div class="empty-state">
          <i class="fa-solid fa-ban"></i>
          <p>Không có sân nào</p>
        </div>
      `;
    }

    const slots = Array.from({ length: 24 }, (_, i) => i);
    const targetDate = selectedDate || new Date().toISOString().split("T")[0];
    const activeBookings = getActiveBookings(bookings, targetDate);
    const filterActive = Boolean(timeFilter?.enabled);
    
    let html = `
      <div class="courts-grid">
        <table class="courts-table">
          <thead>
            <tr>
              <th style="width: 150px;">Tên Sân</th>
              <th style="width: 100px;">Loại</th>
              <th style="width: 100px;">Giá/h</th>
              <th>Timeline Booking</th>
            </tr>
          </thead>
          <tbody>
    `;

    
    let renderedRows = 0;
    courts.forEach(court => {
      const courtId = court.id || court.court_id;
      const courtBookings = activeBookings.filter(b => {
        const bCourtId = b.courtId || b.court_id;
        return bCourtId === courtId;
      });
      const matchesFilter = filterActive ? courtBookings.some((booking) => overlapsFilter(booking, timeFilter)) : true;
      if (filterActive && !matchesFilter) {
        return;
      }
      const slotBookingMap = new Map();
      const slotStatusMap = new Map();
      courtBookings.forEach(booking => {
        const start = parseDateSafe(booking.start_time || booking.start);
        const end = parseDateSafe(booking.end_time || booking.end);
        if (!start || !end) return;
        for (let h = start.getHours(); h < end.getHours(); h++) {
          slotBookingMap.set(h, booking);
          slotStatusMap.set(h, (booking.uiStatus || booking.status || "").toLowerCase());
        }
      });

      let timelineHtml = `<div class="timeline-row">`;
        slots.forEach(h => {
          const slotClass = slotBookingMap.has(h)
            ? slotStatusMap.get(h) === "booked"
              ? "slot-pending"
              : "slot-booked"
            : "slot-free";
          const booking = slotBookingMap.get(h);
          const bookingId = booking ? booking.booking_id || booking.id : null;
          const clickHandler = booking
            ? `onclick="ManagerCourts.viewBookingDetails(${bookingId})"`
            : `onclick="ManagerCourts.openWalkInFormForSlot(${courtId}, ${h}, '${targetDate}')"`; 
          
          const slotStart = new Date(targetDate);
          slotStart.setHours(h, 0, 0, 0);
          const slotPrice = typeof getCourtSlotPrice === "function"
            ? getCourtSlotPrice(courtId, slotStart)
            : court.hourlyRate || court.price || court.hourly_rate || 100000;
          const priceLabel = window.formatCurrency(slotPrice);
          const slotLabel = `${String(h).padStart(2, '0')}:00`;
          const tooltipParts = [slotLabel, `Giá: ${priceLabel}`];
          if (booking) {
            tooltipParts.unshift(booking.customer || booking.customer_name || "Khách hàng");
          }
          const tooltip = tooltipParts.join(" · ");

          const slotExtraClass = isSlotWithinFilter(h, timeFilter) ? "" : "slot-outside";
          timelineHtml += `<div class="timeline-slot ${slotClass} ${slotExtraClass} clickable" title="${tooltip}" ${clickHandler}>${h}</div>`;
        });
      timelineHtml += `</div>`;
      const segments = typeof getManagerSegmentsForCourt === "function"
        ? getManagerSegmentsForCourt(courtId)
        : [];
      const segmentBadges = segments.length
        ? `<div class="segment-badges">${segments
            .map(
              (segment) =>
                `<span class="segment-badge">${segment.startLabel} - ${segment.endLabel} · ${window.formatCurrency(
                  segment.price
                )}</span>`
            )
            .join("")}</div>`
        : "";
      const timelineWithSegments = `${timelineHtml}${segmentBadges}`;

      renderedRows += 1;
      html += `
        <tr>
          <td><strong>${court.name || court.courtName}</strong></td>
          <td>${court.type || court.surface_type || '--'}</td>
          <td>${window.formatCurrency(court.hourly_rate || court.price || 100000)}</td>
          <td>${timelineWithSegments}</td>
        </tr>
      `;
    });

    if (filterActive) {
      if (renderedRows === 0) {
        html += `
          <tr>
            <td colspan="4" class="courts-filter-empty">
              Không có sân nào được đặt trong ca ${String(timeFilter.startHour).padStart(2, '0')}:00 – ${String(timeFilter.endHour).padStart(2, '0')}:00.
            </td>
          </tr>
        `;
      } else {
        html += `
          <tr>
            <td colspan="4" class="courts-filter-summary">
              Đang hiển thị ${renderedRows} sân có booking trong ca ${String(timeFilter.startHour).padStart(2, '0')}:00 – ${String(timeFilter.endHour).padStart(2, '0')}:00.
            </td>
          </tr>
        `;
      }
    }

    html += `
          </tbody>
        </table>
      </div>
      <div class="legend-row">
        <div><span class="legend-box slot-free"></span> Trống</div>
        <div><span class="legend-box slot-booked"></span> Đã đặt</div>
      </div>
    `;

    return html;
  };

  const calculateHoursByCourt = (courts = [], bookings = [], selectedDate) => {
    const result = {};
    const activeBookings = getActiveBookings(bookings, selectedDate);
    
    courts.forEach(court => {
      const courtId = court.id || court.court_id;
      const courtBookings = activeBookings.filter(b => {
        const bCourtId = b.courtId || b.court_id;
        return bCourtId === courtId;
      });

      let totalHours = 0;
      courtBookings.forEach(booking => {
        const start = parseDateSafe(booking.start_time || booking.start);
        const end = parseDateSafe(booking.end_time || booking.end);
        if (!start || !end) return;
        const hours = (end - start) / (1000 * 60 * 60);
        totalHours += hours;
      });

      result[courtId] = totalHours;
    });

    return result;
  };

  const countCourtsWithFilterMatches = (courts = [], bookings = [], selectedDate, filter) => {
    if (!filter || !filter.enabled) return 0;
    const activeBookings = getActiveBookings(bookings, selectedDate);
    const courtsSet = new Set();
    activeBookings.forEach((booking) => {
      if (overlapsFilter(booking, filter)) {
        const courtId = booking.court_id || booking.courtId;
        if (courtId) courtsSet.add(courtId);
      }
    });
    return courtsSet.size;
  };

  const renderCourtsStats = (courts, bookings, dateStr, timeFilter) => {
    const totalCourts = courts.length;
    const activeBookings = getActiveBookings(bookings, dateStr);
    const totalBookings = activeBookings.length;
    const hoursByCourtId = calculateHoursByCourt(courts, bookings, dateStr);
    const totalHours = Object.values(hoursByCourtId).reduce((sum, h) => sum + h, 0);
    const filterActive = Boolean(timeFilter?.enabled);
    const filteredCourts = countCourtsWithFilterMatches(courts, bookings, dateStr, timeFilter);
    const filterInfo = filterActive
      ? `<div class="stats-filter-note">
           Ca ${String(timeFilter.startHour).padStart(2, '0')}:00 – ${String(timeFilter.endHour).padStart(2, '0')}:00 · ${filteredCourts} sân đang có booking
         </div>`
      : "";

    return `
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon"><i class="fa-solid fa-map-marker-alt"></i></div>
          <div class="stat-content">
            <div class="stat-label">Tổng Sân</div>
            <div class="stat-value">${totalCourts}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <div class="stat-content">
            <div class="stat-label">Booking Hôm Nay</div>
            <div class="stat-value">${totalBookings}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><i class="fa-solid fa-clock"></i></div>
          <div class="stat-content">
            <div class="stat-label">Tổng Giờ Đặt</div>
            <div class="stat-value">${totalHours.toFixed(1)}h</div>
          </div>
        </div>
      </div>
      ${filterInfo}
    `;
  };

  const viewBookingDetails = (bookingId) => {
    // console.log('[ManagerCourts.viewBookingDetails] Booking ID:', bookingId);
    if (!bookingId) {
      window.showToast('   Không tìm thấy thông tin booking');
      return;
    }
    
    // Gọi hàm hiển thị modal từ ManagerBooking
    if (window.ManagerBooking && typeof window.ManagerBooking.showBookingDetailModal === 'function') {
      window.ManagerBooking.showBookingDetailModal(bookingId);
    } else {
      console.error('[ManagerCourts.viewBookingDetails] ManagerBooking.showBookingDetailModal not found');
      window.showToast('   Chức năng xem chi tiết chưa sẵn sàng');
    }
  };
  
  const openWalkInFormForSlot = (courtId, hour, date) => {
    // console.log('[ManagerCourts.openWalkInFormForSlot] Court:', courtId, 'Hour:', hour, 'Date:', date);
    
    // Find court name
    const court = window.state.courts.find(c => (c.id || c.court_id) === courtId);
    const courtName = court ? (court.name || court.courtName || `Sân #${courtId}`) : `Sân #${courtId}`;
    
    // Pre-fill walk-in modal data
    window.walkInModalData = {
      courtId,
      courtName,
      date,
      hour,
      facilityId: window.ManagerApp?.getState().managerFacilityId
    };
    
    // Open modal and populate
    window.ManagerApp.openWalkInModal(courtId, courtName, date, hour);
    
    window.showToast(`  Đặt sân ${courtName} lúc ${hour}:00`);
  };

  const api = {
    renderCourtsSection,
    renderCourtsStats,
    calculateHoursByCourt,
    viewBookingDetails,
    openWalkInFormForSlot,
  };
  return api;
})();

window.ManagerCourts = ManagerCourts;
window.calculateHoursByCourt = ManagerCourts.calculateHoursByCourt;
