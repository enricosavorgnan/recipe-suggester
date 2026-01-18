"""Add jobs tables

Revision ID: 003
Revises: 002
Create Date: 2026-01-18 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('ingredients_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('running', 'completed', 'failed', name='jobstatus'), nullable=False),
        sa.Column('ingredients_json', sa.Text(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingredients_jobs_id'), 'ingredients_jobs', ['id'], unique=False)

    op.create_table('recipe_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('running', 'completed', 'failed', name='jobstatus'), nullable=False),
        sa.Column('recipe_json', sa.Text(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipe_jobs_id'), 'recipe_jobs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_recipe_jobs_id'), table_name='recipe_jobs')
    op.drop_table('recipe_jobs')
    op.drop_index(op.f('ix_ingredients_jobs_id'), table_name='ingredients_jobs')
    op.drop_table('ingredients_jobs')
    op.execute('DROP TYPE jobstatus')
