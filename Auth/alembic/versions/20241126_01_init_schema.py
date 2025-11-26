"""Init auth schema"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20241126_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS User_Infor;
        CREATE TABLE User_Infor (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            fullname VARCHAR(255),
            password VARCHAR(255),
            role VARCHAR(50)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS User_Infor;")
