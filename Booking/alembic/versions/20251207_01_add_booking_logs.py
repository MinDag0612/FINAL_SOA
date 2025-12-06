"""Add booking_logs table for audit history"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20251207_01"
down_revision = "20251206_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE booking_logs (
            log_id               INT AUTO_INCREMENT PRIMARY KEY,
            booking_id           INT NOT NULL,
            action_type          VARCHAR(50) NOT NULL,
            old_status           VARCHAR(20),
            new_status           VARCHAR(20),
            old_payment_status   VARCHAR(20),
            new_payment_status   VARCHAR(20),
            changed_by_user_id   INT,
            changed_by_role      VARCHAR(20) DEFAULT 'system',
            reason               TEXT,
            changes_json         JSON,
            created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_booking_logs_booking FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE INDEX idx_booking_logs_booking ON booking_logs (booking_id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS booking_logs;
        """
    )
