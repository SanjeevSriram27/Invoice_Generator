"""add_seller_bank_details

Revision ID: 97b51850384b
Revises: f91f5b9faf34
Create Date: 2026-01-21 17:13:05.103537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97b51850384b'
down_revision: Union[str, None] = 'f91f5b9faf34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add seller bank details columns
    op.add_column('invoices', sa.Column('seller_bank_name', sa.String(length=200), nullable=True))
    op.add_column('invoices', sa.Column('seller_account_number', sa.String(length=50), nullable=True))
    op.add_column('invoices', sa.Column('seller_ifsc_code', sa.String(length=11), nullable=True))
    op.add_column('invoices', sa.Column('seller_account_holder_name', sa.String(length=200), nullable=True))
    op.add_column('invoices', sa.Column('seller_branch', sa.String(length=200), nullable=True))


def downgrade() -> None:
    # Remove seller bank details columns
    op.drop_column('invoices', 'seller_branch')
    op.drop_column('invoices', 'seller_account_holder_name')
    op.drop_column('invoices', 'seller_ifsc_code')
    op.drop_column('invoices', 'seller_account_number')
    op.drop_column('invoices', 'seller_bank_name')
