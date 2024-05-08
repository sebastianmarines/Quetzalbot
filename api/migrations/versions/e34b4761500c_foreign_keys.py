"""foreign_keys

Revision ID: e34b4761500c
Revises: 0124d644a4a2
Create Date: 2024-04-19 10:03:47.381597

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "e34b4761500c"
down_revision: Union[str, None] = "0124d644a4a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("change", schema=None) as batch_op:
        batch_op.drop_column("elem_id")
        batch_op.drop_column("element_id")
        batch_op.drop_column("active")

    with op.batch_alter_table("element", schema=None) as batch_op:
        batch_op.add_column(sa.Column("active", sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("element", schema=None) as batch_op:
        batch_op.drop_column("active")

    with op.batch_alter_table("change", schema=None) as batch_op:
        batch_op.add_column(sa.Column("active", sa.BOOLEAN(), nullable=False))
        batch_op.add_column(sa.Column("element_id", sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column("elem_id", sa.INTEGER(), nullable=True))

    # ### end Alembic commands ###
