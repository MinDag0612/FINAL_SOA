from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from Billing.core.connDB import connDB
from Billing.models.billing_models import (
    BillingHistoryParams,
    InvoiceCreate,
    PaymentRequest,
    PaymentWebhook,
)
from Billing.service.billing_service import BillingService

app = FastAPI()
db = connDB()


def get_service() -> BillingService:
    return BillingService()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "billing"}

@app.post("/billing")
def create_invoice(
    payload: InvoiceCreate,
    service: BillingService = Depends(get_service),
    session: Session = Depends(db.get_db),
):
    return {"status": "success", "data": service.create_invoice(payload)}


@app.get("/billing/{invoice_id}")
def get_invoice(invoice_id: int, service: BillingService = Depends(get_service)):
    return {"status": "success", "data": service.get_invoice(invoice_id)}


@app.post("/billing/{invoice_id}/pay")
def pay_invoice(
    invoice_id: int,
    payload: PaymentRequest,
    service: BillingService = Depends(get_service),
):
    return service.initiate_payment(invoice_id, payload)


@app.post("/billing/{invoice_id}/webhook")
def billing_webhook(
    invoice_id: int,
    payload: PaymentWebhook,
    service: BillingService = Depends(get_service),
):
    return service.handle_webhook(invoice_id, payload)


@app.get("/billing/history")
def billing_history(
    params: BillingHistoryParams = Depends(),
    service: BillingService = Depends(get_service),
):
    return {"status": "success", "data": service.list_history(params)}

@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")

