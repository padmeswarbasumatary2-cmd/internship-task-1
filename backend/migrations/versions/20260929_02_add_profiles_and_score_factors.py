"""Add extracted profile and transparent score factors.

Revision ID: 20260929_02
Revises: 20260929_01
Create Date: 2026-09-29
"""
from alembic import op
import sqlalchemy as sa

revision = "20260929_02"
down_revision = "20260929_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("resumes", sa.Column("filename", sa.String(length=255), nullable=False, server_default="pasted-text.txt"))
    op.add_column("resumes", sa.Column("profile", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    op.add_column("analyses", sa.Column("skill_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("analyses", sa.Column("experience_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("analyses", sa.Column("education_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("analyses", sa.Column("semantic_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("analyses", sa.Column("recommendations", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
    with op.batch_alter_table("analyses") as batch_op:
        batch_op.create_check_constraint("ck_analyses_skill_score_range", "skill_score BETWEEN 0 AND 100")
        batch_op.create_check_constraint("ck_analyses_experience_score_range", "experience_score BETWEEN 0 AND 100")
        batch_op.create_check_constraint("ck_analyses_education_score_range", "education_score BETWEEN 0 AND 100")
        batch_op.create_check_constraint("ck_analyses_semantic_score_range", "semantic_score BETWEEN 0 AND 100")


def downgrade() -> None:
    with op.batch_alter_table("analyses") as batch_op:
        batch_op.drop_constraint("ck_analyses_semantic_score_range", type_="check")
        batch_op.drop_constraint("ck_analyses_education_score_range", type_="check")
        batch_op.drop_constraint("ck_analyses_experience_score_range", type_="check")
        batch_op.drop_constraint("ck_analyses_skill_score_range", type_="check")
    op.drop_column("analyses", "recommendations")
    op.drop_column("analyses", "semantic_score")
    op.drop_column("analyses", "education_score")
    op.drop_column("analyses", "experience_score")
    op.drop_column("analyses", "skill_score")
    op.drop_column("resumes", "profile")
    op.drop_column("resumes", "filename")
