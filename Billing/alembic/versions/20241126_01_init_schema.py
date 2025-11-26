"""Init billing schema"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20241126_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS invoices;

        CREATE TABLE invoices (
            invoice_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT NOT NULL,
            user_id INT NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            currency VARCHAR(10) NOT NULL DEFAULT 'VND',
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            payment_method VARCHAR(50),
            payment_url TEXT,
            payment_reference VARCHAR(100),
            vnp_txn_ref VARCHAR(100),
            vnp_response_code VARCHAR(10),
            vnp_transaction_no VARCHAR(50),
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS invoices;")
