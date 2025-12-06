"""Add customer fields to bookings table"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20251206_01"
down_revision = "20241126_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add customer_name, customer_phone, customer_email columns"""
    op.execute(
        """
        ALTER TABLE bookings
        ADD COLUMN customer_name VARCHAR(255) AFTER payment_reference,
        ADD COLUMN customer_phone VARCHAR(20) AFTER customer_name,
        ADD COLUMN customer_email VARCHAR(255) AFTER customer_phone;
        """
    )


def downgrade() -> None:
    """Remove customer fields"""
    op.execute(
        """
        ALTER TABLE bookings
        DROP COLUMN customer_email,
        DROP COLUMN customer_phone,
        DROP COLUMN customer_name;
        """
    )
