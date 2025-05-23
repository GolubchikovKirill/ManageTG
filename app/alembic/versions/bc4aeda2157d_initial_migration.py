"""Initial migration

Revision ID: bc4aeda2157d
Revises: 
Create Date: 2025-04-28 08:33:30.718277

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc4aeda2157d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('channels',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('open', 'private', name='channel_status'), nullable=False),
    sa.Column('request_count', sa.Integer(), nullable=False),
    sa.Column('accepted_request_count', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_channels_id'), 'channels', ['id'], unique=False)
    op.create_index(op.f('ix_channels_name'), 'channels', ['name'], unique=True)
    op.create_table('proxy',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ip_address', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('login', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proxy_id'), 'proxy', ['id'], unique=False)
    op.create_index(op.f('ix_proxy_ip_address'), 'proxy', ['ip_address'], unique=True)
    op.create_index(op.f('ix_proxy_login'), 'proxy', ['login'], unique=True)
    op.create_index(op.f('ix_proxy_password'), 'proxy', ['password'], unique=True)
    op.create_table('accounts',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('is_authorized', sa.Boolean(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('api_id', sa.Integer(), nullable=False),
    sa.Column('api_hash', sa.String(), nullable=False),
    sa.Column('proxy_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['proxy_id'], ['proxy.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)
    op.create_index(op.f('ix_accounts_last_name'), 'accounts', ['last_name'], unique=False)
    op.create_index(op.f('ix_accounts_name'), 'accounts', ['name'], unique=False)
    op.create_index(op.f('ix_accounts_phone_number'), 'accounts', ['phone_number'], unique=False)
    op.create_index(op.f('ix_accounts_proxy_id'), 'accounts', ['proxy_id'], unique=False)
    op.create_table('comment_actions',
    sa.Column('channel_id', sa.Integer(), nullable=False),
    sa.Column('positive_count', sa.Integer(), nullable=False),
    sa.Column('neutral_count', sa.Integer(), nullable=False),
    sa.Column('critical_count', sa.Integer(), nullable=False),
    sa.Column('question_count', sa.Integer(), nullable=False),
    sa.Column('custom_prompt', sa.Text(), nullable=True),
    sa.Column('custom_count', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('action_time', sa.Integer(), nullable=False),
    sa.Column('random_percentage', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comment_actions_channel_id'), 'comment_actions', ['channel_id'], unique=False)
    op.create_index(op.f('ix_comment_actions_id'), 'comment_actions', ['id'], unique=False)
    op.create_table('reaction_actions',
    sa.Column('channel_id', sa.Integer(), nullable=False),
    sa.Column('emoji', sa.String(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('action_time', sa.Integer(), nullable=False),
    sa.Column('random_percentage', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reaction_actions_channel_id'), 'reaction_actions', ['channel_id'], unique=False)
    op.create_index(op.f('ix_reaction_actions_id'), 'reaction_actions', ['id'], unique=False)
    op.create_table('view_actions',
    sa.Column('channel_id', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.Column('post_link', sa.Text(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('action_time', sa.Integer(), nullable=False),
    sa.Column('random_percentage', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_view_actions_channel_id'), 'view_actions', ['channel_id'], unique=False)
    op.create_index(op.f('ix_view_actions_id'), 'view_actions', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_view_actions_id'), table_name='view_actions')
    op.drop_index(op.f('ix_view_actions_channel_id'), table_name='view_actions')
    op.drop_table('view_actions')
    op.drop_index(op.f('ix_reaction_actions_id'), table_name='reaction_actions')
    op.drop_index(op.f('ix_reaction_actions_channel_id'), table_name='reaction_actions')
    op.drop_table('reaction_actions')
    op.drop_index(op.f('ix_comment_actions_id'), table_name='comment_actions')
    op.drop_index(op.f('ix_comment_actions_channel_id'), table_name='comment_actions')
    op.drop_table('comment_actions')
    op.drop_index(op.f('ix_accounts_proxy_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_phone_number'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_name'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_last_name'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_id'), table_name='accounts')
    op.drop_table('accounts')
    op.drop_index(op.f('ix_proxy_password'), table_name='proxy')
    op.drop_index(op.f('ix_proxy_login'), table_name='proxy')
    op.drop_index(op.f('ix_proxy_ip_address'), table_name='proxy')
    op.drop_index(op.f('ix_proxy_id'), table_name='proxy')
    op.drop_table('proxy')
    op.drop_index(op.f('ix_channels_name'), table_name='channels')
    op.drop_index(op.f('ix_channels_id'), table_name='channels')
    op.drop_table('channels')
    # ### end Alembic commands ###
