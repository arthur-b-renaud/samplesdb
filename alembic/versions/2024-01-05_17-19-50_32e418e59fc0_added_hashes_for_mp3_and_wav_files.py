"""added hashes for mp3 and wav files

Revision ID: 32e418e59fc0
Revises: 0bd538833c1a
Create Date: 2024-01-05 17:19:50.740364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32e418e59fc0'
down_revision: Union[str, None] = '0bd538833c1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('track', sa.Column('wav_etag_hash', sa.String(), nullable=True))
    op.add_column('track', sa.Column('mp3_etag_hash', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('track', 'mp3_etag_hash')
    op.drop_column('track', 'wav_etag_hash')
    # ### end Alembic commands ###
