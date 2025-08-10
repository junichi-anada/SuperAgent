"""Add agent_images table for photo gallery

Revision ID: 6e337a675946
Revises: 89e8383c8715
Create Date: 2025-08-08 06:02:16.897296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e337a675946'
down_revision: Union[str, Sequence[str], None] = '89e8383c8715'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create agent_images table
    op.create_table('agent_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_images_id'), 'agent_images', ['id'], unique=False)
    op.create_index(op.f('ix_agent_images_agent_id'), 'agent_images', ['agent_id'], unique=False)
    
    # Migrate existing agent image_urls to the new table
    # First, we need to insert existing images as primary images
    op.execute("""
        INSERT INTO agent_images (agent_id, image_url, is_primary, created_at)
        SELECT id, image_url, true, created_at
        FROM agents
        WHERE image_url IS NOT NULL
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # First, update agents table with primary images from agent_images
    op.execute("""
        UPDATE agents
        SET image_url = ai.image_url
        FROM agent_images ai
        WHERE agents.id = ai.agent_id AND ai.is_primary = true
    """)
    
    # Drop the agent_images table
    op.drop_index(op.f('ix_agent_images_agent_id'), table_name='agent_images')
    op.drop_index(op.f('ix_agent_images_id'), table_name='agent_images')
    op.drop_table('agent_images')