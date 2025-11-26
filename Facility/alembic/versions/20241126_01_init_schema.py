"""Init facility schema"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20241126_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS Facility;
        CREATE TABLE Facility  (
            facility_id     INT AUTO_INCREMENT PRIMARY KEY,
            user_id         INT NOT NULL,
            name            VARCHAR(200) NOT NULL,
            address         VARCHAR(255),
            sport           VARCHAR(100),
            description     TEXT,
            opening_hours   VARCHAR(100) DEFAULT '24/7',
            contact_phone   VARCHAR(50),
            amenities       JSON,
            is_active       TINYINT(1) DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS Facility;")
