"""add users

Revision ID: fee0fd5b1965
Revises:
Create Date: 2022-05-21 01:04:51.467232

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fee0fd5b1965"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("agreed_to_rules", sa.Boolean(), nullable=False),
        sa.Column("agreed_to_code_of_conduct", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users")
    # ### end Alembic commands ###
