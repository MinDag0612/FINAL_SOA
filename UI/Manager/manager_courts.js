const ManagerCourts = (() => {
  const parseDateSafe = (value) => {
    if (!value) return null;
    const date = value instanceof Date ? value : new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  };

  const renderCourtsSection = (courts, bookings, selectedDate) => {
    console.log("[ManagerCourts.renderCourtsSection] courts:", courts.length, "bookings:", bookings.length);
    
    if (!courts || courts.length === 0) {
      return `
        <div class="empty-state">
          <i class="fa-solid fa-ban"></i>
          <p>Không có sân nào</p>
        </div>
      `;
    }

    const slots = Array.from({ length: 24 }, (_, i) => i);
    
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

    courts.forEach(court => {
      const courtBookings = bookings.filter(b => b.courtId === court.id || b.court_id === court.id);
      if (courtBookings.length > 0) {
        console.log(`[ManagerCourts] Court ${court.name} (id=${court.id}) has ${courtBookings.length} bookings:`, courtBookings);
      }
      
      // Map slot hours to their booking status: confirmed=booked (red), pending=pending (yellow), else=free (white)
      const slotStatus = {};
      courtBookings.forEach(booking => {
        const start = parseDateSafe(booking.start_time || booking.start);
        const end = parseDateSafe(booking.end_time || booking.end);
        if (!start || !end) {
          console.warn("[ManagerCourts] Invalid booking time range", booking);
          return;
        }
        const bookingStatus = booking.status || booking.uiStatus || 'pending';
        for (let h = start.getHours(); h < end.getHours(); h++) {
          // Only show color for confirmed (red) or pending (yellow), cancelled/expired = white
          if (bookingStatus === 'confirmed') {
            slotStatus[h] = 'slot-booked'; // Red
          } else if (bookingStatus === 'pending' && !slotStatus[h]) {
            slotStatus[h] = 'slot-pending'; // Yellow
          }
          // cancelled/expired remain as 'slot-free' (white)
        }
      });

      let timelineHtml = `<div class="timeline-row">`;
      slots.forEach(h => {
        const slotClass = slotStatus[h] || 'slot-free';
        const slotLabel = `${String(h).padStart(2, '0')}:00`;
        timelineHtml += `<div class="timeline-slot ${slotClass}" title="${slotLabel}">${h}</div>`;
      });
      timelineHtml += `</div>`;

      html += `
        <tr>
          <td><strong>${court.name || court.courtName}</strong></td>
          <td>${court.type || court.surface_type || '--'}</td>
          <td>${window.formatCurrency(court.hourly_rate || court.price || 100000)}</td>
          <td>${timelineHtml}</td>
        </tr>
      `;
    });

    html += `
          </tbody>
        </table>
      </div>
      <div class="legend-row">
        <div><span class="legend-box slot-free"></span> Trống</div>
        <div><span class="legend-box slot-pending"></span> Chờ Xác Nhận</div>
        <div><span class="legend-box slot-booked"></span> Đã Xác Nhận</div>
      </div>
    `;

    return html;
  };

  const calculateHoursByCourt = (courts = [], bookings = []) => {
    const result = {};
    
    courts.forEach(court => {
      const courtId = court.id || court.court_id;
      const courtBookings = bookings.filter(b => {
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

  const renderCourtsStats = (courts, bookings) => {
    const totalCourts = courts.length;
    const totalBookings = bookings.length;
    const hoursByCourtId = calculateHoursByCourt(courts, bookings);
    const totalHours = Object.values(hoursByCourtId).reduce((sum, h) => sum + h, 0);

    return `
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">📍</div>
          <div class="stat-content">
            <div class="stat-label">Tổng Sân</div>
            <div class="stat-value">${totalCourts}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-label">Booking Hôm Nay</div>
            <div class="stat-value">${totalBookings}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-label">Tổng Giờ Đặt</div>
            <div class="stat-value">${totalHours.toFixed(1)}h</div>
          </div>
        </div>
      </div>
    `;
  };

  const api = {
    renderCourtsSection,
    renderCourtsStats,
    calculateHoursByCourt,
  };
  return api;
})();

window.ManagerCourts = ManagerCourts;
window.calculateHoursByCourt = ManagerCourts.calculateHoursByCourt;
