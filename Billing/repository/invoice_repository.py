from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

from Billing.models.billing_models import Invoice, InvoiceCreate


class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: InvoiceCreate, status: str = "pending") -> Invoice:
        query = text(
            """
            INSERT INTO invoices (booking_id, user_id, amount, currency, status)
            VALUES (:booking_id, :user_id, :amount, :currency, :status)
            """
        )
        result = self.db.execute(
            query,
            {
                "booking_id": payload.booking_id,
                "user_id": payload.user_id,
                "amount": payload.amount,
                "currency": payload.currency,
                "status": status,
            },
        )
        self.db.commit()
        invoice_id = result.lastrowid
        return self.get(invoice_id)

    def get(self, invoice_id: int) -> Optional[Invoice]:
        query = text(
            """
            SELECT invoice_id, booking_id, user_id, amount, currency, status,
                   payment_method, payment_url, payment_reference,
                   vnp_txn_ref, vnp_response_code, vnp_transaction_no, note,
                   created_at, updated_at
            FROM invoices
            WHERE invoice_id = :invoice_id
            """
        )
        row = self.db.execute(query, {"invoice_id": invoice_id}).mappings().first()
        if not row:
            return None
        return self._row_to_model(row)

    def list_by_user(self, user_id: int, limit: int = 10) -> List[Invoice]:
        query = text(
            """
            SELECT invoice_id, booking_id, user_id, amount, currency, status,
                   payment_method, payment_url, payment_reference,
                   vnp_txn_ref, vnp_response_code, vnp_transaction_no, note,
                   created_at, updated_at
            FROM invoices
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
            """
        )
        rows = self.db.execute(query, {"user_id": user_id, "limit": limit}).mappings().all()
        return [self._row_to_model(r) for r in rows]

    def update_payment_url(self, invoice_id: int, payment_url: str, payment_method: str, vnp_txn_ref: str) -> None:
        query = text(
            """
            UPDATE invoices
            SET payment_url = :payment_url,
                payment_method = :payment_method,
                vnp_txn_ref = :vnp_txn_ref
            WHERE invoice_id = :invoice_id
            """
        )
        self.db.execute(
            query,
            {
                "payment_url": payment_url,
                "payment_method": payment_method,
                "vnp_txn_ref": vnp_txn_ref,
                "invoice_id": invoice_id,
            },
        )
        self.db.commit()

    def update_status(
        self,
        invoice_id: int,
        status: str,
        payment_reference: Optional[str] = None,
        vnp_response_code: Optional[str] = None,
        vnp_transaction_no: Optional[str] = None,
    ) -> Optional[Invoice]:
        query = text(
            """
            UPDATE invoices
            SET status = :status,
                payment_reference = COALESCE(:payment_reference, payment_reference),
                vnp_response_code = COALESCE(:vnp_response_code, vnp_response_code),
                vnp_transaction_no = COALESCE(:vnp_transaction_no, vnp_transaction_no)
            WHERE invoice_id = :invoice_id
            """
        )
        self.db.execute(
            query,
            {
                "invoice_id": invoice_id,
                "status": status,
                "payment_reference": payment_reference,
                "vnp_response_code": vnp_response_code,
                "vnp_transaction_no": vnp_transaction_no,
            },
        )
        self.db.commit()
        return self.get(invoice_id)

    def _row_to_model(self, row) -> Invoice:
        return Invoice(
            invoice_id=row["invoice_id"],
            booking_id=row["booking_id"],
            user_id=row["user_id"],
            amount=float(row["amount"]),
            currency=row["currency"],
            status=row["status"],
        )
