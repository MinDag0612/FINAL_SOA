"""Init session schema"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20241126_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS Session;
        CREATE TABLE Session (
            session_id   INT AUTO_INCREMENT PRIMARY KEY,
            user_id      INT NOT NULL,
            device       VARCHAR(100),
            ip_address   VARCHAR(45),
            user_agent   VARCHAR(255),
            is_active    TINYINT(1) DEFAULT 1,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS Session;")
