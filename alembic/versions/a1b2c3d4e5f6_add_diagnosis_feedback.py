"""Add diagnosis_feedback table

Revision ID: a1b2c3d4e5f6
Revises: f5b6c7d8e9f0
Create Date: 2026-04-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f5b6c7d8e9f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'diagnosis_feedback',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('diagnosis_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('ai_was_correct', sa.Boolean(), nullable=False),
        sa.Column('feedback_category', sa.String(50), nullable=False),
        sa.Column('confidence_appropriate', sa.Boolean(), nullable=True),
        sa.Column('severity_mismatch', sa.Boolean(), server_default='false'),
        sa.Column('missed_diagnoses', sa.JSON(), nullable=True),
        sa.Column('incorrect_medications', sa.JSON(), nullable=True),
        sa.Column('feedback_notes', sa.Text(), nullable=True),
        sa.Column('ai_diagnosis_snapshot', sa.Text(), nullable=True),
        sa.Column('ai_confidence_snapshot', sa.Float(), nullable=True),
        sa.Column('ai_severity_snapshot', sa.String(20), nullable=True),
        sa.Column('ai_model_version_snapshot', sa.String(100), nullable=True),
        sa.Column('final_diagnosis_snapshot', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('synced_to_bq', sa.Boolean(), server_default='false'),
        sa.ForeignKeyConstraint(['diagnosis_id'], ['diagnoses.id']),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_diagnosis_feedback_diagnosis_id', 'diagnosis_feedback', ['diagnosis_id'])
    op.create_index('ix_diagnosis_feedback_reviewer_id', 'diagnosis_feedback', ['reviewer_id'])
    op.create_index('ix_diagnosis_feedback_category', 'diagnosis_feedback', ['feedback_category'])
    op.create_index('ix_diagnosis_feedback_synced', 'diagnosis_feedback', ['synced_to_bq'])


def downgrade() -> None:
    op.drop_index('ix_diagnosis_feedback_synced', table_name='diagnosis_feedback')
    op.drop_index('ix_diagnosis_feedback_category', table_name='diagnosis_feedback')
    op.drop_index('ix_diagnosis_feedback_reviewer_id', table_name='diagnosis_feedback')
    op.drop_index('ix_diagnosis_feedback_diagnosis_id', table_name='diagnosis_feedback')
    op.drop_table('diagnosis_feedback')
