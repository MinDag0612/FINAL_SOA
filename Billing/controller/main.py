from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import logging

from Billing.core.connDB import connDB
from Billing.models.billing_models import (
    BillingHistoryParams,
    InvoiceCreate,
    PaymentRequest,
    PaymentWebhook,
    SePayCreatePaymentRequest,
)
from Billing.service.billing_service import BillingService

app = FastAPI()
db = connDB()
logger = logging.getLogger(__name__)


def get_service(session: Session = Depends(db.get_db)) -> BillingService:
    return BillingService(session)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "billing"}


@app.post("/billing")
def create_invoice(
    payload: InvoiceCreate,
    service: BillingService = Depends(get_service),
    session: Session = Depends(db.get_db),
):
    return {"status": "success", "data": service.create_invoice(payload)}


@app.get("/billing/history")
def billing_history(
    params: BillingHistoryParams = Depends(),
    service: BillingService = Depends(get_service),
):
    return {"status": "success", "data": service.list_history(params)}


@app.post("/billing/{invoice_id}/pay")
def pay_invoice(
    invoice_id: int,
    payload: PaymentRequest,
    service: BillingService = Depends(get_service),
):
    return service.initiate_payment(invoice_id, payload)


@app.get("/billing/{invoice_id}")
def get_invoice(invoice_id: int, service: BillingService = Depends(get_service)):
    return {"status": "success", "data": service.get_invoice(invoice_id)}


@app.post("/billing/{invoice_id}/webhook")
def billing_webhook(
    invoice_id: int,
    payload: PaymentWebhook,
    service: BillingService = Depends(get_service),
):
    return service.handle_webhook(invoice_id, payload)


# ===== SePay Payment Gateway Endpoints =====

@app.post("/billing/{invoice_id}/sepay/create-payment")
def create_sepay_payment(
    invoice_id: int,
    payload: SePayCreatePaymentRequest,
    service: BillingService = Depends(get_service),
):
    """
    Create SePay payment link
    
    Request:
        {
            "booking_id": 123,
            "amount": 500000,
            "description": "Booking court for 2 hours"
        }
    
    Response:
        {
            "payment_url": "https://pay-sandbox.sepay.vn/...",
            "booking_id": 123,
            "amount": 500000,
            "merchant_id": "SP-TEST-...",
            "status": "pending",
            "message": "..."
        }
    """
    try:
        logger.info(f"Creating SePay payment for invoice {invoice_id}, booking {payload.booking_id}, amount {payload.amount}")
        result = service.create_sepay_payment(invoice_id, payload)
        logger.info(f"SePay payment created successfully for invoice {invoice_id}")
        return {"status": "success", "data": result}
    except HTTPException as e:
        logger.error(f"HTTP Error creating SePay payment for invoice {invoice_id}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error creating SePay payment for invoice {invoice_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")


@app.get("/billing/sepay/return")
async def sepay_return_get(
    request: Request,
    service: BillingService = Depends(get_service),
):
    """
    SePay return URL (GET method)
    User is redirected here after payment on SePay checkout
    
    Query params from SePay:
        - status: success, cancel, failed
        - booking_id: booking ID
        - transactionId: transaction ID from SePay
    
    Response:
        Redirect to /customer.html?payment=success|failed&booking_id=...
    """
    query_params = dict(request.query_params)
    
    result = service.handle_sepay_return(query_params)
    redirect_url = result.get("redirect_url", "/customer.html?payment=failed")
    
    # Return HTML with redirect script (since we need to preserve all context)
    return RedirectResponse(url=redirect_url, status_code=303)


@app.post("/billing/sepay/return")
async def sepay_return_post(
    request: Request,
    service: BillingService = Depends(get_service),
):
    """
    SePay return URL (POST method)
    Handle POST data from SePay
    """
    # Parse form and query data
    form_data = await request.form()
    query_params = dict(request.query_params)
    query_params.update(dict(form_data))
    
    result = service.handle_sepay_return(query_params)
    redirect_url = result.get("redirect_url", "/customer.html?payment=failed")
    
    return RedirectResponse(url=redirect_url, status_code=303)


@app.post("/billing/sepay/ipn")
async def sepay_ipn(
    request: Request,
    service: BillingService = Depends(get_service),
):
    """
    SePay IPN Webhook (server-to-server payment notification)
    
    SePay will POST to this URL to notify payment status
    
    Expected payload:
        {
            "merchantId": "SP-TEST-...",
            "orderCode": "invoice-123",
            "status": "success|failed",
            "transactionId": "...",
            "signature": "..."
        }
    
    Response:
        {"ok": true/false}
    """
    try:
        # Parse JSON payload
        payload = await request.json()
        result = service.handle_sepay_ipn(payload)
        return result
    except Exception as e:
        logger.error(f"Error processing SePay IPN: {str(e)}")
        return {"ok": False, "message": str(e)}

