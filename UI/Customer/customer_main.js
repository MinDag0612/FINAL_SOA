// ===================================
// CUSTOMER MAIN APPLICATION
// ===================================

const CustomerApp = (() => {
  const { 
    getAuthOrRedirect, buildProfileFromAuth, setAvatarInitials,
    refreshFacilities, refreshCourts, refreshBookings,
    setSelection, showToast
  } = window.SharedUtils;

  let currentView = "booking";
  const dynamicContent = document.getElementById("dynamic-content");
  const pageTitle = document.getElementById("page-title");

  // ===================================
  // INITIALIZATION
  // ===================================

  async function initialize() {
    const auth = getAuthOrRedirect();
    if (!auth) return;

    // Check if user is customer
    if (auth.user.role !== 'customer') {
      alert('Bạn không có quyền truy cập trang này. Chỉ khách hàng mới có thể đặt sân.');
      window.location.href = '../Login/login.html';
      return;
    }

    window.state.userProfile = buildProfileFromAuth(auth.user);
    setAvatarInitials(window.state.userProfile.name);

    // Check for payment callback (quick)
    await handlePaymentReturn();

    // Load facilities and courts first (fast, needed for UI)
    await Promise.all([refreshFacilities(), refreshCourts()]);

    // Set default selection immediately
    if (!window.state.selectedFacilityId && window.state.facilities.length) {
      setSelection(
        window.state.facilities[0].facility_id || window.state.facilities[0].id,
        window.state.selectedDate || new Date().toISOString().split("T")[0]
      );
    }
    if (!window.state.selectedDate) {
      setSelection(window.state.selectedFacilityId, new Date().toISOString().split("T")[0]);
    }

    // Load occupied bookings FIRST (needed for red cells)
    if (typeof window.refreshOccupiedBookings === "function") {
      await window.refreshOccupiedBookings({
        forceRefresh: true,
        facilityId: window.state.selectedFacilityId,
        date: window.state.selectedDate,
      }).catch((err) => {
        console.error("[CustomerApp] Failed to preload occupied bookings:", err);
      });
    }

    // Load user's bookings in background (slow, not critical for UI)
    refreshBookings().catch(err => {
      console.error("Failed to load bookings in background:", err);
    });

    // Load default view
    changeView("booking");

    // Show selection modal if needed
    const SHOULD_PROMPT = !window.state.selectedFacilityId || !window.state.selectedDate;
    if (SHOULD_PROMPT) {
      window.CustomerBooking.openSelectionModal();
    }
  }

  // ===================================
  // VIEW ROUTING
  // ===================================

  function changeView(viewName) {
    currentView = viewName;
    window.currentView = viewName;

    if (viewName === "dashboard") {
      window.CustomerDashboard.renderDashboard();
    } else if (viewName === "profile") {
      window.CustomerDashboard.renderProfile();
    } else if (viewName === "booking") {
      window.CustomerBooking.renderBooking();
    } else {
      window.CustomerBooking.renderBooking();
    }
  }

  // ===================================
  // PAYMENT RETURN HANDLER
  // ===================================

  async function handlePaymentReturn() {
    try {
      console.log("[handlePaymentReturn] Checking for payment params in URL...");
      const returnData = await window.PaymentHandler.handlePaymentReturn();
      if (!returnData) {
        console.log("[handlePaymentReturn] No payment params found");
        return;
      }
      console.log("[handlePaymentReturn] Result:", returnData);

      if (returnData.success) {
        console.log("[handlePaymentReturn] Payment successful, reloading bookings...");
        
        showToast(returnData.message || "  Thanh toán thành công! Ô sân đã được xác nhận (màu đỏ).");
        
        // Clear selected slots after successful payment
        window.state.selectedSlots = [];
        if (typeof window.CustomerBooking.updateSelectionBar === 'function') {
          window.CustomerBooking.updateSelectionBar();
        }
        
        // Switch to booking view first
        if (currentView !== "booking") {
          console.log("[handlePaymentReturn] Switching to booking view");
          changeView("booking");
        }
        
        // Force reload bookings data to get updated payment status
        try {
          // Reload BOTH user bookings AND occupied slots (for red cells)
          await Promise.all([
            refreshBookings({ forceRefresh: true }),
            window.refreshOccupiedBookings?.({
              forceRefresh: true,
              facilityId: window.state.selectedFacilityId,
              date: window.state.selectedDate,
            })
          ]);
          
          // Re-render booking view
          if (typeof window.CustomerBooking?.renderBooking === "function") {
            window.CustomerBooking.renderBooking();
          }
          console.log("[handlePaymentReturn] Bookings reloaded and view refreshed");
        } catch (loadErr) {
          console.error("[handlePaymentReturn] Failed to reload bookings:", loadErr);
        }
        
        window.scrollTo(0, 0);
      } else if (returnData.status === 'cancelled') {
        console.log("[handlePaymentReturn] Payment cancelled");
        showToast("Đã hủy thanh toán. Bạn có thể chọn lại các ô.");
        // Clear selected slots on cancel
        window.state.selectedSlots = [];
        if (typeof window.CustomerBooking.updateSelectionBar === 'function') {
          window.CustomerBooking.updateSelectionBar();
        }
      } else {
        console.log("[handlePaymentReturn] Payment failed:", returnData.message);
        showToast(returnData.message || "   Thanh toán thất bại. Vui lòng thử lại.");
        // Keep selected slots so user can retry
      }
    } catch (err) {
      console.error("[handlePaymentReturn] Error:", err);
      showToast("Không thể xác nhận thanh toán. Vui lòng thử lại sau.");
    }
  }

  // ===================================
  // EXPORT API
  // ===================================

  return {
    initialize,
    changeView,
    handlePaymentReturn,
  };
})();

// ===================================
// DOM READY
// ===================================

document.addEventListener("DOMContentLoaded", () => {
  CustomerApp.initialize().catch((err) => {
    console.error("[CustomerApp] Initialization error:", err);
  });
});

// Export to window
window.CustomerApp = CustomerApp;
window.changeView = CustomerApp.changeView;
