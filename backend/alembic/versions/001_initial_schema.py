"""Initial database schema migration (users, prediction_records, audit_events)

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-30 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Create prediction_records table
    op.create_table(
        'prediction_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False, server_default='1.0.0'),
        sa.Column('outcome', sa.String(length=50), nullable=False),
        sa.Column('probability', sa.Float(), nullable=True),
        sa.Column('explanation', sa.JSON(), nullable=False),
        sa.Column('input_snapshot', sa.JSON(), nullable=False),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_prediction_records_id'), 'prediction_records', ['id'], unique=False)
    op.create_index(op.f('ix_prediction_records_user_id'), 'prediction_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_prediction_records_created_at'), 'prediction_records', ['created_at'], unique=False)
    op.create_index(op.f('ix_prediction_records_request_id'), 'prediction_records', ['request_id'], unique=False)
    op.create_index('ix_prediction_records_user_created', 'prediction_records', ['user_id', 'created_at'], unique=False)

    # 3. Create audit_events table
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('actor_user_id', sa.String(length=36), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('target_type', sa.String(length=100), nullable=True),
        sa.Column('target_id', sa.String(length=100), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_events_id'), 'audit_events', ['id'], unique=False)
    op.create_index(op.f('ix_audit_events_actor_user_id'), 'audit_events', ['actor_user_id'], unique=False)
    op.create_index(op.f('ix_audit_events_event_type'), 'audit_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_audit_events_created_at'), 'audit_events', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('prediction_records')
    op.drop_table('users')

