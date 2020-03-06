"""fix a typo

Revision ID: 09a0cdcdf25a
Revises: a4d8296246f3
Create Date: 2020-03-05 21:59:57.412275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09a0cdcdf25a'
down_revision = 'a4d8296246f3'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('employee', 'loyalty_id', new_column_name='employee_id')


def downgrade():
    op.alter_column('employee', 'employee_id', new_column_name='loyalty_id')
