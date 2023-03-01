"""empty message

Revision ID: 5328f1c9871b
Revises: 006d4747f858
Create Date: 2023-03-01 08:14:09.598924

"""

# revision identifiers, used by Alembic.
revision = '5328f1c9871b'
down_revision = '006d4747f858'

from alembic import op
import sqlalchemy as sa


def upgrade():
    try:
        op.add_column('policycondition', sa.Column('undef', sa.Unicode(length=255), nullable=False))
    except (OperationalError, ProgrammingError, InternalError) as exx:
        print("Looks like the column undef already exists in the policycondition table.")
        print(exx)
    except Exception as exx:
        print("Could not add undef to policycondition table.")
        print (exx)


def downgrade():
    pass
