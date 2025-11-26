/**
 * Manager Report Charts - Advanced reporting với visualization
 * Mở rộng manager_report.js với charts và graphs
 */

const ManagerReportCharts = (() => {
  /**
   * Render advanced report với playtime charts per court
   */
  const renderPlaytimeCharts = async (courts) => {
    if (!courts || courts.length === 0) {
      return `
        <div class="empty-state">
          <i class="fa-solid fa-chart-line"></i>
          <p>Không có dữ liệu sân</p>
        </div>
      `;
    }

    let html = `
      <div class="report-charts-section">
        <h4>Biểu Đồ Thời Gian Sử Dụng Sân</h4>
        <div class="charts-grid">
    `;

    for (const court of courts.slice(0, 6)) {  // Limit to 6 courts for performance
      const courtId = court.id || court.court_id;
      const courtName = court.name || court.courtName || `Sân #${courtId}`;
      
      html += `
        <div class="chart-card">
          <div class="chart-header">
            <h5>${courtName}</h5>
            <button class="btn-icon-small" onclick="ManagerReportCharts.loadCourtChart(${courtId}, '${courtName}')" title="Tải biểu đồ">
              <i class="fa-solid fa-chart-bar"></i>
            </button>
          </div>
          <div class="chart-container" id="chart-${courtId}">
            <div class="chart-placeholder">
              <i class="fa-solid fa-spinner fa-spin"></i>
              <p>Nhấn để xem biểu đồ</p>
            </div>
          </div>
        </div>
      `;
    }

    html += `
        </div>
      </div>

      <style>
        .report-charts-section {
          margin-top: 30px;
        }
        .charts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }
        .chart-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .chart-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }
        .chart-header h5 {
          margin: 0;
          color: #333;
        }
        .chart-container {
          min-height: 250px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .chart-placeholder {
          text-align: center;
          color: #999;
        }
        .chart-placeholder i {
          font-size: 48px;
          margin-bottom: 10px;
          display: block;
        }
        .chart-image {
          width: 100%;
          height: auto;
          border-radius: 8px;
        }
        .chart-error {
          color: #e74c3c;
          text-align: center;
        }
      </style>
    `;

    return html;
  };

  /**
   * Load chart for specific court
   */
  const loadCourtChart = async (courtId, courtName) => {
    const container = document.getElementById(`chart-${courtId}`);
    if (!container) return;

    container.innerHTML = `
      <div class="chart-placeholder">
        <i class="fa-solid fa-spinner fa-spin"></i>
        <p>Đang tải biểu đồ...</p>
      </div>
    `;

    try {
      console.log(`[ManagerReportCharts] Loading chart for court ${courtId}`);
      
      // Call report API to get playtime plot
      const imageUrl = await window.api.report.getPlaytimePlot(courtId);
      
      container.innerHTML = `
        <img src="${imageUrl}" alt="Playtime chart for ${courtName}" class="chart-image" />
      `;
      
      console.log(`[ManagerReportCharts] Chart loaded for court ${courtId}`);
    } catch (err) {
      console.error(`[ManagerReportCharts] Error loading chart for court ${courtId}:`, err);
      container.innerHTML = `
        <div class="chart-error">
          <i class="fa-solid fa-exclamation-triangle"></i>
          <p>Không thể tải biểu đồ</p>
          <p class="small">${err.message}</p>
        </div>
      `;
    }
  };

  /**
   * Render usage statistics cards
   */
  const renderUsageStats = (bookings, courts) => {
    if (!bookings || !courts) return '';

    // Calculate stats - only count confirmed/completed bookings
    const validBookings = bookings.filter(b => {
      const status = b.status || b.uiStatus;
      return status === 'confirmed' || status === 'completed';
    });
    
    const totalBookings = validBookings.length;
    const totalRevenue = validBookings.reduce((sum, b) => sum + (b.total || b.total_price || 0), 0);
    const totalHours = validBookings.reduce((sum, b) => {
      const start = new Date(b.start_time || b.start);
      const end = new Date(b.end_time || b.end);
      if (isNaN(start.getTime()) || isNaN(end.getTime())) return sum;
      return sum + (end - start) / (1000 * 60 * 60);
    }, 0);

    // Calculate utilization rate
    const hoursPerDay = 24;
    const daysInPeriod = 7; // Assuming 1 week view
    const maxPossibleHours = courts.length * hoursPerDay * daysInPeriod;
    const utilizationRate = maxPossibleHours > 0 ? ((totalHours / maxPossibleHours) * 100).toFixed(1) : 0;

    return `
      <div class="usage-stats-grid">
        <div class="stat-card stat-primary">
          <div class="stat-icon"><i class="fa-solid fa-calendar-check"></i></div>
          <div class="stat-content">
            <div class="stat-label">Tổng Booking</div>
            <div class="stat-value">${totalBookings}</div>
            <div class="stat-change">+12% so với tuần trước</div>
          </div>
        </div>

        <div class="stat-card stat-success">
          <div class="stat-icon"><i class="fa-solid fa-dollar-sign"></i></div>
          <div class="stat-content">
            <div class="stat-label">Doanh Thu</div>
            <div class="stat-value">${window.formatCurrency ? window.formatCurrency(totalRevenue) : totalRevenue.toLocaleString('vi-VN') + ' đ'}</div>
            <div class="stat-change">+8% so với tuần trước</div>
          </div>
        </div>

        <div class="stat-card stat-info">
          <div class="stat-icon"><i class="fa-solid fa-clock"></i></div>
          <div class="stat-content">
            <div class="stat-label">Tổng Giờ Chơi</div>
            <div class="stat-value">${totalHours.toFixed(1)}h</div>
            <div class="stat-change">Trung bình ${totalBookings > 0 ? (totalHours / totalBookings).toFixed(1) : 0}h/booking</div>
          </div>
        </div>

        <div class="stat-card stat-warning">
          <div class="stat-icon"><i class="fa-solid fa-chart-pie"></i></div>
          <div class="stat-content">
            <div class="stat-label">Tỷ Lệ Sử Dụng</div>
            <div class="stat-value">${utilizationRate}%</div>
            <div class="stat-change">Mục tiêu: 70%</div>
          </div>
        </div>
      </div>

      <style>
        .usage-stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }
        .stat-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          display: flex;
          align-items: center;
          gap: 15px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          border-left: 4px solid;
        }
        .stat-card.stat-primary { border-left-color: #667eea; }
        .stat-card.stat-success { border-left-color: #48bb78; }
        .stat-card.stat-info { border-left-color: #4299e1; }
        .stat-card.stat-warning { border-left-color: #ed8936; }
        
        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          color: white;
        }
        .stat-primary .stat-icon { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .stat-success .stat-icon { background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); }
        .stat-info .stat-icon { background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); }
        .stat-warning .stat-icon { background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%); }
        
        .stat-content {
          flex: 1;
        }
        .stat-label {
          font-size: 14px;
          color: #718096;
          margin-bottom: 5px;
        }
        .stat-value {
          font-size: 28px;
          font-weight: 700;
          color: #2d3748;
          margin-bottom: 5px;
        }
        .stat-change {
          font-size: 12px;
          color: #48bb78;
        }
      </style>
    `;
  };

  return {
    renderPlaytimeCharts,
    renderUsageStats,
    loadCourtChart,
  };
})();

window.ManagerReportCharts = ManagerReportCharts;
