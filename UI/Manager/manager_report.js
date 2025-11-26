/**
 * manager_report.js - Báo cáo doanh thu theo ngày/tuần
 * 
 * Chức năng:
 * 1. Cho phép chọn khoảng thời gian (ngày bắt đầu - kết thúc)
 * 2. Tính toán doanh thu = sum(booking.price)
 * 3. Tính toán tổng giờ = sum(end_hour - start_hour)
 * 4. Group theo sân
 * 5. Render bảng report
 */

const ManagerReport = (() => {
  /**
   * Tính doanh thu theo sân trong khoảng thời gian
   * @param {Array} bookings - Danh sách booking
   * @param {Array} courts - Danh sách sân
   * @param {string} startDate - YYYY-MM-DD
   * @param {string} endDate - YYYY-MM-DD
   * @returns {Array} - [{courtId, courtName, totalHours, totalRevenue}, ...]
   */
  const calculateRevenueByCourtId = (bookings, courts, startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    end.setDate(end.getDate() + 1); // Include end date

    const courtMap = {};
    (courts || []).forEach(c => {
      const cId = c.id || c.court_id;
      courtMap[cId] = {
        courtId: cId,
        courtName: c.name || c.courtName,
        totalHours: 0,
        totalRevenue: 0,
        bookingCount: 0,
      };
    });

    (bookings || []).forEach(booking => {
      // Only count confirmed/completed bookings for revenue report
      const status = booking.status || booking.uiStatus;
      if (status === 'cancelled' || status === 'pending') {
        return; // Skip cancelled and pending bookings
      }

      const bookingStart = new Date(booking.start_time || booking.start);
      const bookingEnd = new Date(booking.end_time || booking.end);

      if (isNaN(bookingStart.getTime()) || isNaN(bookingEnd.getTime())) return;
      if (bookingEnd <= start || bookingStart >= end) return;

      const courtId = booking.courtId || booking.court_id;

      if (!courtMap[courtId]) {
        courtMap[courtId] = {
          courtId: courtId,
          courtName: `Sân #${courtId}`,
          totalHours: 0,
          totalRevenue: 0,
          bookingCount: 0,
        };
      }

      const hours = (bookingEnd - bookingStart) / (1000 * 60 * 60);
      const revenue = booking.total || booking.price || (hours * 100000);
      courtMap[courtId].totalHours += hours;
      courtMap[courtId].totalRevenue += revenue;
      courtMap[courtId].bookingCount += 1;
    });

    return Object.values(courtMap).filter(c => c.bookingCount > 0);
  };

  /**
   * Render form chọn khoảng thời gian
   * @param {string} startDate - Default start date
   * @param {string} endDate - Default end date
   * @returns {string} HTML
   */
  const renderDateRangeFilter = (startDate, endDate) => {
    return `
      <div class="report-filter">
        <div class="form-group">
          <label>Từ Ngày</label>
          <input type="date" id="report-start-date" value="${startDate}" />
        </div>
        <div class="form-group">
          <label>Đến Ngày</label>
          <input type="date" id="report-end-date" value="${endDate}" />
        </div>
        <button class="btn-primary" onclick="ManagerReport.updateReport()">Xem Report</button>
      </div>
    `;
  };

  /**
   * Render bảng report
   * @param {Array} reportData - Output từ calculateRevenueByCourtId
   * @param {string} dateRange - Display text (e.g., "01/01/2024 - 07/01/2024")
   * @returns {string} HTML
   */
  const renderReportTable = (reportData, dateRange) => {
    if (!reportData || reportData.length === 0) {
      return `
        <div class="empty-state">
          <i class="fa-solid fa-chart-line"></i>
          <p>Không có dữ liệu</p>
        </div>
      `;
    }

    let totalHours = 0;
    let totalRevenue = 0;
    let totalBookings = 0;

    reportData.forEach(row => {
      totalHours += row.totalHours || 0;
      totalRevenue += row.totalRevenue || 0;
      totalBookings += row.bookingCount || 0;
    });

    let html = `
      <div class="report-header">
        <h4>Báo Cáo Doanh Thu: ${dateRange}</h4>
      </div>

      <div class="report-summary">
        <div class="summary-card">
          <div class="label">Tổng Booking</div>
          <div class="value">${totalBookings}</div>
        </div>
        <div class="summary-card">
          <div class="label">Tổng Giờ</div>
          <div class="value">${totalHours.toFixed(1)}h</div>
        </div>
        <div class="summary-card">
          <div class="label">Tổng Doanh Thu</div>
          <div class="value">${window.formatCurrency(totalRevenue)}</div>
        </div>
      </div>

      <div class="report-table-wrapper">
        <table class="report-table">
          <thead>
            <tr>
              <th>Sân</th>
              <th>Số Lần Đặt</th>
              <th>Tổng Giờ</th>
              <th>Doanh Thu</th>
              <th>TB Giờ/Lần</th>
              <th>Tỷ Lệ (%)</th>
            </tr>
          </thead>
          <tbody>
    `;

    reportData.forEach(row => {
      const avgHours = row.bookingCount > 0 ? (row.totalHours / row.bookingCount).toFixed(1) : 0;
      const percentage = totalRevenue > 0 ? ((row.totalRevenue / totalRevenue) * 100).toFixed(1) : 0;

      html += `
        <tr>
          <td><strong>${row.courtName}</strong></td>
          <td>${row.bookingCount}</td>
          <td>${row.totalHours.toFixed(1)}h</td>
          <td>${window.formatCurrency(row.totalRevenue)}</td>
          <td>${avgHours}h</td>
          <td>${percentage}%</td>
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

  /**
   * Update report (called từ button click)
   */
  const updateReport = async () => {
    const startDate = document.getElementById("report-start-date")?.value;
    const endDate = document.getElementById("report-end-date")?.value;

    if (!startDate || !endDate) {
      alert("Vui lòng chọn khoảng thời gian");
      return;
    }

    if (new Date(startDate) > new Date(endDate)) {
      alert("Ngày bắt đầu phải nhỏ hơn ngày kết thúc");
      return;
    }

    try {
      console.log("[ManagerReport] Loading report:", { startDate, endDate });

      const facilityId = state?.managerFacilityId;
      if (!facilityId) {
        alert("Vui lòng chọn cơ sở để xem báo cáo");
        return;
      }

      const bookings = await window.api.booking.managerList(facilityId);
      const courts = await window.api.court.listByFacility(facilityId);
      const normalized = (bookings || []).map(normalizeBooking);
      const courtList = (courts || []).map(mapCourt);

      const reportData = ManagerReport.calculateRevenueByCourtId(normalized, courtList, startDate, endDate);
      
      const startObj = new Date(startDate);
      const endObj = new Date(endDate);
      const dateRange = `${startObj.toLocaleDateString('vi-VN')} - ${endObj.toLocaleDateString('vi-VN')}`;

      const reportHtml = ManagerReport.renderReportTable(reportData, dateRange);
      const reportContainer = document.getElementById("report-container");
      if (reportContainer) {
        reportContainer.innerHTML = reportHtml;
      }

      console.log("[ManagerReport] Report updated");
    } catch (err) {
      console.error("[ManagerReport] Error:", err);
      alert("Lỗi load report: " + err.message);
    }
  };

  /**
   * Export report to CSV (future feature)
   */
  const exportToCSV = (reportData, dateRange) => {
    // TODO: Implement CSV export
    console.log("Export to CSV not implemented yet");
  };

  return {
    calculateRevenueByCourtId,
    renderDateRangeFilter,
    renderReportTable,
    updateReport,
    exportToCSV,
  };
})();

window.ManagerReport = ManagerReport;
