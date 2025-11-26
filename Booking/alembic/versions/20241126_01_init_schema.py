"""Init booking schema without hold_expires_at"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20241126_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS booking_items;
        DROP TABLE IF EXISTS bookings;

        CREATE TABLE bookings (
            booking_id       INT AUTO_INCREMENT PRIMARY KEY,
            user_id          INT NOT NULL,
            facility_id      INT NOT NULL,
            status           VARCHAR(20) NOT NULL DEFAULT 'pending',
            total_amount     DECIMAL(12,2) NOT NULL,
            payment_status   VARCHAR(20),
            payment_method   VARCHAR(50),
            payment_reference VARCHAR(100),
            note             TEXT,
            paid_at          DATETIME,
            cancel_reason    TEXT,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE booking_items (
            item_id     INT AUTO_INCREMENT PRIMARY KEY,
            booking_id  INT NOT NULL,
            court_id    INT NOT NULL,
            start_time  DATETIME NOT NULL,
            end_time    DATETIME NOT NULL,
            price       DECIMAL(12,2) NOT NULL,
            CONSTRAINT fk_booking_item_booking FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE INDEX idx_booking_court_time ON booking_items (court_id, start_time, end_time);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS booking_items;
        DROP TABLE IF EXISTS bookings;
        """
    )
