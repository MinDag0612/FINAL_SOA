"""Init court schema"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20241126_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS Court;
        CREATE TABLE Court (
            court_id        INT AUTO_INCREMENT PRIMARY KEY,
            facility_id     INT NOT NULL,
            name            VARCHAR(200) NOT NULL,
            surface_type    VARCHAR(100),
            hourly_rate     DECIMAL(10,2),
            description     TEXT,
            available_hours JSON NULL COMMENT 'NULL = open 24/7, otherwise list of hourly start times',
            is_active       TINYINT(1) DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS Court;")
