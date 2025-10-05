"""merge heads 963c1ca67ad3 and b1c2d3e4f5a6

Revision ID: merge_963c1_b1c2
Revises: 963c1ca67ad3, b1c2d3e4f5a6
Create Date: 2025-10-04 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'merge_963c1_b1c2'
down_revision: Union[str, Sequence[str], None] = ('963c1ca67ad3', 'b1c2d3e4f5a6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Merge-only revision; no DB schema changes.
    pass


def downgrade() -> None:
    pass
