const ManagerSettings = (() => {
  const STORAGE_KEY = "manager_court_settings";

  const loadSettings = () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (err) {
      console.warn("[ManagerSettings] Cannot parse saved settings", err);
      return {};
    }
  };

  const saveSettings = (settings) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  };

  const formatNumber = (value) => {
    const num = Number(value);
    return Number.isFinite(num) ? num : "";
  };

  const renderSegmentRow = (courtId, segment, index) => `
      <div class="segment-card" data-court="${courtId}" data-index="${index}">
        <div class="segment-card-body">
          <div class="segment-field">
            <label class="segment-label"><i class="fa-solid fa-clock"></i> Từ</label>
            <input type="time" class="segment-input segment-start" value="${segment.start || ""}" />
          </div>
          <div class="segment-field">
            <label class="segment-label"><i class="fa-solid fa-clock"></i> Đến</label>
            <input type="time" class="segment-input segment-end" value="${segment.end || ""}" />
          </div>
          <div class="segment-field">
            <label class="segment-label"><i class="fa-solid fa-money-bill-wave"></i> Giá (VND)</label>
            <input type="number" min="0" step="1000" class="segment-input segment-price segment-price-input" placeholder="120000" value="${formatNumber(segment.price)}" />
          </div>
        </div>
        <button type="button" class="segment-remove-btn" data-action="remove-segment" data-court-id="${courtId}" title="Xóa khung giờ">
          <i class="fa-solid fa-trash-can"></i>
        </button>
      </div>`;

  const renderCard = (court, saved) => {
    const cfg = saved[court.id] || {};
    const segments = cfg.segments || [];
    const rowsHtml = segments.length
      ? segments.map((seg, idx) => renderSegmentRow(court.id, seg, idx)).join("")
      : renderSegmentRow(court.id, {}, 0);
    
    const courtTypeIcon = court.type === 'Premium' ? 'fa-crown' : court.type === 'VIP' ? 'fa-star' : 'fa-futbol';
    const courtTypeColor = court.type === 'Premium' ? '#f59e0b' : court.type === 'VIP' ? '#8b5cf6' : '#3b82f6';
    
    return `
      <div class="settings-card" data-court="${court.id}">
        <div class="court-price-card" data-court="${court.id}">
          <div class="court-card-header">
            <div class="court-info">
              <div class="court-icon" style="background: ${courtTypeColor}20; color: ${courtTypeColor};">
                <i class="fa-solid ${courtTypeIcon}"></i>
              </div>
              <div class="court-details">
                <h3 class="court-name">${court.name}</h3>
                <div class="court-meta">
                  <span class="court-type" style="background: ${courtTypeColor}20; color: ${courtTypeColor};">
                    <i class="fa-solid ${courtTypeIcon}"></i> ${court.type || court.surface_type || "Standard"}
                  </span>
                  <span class="court-id"><i class="fa-solid fa-hashtag"></i> ${court.id}</span>
                </div>
              </div>
            </div>
            <div class="court-actions">
              <button type="button" class="action-btn action-btn-secondary" data-action="reset" data-court-id="${court.id}" title="Khôi phục mặc định">
                <i class="fa-solid fa-rotate-left"></i>
                <span>Khôi phục</span>
              </button>
              <button type="button" class="action-btn action-btn-primary" data-action="save" data-court-id="${court.id}" title="Lưu cài đặt">
                <i class="fa-solid fa-floppy-disk"></i>
                <span>Lưu giá</span>
              </button>
            </div>
          </div>
          <div class="price-segments-container">
            ${rowsHtml}
            <button type="button" class="segment-card segment-card-add" data-action="add-segment" data-court-id="${court.id}">
              <div class="add-card-content">
                <i class="fa-solid fa-plus-circle"></i>
                <span>Thêm khung giờ</span>
              </div>
            </button>
          </div>
        </div>
      </div>`;
  };

  let currentCourts = [];

  const render = (courts = []) => {
    const container = document.getElementById("settings-content");
    if (!container) return;
    if (!courts.length) {
      container.innerHTML = `<p class="muted">Chưa có dữ liệu sân để cấu hình. Hãy tải lại tab sân.</p>`;
      return;
    }
    const saved = loadSettings();
    currentCourts = courts;
    container.innerHTML = courts.map((c) => renderCard(c, saved)).join("");
  };

  const handleAction = (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    const courtId = Number(button.dataset.courtId);
    if (!courtId) return;
    const card = document.querySelector(`.settings-card[data-court="${courtId}"]`);
    if (!card) return;
    const settings = loadSettings();

    if (action === "reset") {
      delete settings[courtId];
      saveSettings(settings);
      render(currentCourts);
      window.showToast("Thiết lập sân đã được đặt về mặc định.");
      return;
    }

    if (action === "add-segment") {
      const container = card.querySelector(".price-segments-container");
      const addCard = card.querySelector(".segment-card-add");
      const rows = card.querySelectorAll(".segment-card:not(.segment-card-add)");
      const newIndex = rows.length;
      if (addCard) {
        addCard.insertAdjacentHTML("beforebegin", renderSegmentRow(courtId, {}, newIndex));
      } else if (container) {
        container.insertAdjacentHTML("beforeend", renderSegmentRow(courtId, {}, newIndex));
      }
      return;
    }

    if (action === "remove-segment") {
      const row = event.target.closest(".segment-card:not(.segment-card-add)");
      if (row) {
        const container = row.parentElement;
        row.remove();
        if (container && container.querySelectorAll(".segment-card:not(.segment-card-add)").length === 0) {
          const addCard = container.querySelector(".segment-card-add");
          if (addCard) {
            addCard.insertAdjacentHTML("beforebegin", renderSegmentRow(courtId, {}, 0));
          } else {
            container.insertAdjacentHTML("beforeend", renderSegmentRow(courtId, {}, 0));
          }
        }
      }
      return;
    }

    const gridRows = card.querySelectorAll(".segment-card:not(.segment-card-add)");
    const payloadSegments = Array.from(gridRows)
      .map((row) => {
        const start = row.querySelector(".segment-start")?.value;
        const end = row.querySelector(".segment-end")?.value;
        const price = Number(row.querySelector(".segment-price")?.value || "0");
        if (!start || !end) return null;
        return { start, end, price };
      })
      .filter(Boolean);

    settings[courtId] = { segments: payloadSegments.length ? payloadSegments : [] };
    saveSettings(settings);
    window.showToast(`Lưu giá cho ${card.querySelector(".court-name")?.innerText || "sân này"} thành công.`);
    if (window.ManagerBooking?.logManagerAction) {
      const courtName = card.querySelector(".court-name")?.innerText || "sân này";
      const formatCurrency =
        window.SharedUtils?.formatCurrency || ((value) => (value ? `${value}đ` : "0đ"));
      const detailParts =
        payloadSegments.length > 0
          ? payloadSegments.map(
              (seg) => `${seg.start}-${seg.end} @ ${formatCurrency(seg.price)}`
            )
          : ["Xóa toàn bộ khung giờ đã cấu hình"];
      window.ManagerBooking.logManagerAction({
        action: "price-update",
        detail: `${courtName}: ${detailParts.join(" · ")}`,
        contextId: `court-${courtId}`,
      });
    }
  };

  document.addEventListener("click", (event) => {
    if (event.target.closest(".settings-card")) {
      handleAction(event);
    }
  });

  return {
    render,
  };
})();

window.ManagerSettings = ManagerSettings;
