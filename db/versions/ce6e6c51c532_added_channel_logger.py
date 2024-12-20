"""added_channel_logger

Revision ID: ce6e6c51c532
Revises: 6bfbb039a05d
Create Date: 2024-10-24 15:10:47.918481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce6e6c51c532'
down_revision = 'fe0b2e850214'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jb_channel_logger',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('turn_id', sa.String(), nullable=True),
    sa.Column('channel_id', sa.String(), nullable=True),
    sa.Column('channel_name', sa.String(), nullable=True),
    sa.Column('msg_intent', sa.String(), nullable=True),
    sa.Column('msg_type', sa.String(), nullable=True),
    sa.Column('sent_to_service', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['turn_id'], ['jb_api_logger.turn_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('jb_channel_logger')
    # ### end Alembic commands ###