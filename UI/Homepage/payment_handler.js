
const PaymentHandler = (() => {
  const BACKEND_URL = window.CONFIG?.BACKEND_PUBLIC_URL ||
                     window.location.origin.replace(/:\d+$/, '');

  console.log('[PaymentHandler] Initialized with BACKEND_URL:', BACKEND_URL);

  function extractBookingPayload(bookingResponse) {
    if (!bookingResponse) return null;
    if (bookingResponse.data?.booking) return bookingResponse.data.booking;
    if (bookingResponse.booking) return bookingResponse.booking;
    if (bookingResponse.data) return bookingResponse.data;
    return bookingResponse;
  }

  function resolveBookingId(bookingPayload) {
    if (!bookingPayload) return null;
    return (
      bookingPayload.booking_id ||
      bookingPayload.bookingId ||
      bookingPayload.id ||
      null
    );
  }

  function sumItemPrices(items = []) {
    return items.reduce((sum, item) => {
      const price = Number(item?.price || 0);
      return sum + (Number.isFinite(price) ? price : 0);
    }, 0);
  }

  function calculateInvoiceAmount(bookingPayload, bookingData) {
    const directAmount = Number(
      bookingPayload?.total_amount ??
      bookingPayload?.totalAmount ??
      bookingData?.total_price ??
      bookingData?.totalPrice
    );
    if (Number.isFinite(directAmount) && directAmount > 0) {
      return directAmount;
    }
    if (Array.isArray(bookingPayload?.items) && bookingPayload.items.length) {
      const amount = sumItemPrices(bookingPayload.items);
      if (amount > 0) return amount;
    }
    if (Array.isArray(bookingData?.items) && bookingData.items.length) {
      const amount = sumItemPrices(bookingData.items);
      if (amount > 0) return amount;
    }
    return 0;
  }

  function unwrapInvoicePayload(payload) {
    let current = payload;
    const visited = new Set();
    while (current && typeof current === "object") {
      if (visited.has(current)) break;
      visited.add(current);
      if (current.invoice_id || current.id) return current;
      if (current.data) {
        current = current.data;
        continue;
      }
      break;
    }
    return null;
  }

  function normalizeInvoiceInfo(invoicePayload) {
    const normalized = unwrapInvoicePayload(invoicePayload);
    if (!normalized) return null;
    const invoiceId = normalized.invoice_id ?? normalized.id ?? null;
    if (!invoiceId) return null;
    const amountRaw = normalized.amount ?? normalized.total_amount ?? normalized.totalAmount;
    const amount = Number(amountRaw);
    return {
      invoiceId,
      amount: Number.isFinite(amount) ? amount : null,
      status: normalized.status || invoicePayload?.status || null,
      raw: normalized,
    };
  }

  function extractInvoiceInfoFromBookingResponse(bookingResponse) {
    if (!bookingResponse) return null;
    const data = bookingResponse.data || bookingResponse;
    if (data?.invoice) {
      return normalizeInvoiceInfo(data.invoice);
    }
    if (bookingResponse.invoice) {
      return normalizeInvoiceInfo(bookingResponse.invoice);
    }
    return null;
  }

  function resolveUserId(userProfile = {}, fallbackBooking = {}) {
    return (
      userProfile.id ||
      userProfile.user_id ||
      userProfile.userId ||
      fallbackBooking.user_id ||
      fallbackBooking.userId ||
      null
    );
  }

  function readAuthFromStorage() {
    try {
      const raw = localStorage.getItem("soa_auth");
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (err) {
      console.warn("[PaymentHandler] Cannot parse soa_auth cache", err);
      return null;
    }
  }

  async function processPayment(bookingData, userProfile) {
    try {
      console.log('[PaymentHandler] Starting payment flow for booking:', bookingData);

      console.log('[PaymentHandler] Step 1: Creating booking...');
      const bookingResponse = await window.api.booking.create(bookingData);
      if (!bookingResponse) {
        throw new Error('Booking service returned null response');
      }

      const bookingPayload = extractBookingPayload(bookingResponse);
      const bookingId = resolveBookingId(bookingPayload);
      if (!bookingId) {
        console.error('[PaymentHandler] Unexpected booking response format:', bookingResponse);
        throw new Error('Failed to create booking: booking_id missing in response');
      }

      console.log('[PaymentHandler] Booking created successfully:', bookingId);

      const inferredAmount = calculateInvoiceAmount(bookingPayload, bookingData);
      let invoiceInfo = extractInvoiceInfoFromBookingResponse(bookingResponse);
      let invoiceId = invoiceInfo?.invoiceId || null;
      let invoiceAmount = invoiceInfo?.amount;
      let invoiceStatus = invoiceInfo?.status || null;

      if (!Number.isFinite(invoiceAmount) || invoiceAmount <= 0) {
        invoiceAmount = inferredAmount;
      }

      if (!Number.isFinite(invoiceAmount) || invoiceAmount <= 0) {
        console.error('[PaymentHandler] Booking payload missing total amount:', bookingPayload);
        throw new Error('Không xác định được tổng tiền booking để tạo hóa đơn');
      }

      const invoiceRequestPayload = {
        booking_id: bookingId,
        user_id: resolveUserId(userProfile, bookingPayload),
        amount: invoiceAmount,
        currency: 'VND',
        description: `Booking for ${userProfile.name || 'Customer'}`,
      };

      if (!invoiceId) {
        console.log('[PaymentHandler] Step 2: Creating invoice via billing service...');
        const invoiceResponse = await window.api.billing.createInvoice(invoiceRequestPayload);
        if (!invoiceResponse) {
          throw new Error('Billing service returned null response for invoice');
        }

        invoiceInfo = normalizeInvoiceInfo(invoiceResponse) || {
          invoiceId: invoiceResponse.invoice_id || invoiceResponse.id || null,
          amount: Number(invoiceResponse.amount) || invoiceRequestPayload.amount,
          status: invoiceResponse.status || 'pending',
        };
        invoiceId = invoiceInfo?.invoiceId || null;
        invoiceAmount = invoiceInfo?.amount || invoiceRequestPayload.amount;
        invoiceStatus = invoiceInfo?.status || 'pending';

        if (!invoiceId) {
          console.error('[PaymentHandler] Invoice response:', invoiceResponse);
          throw new Error('Failed to create invoice: no invoice_id in response');
        }
        console.log('[PaymentHandler] Invoice created successfully:', invoiceId);
      } else {
        console.log('[PaymentHandler] Reusing invoice from booking service:', invoiceId, invoiceStatus);
      }

      if (invoiceStatus === 'paid') {
        console.log('[PaymentHandler] Invoice already marked as paid, skipping SePay redirect.');
        return {
          success: true,
          bookingId,
          invoiceId,
          paymentStatus: 'paid',
          redirectUrl: null,
          message: 'Hóa đơn đã được thanh toán.',
        };
      }

      console.log('[PaymentHandler] Step 3: Creating SePay payment link...');
      const paymentPayload = {
        booking_id: bookingId,
        amount: Math.round(invoiceAmount),
        description: invoiceRequestPayload.description,
      };

      let paymentResponse;
      try {
        paymentResponse = await createSePayPayment(invoiceId, paymentPayload);
      } catch (paymentError) {
        console.error('[PaymentHandler] Failed to create SePay payment:', paymentError);
        return {
          success: false,
          bookingId,
          invoiceId,
          paymentStatus: null,
          redirectUrl: null,
          message: `Payment error: ${paymentError.message || 'Unknown error'}`,
        };
      }
      
      console.log('[PaymentHandler] Payment response received:', paymentResponse);

      if (paymentResponse.payment_url) {
        console.log('[PaymentHandler] SePay enabled. Redirecting to SePay checkout...');
        
        sessionStorage.setItem('last_booking_id', bookingId);
        sessionStorage.setItem('last_invoice_id', invoiceId);
        
        window.location.href = paymentResponse.payment_url;
        
        return {
          success: true,
          bookingId,
          invoiceId,
          paymentStatus: 'pending',
          redirectUrl: paymentResponse.payment_url,
          message: 'Redirecting to SePay checkout',
        };
      } else {
        console.log('[PaymentHandler] SePay disabled; payment marked as paid immediately');
        
        return {
          success: true,
          bookingId,
          invoiceId,
          paymentStatus: 'paid',
          redirectUrl: null,
          message: 'Payment successful (SePay disabled)',
        };
      }
    } catch (error) {
      console.error('[PaymentHandler] Error in payment flow:', error);
      return {
        success: false,
        bookingId: null,
        invoiceId: null,
        paymentStatus: null,
        redirectUrl: null,
        message: error.message || 'Payment processing failed',
      };
    }
  }

  async function createSePayPayment(invoiceId, payload) {
    try {
      console.log('[PaymentHandler] Creating SePay payment for invoice:', invoiceId, 'payload:', payload);
      
      const jwt = getJWT();
      console.log('[PaymentHandler] Using JWT token for authorization');
      
      const response = await fetch(
        `${BACKEND_URL}/billing/${invoiceId}/sepay/create-payment`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${jwt}`,
          },
          body: JSON.stringify(payload),
        }
      );

      console.log('[PaymentHandler] Response status:', response.status);

      if (!response.ok) {
        let errorDetail = `HTTP ${response.status}`;
        try {
          const errorJson = await response.json();
          errorDetail = errorJson.detail || errorJson.message || errorDetail;
          console.error('[PaymentHandler] Error response:', errorJson);
        } catch (parseError) {
          const errorText = await response.text();
          console.error('[PaymentHandler] Error response text:', errorText);
          errorDetail = errorText || errorDetail;
        }
        throw new Error(`Failed to create SePay payment: ${errorDetail}`);
      }

      const result = await response.json();
      console.log('[PaymentHandler] SePay payment created:', result);
      
      if (!result.data) {
        throw new Error('Invalid response format from server: missing data field');
      }
      
      return result.data;
    } catch (error) {
      console.error('[PaymentHandler] Error creating SePay payment:', error.message);
      throw error;
    }
  }

  async function handlePaymentReturn() {
    const params = new URLSearchParams(window.location.search);
    const paymentStatus = (params.get("payment") || "").toLowerCase();
    const bookingIdParam = params.get("booking_id");
    const failureReason = params.get("reason") || "";

    if (!paymentStatus || !bookingIdParam) {
      console.log("[PaymentHandler] No payment params detected in URL.");
      return null;
    }

    const bookingId = parseInt(bookingIdParam, 10);
    const result = {
      success: paymentStatus === "success",
      status: paymentStatus || "unknown",
      bookingId,
      reason: failureReason,
      message: "",
    };

    try {
      if (paymentStatus === "success" && Number.isFinite(bookingId)) {
        const bookingResponse = await window.api.booking.get(bookingId, { forceRefresh: true });
        const booking = bookingResponse?.data || bookingResponse;
        const bookingStatus = booking?.status;
        const bookingPaymentStatus = booking?.payment_status || booking?.paymentStatus;
        const isConfirmed = bookingStatus === "confirmed" || bookingPaymentStatus === "paid";

        result.success = isConfirmed;
        result.status = isConfirmed ? "confirmed" : bookingPaymentStatus || "pending";
        result.message = isConfirmed
          ? "Thanh toán thành công! Ô sân đã được giữ chỗ."
          : "Không thể xác nhận thanh toán ngay. Vui lòng kiểm tra lại danh sách booking.";
      } else if (paymentStatus === "failed") {
        result.success = false;
        result.status = "failed";
        result.message = failureReason
          ? `Thanh toán thất bại: ${failureReason}`
          : "Thanh toán thất bại. Vui lòng thử lại.";
      } else {
        result.success = false;
        result.message = "Thanh toán không thành công.";
      }
    } catch (error) {
      console.error("[PaymentHandler] Error verifying booking:", error);
      result.success = false;
      result.status = "error";
      result.message = error.message || "Không thể xác minh trạng thái thanh toán.";
    }

    if (typeof window.reloadBookingsForSelection === "function") {
      await window.reloadBookingsForSelection({ forceRefresh: true });
    } else if (typeof window.refreshBookings === "function") {
      await window.refreshBookings({ forceRefresh: true });
    }

    window.history.replaceState({}, document.title, window.location.pathname);
    return result;
  }

  async function checkPaymentStatus(invoiceId) {
    try {
      const invoice = await window.api.billing.getInvoice(invoiceId);
      return {
        status: invoice.status,
        amount: invoice.amount,
        currency: invoice.currency,
      };
    } catch (error) {
      console.error('[PaymentHandler] Error checking payment status:', error);
      throw error;
    }
  }

  function getJWT() {
    const auth = window.api?.getAuth?.() || readAuthFromStorage() || {};
    if (auth.token) return auth.token;
    const legacyToken = localStorage.getItem('access_token');
    if (legacyToken) return legacyToken;
    throw new Error('No authentication token found');
  }

  return {
    processPayment,
    handlePaymentReturn,
    checkPaymentStatus,
  };
})();

window.PaymentHandler = PaymentHandler;
