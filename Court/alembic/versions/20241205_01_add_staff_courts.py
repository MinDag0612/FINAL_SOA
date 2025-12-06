"""Add staff_courts junction table"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20241205_01"
down_revision = "20241126_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS staff_courts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            staff_id INT NOT NULL COMMENT 'FK to Auth.User_Infor.user_id',
            court_id INT NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_staff_court (staff_id, court_id),
            FOREIGN KEY (court_id) REFERENCES Court(court_id) ON DELETE CASCADE,
            INDEX idx_staff_id (staff_id),
            INDEX idx_court_id (court_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS staff_courts;")
