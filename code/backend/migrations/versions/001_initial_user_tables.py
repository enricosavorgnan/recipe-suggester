"""Initial user tables

Revision ID: 001
Revises:
Create Date: 2024-01-17

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create user_auth table
    op.create_table(
        'user_auth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.Enum('email', 'google', name='authprovider'), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('provider_user_id', sa.String(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_auth_id'), 'user_auth', ['id'], unique=False)
    op.create_index(op.f('ix_user_auth_provider_user_id'), 'user_auth', ['provider_user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_auth_provider_user_id'), table_name='user_auth')
    op.drop_index(op.f('ix_user_auth_id'), table_name='user_auth')
    op.drop_table('user_auth')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.execute('DROP TYPE authprovider')
