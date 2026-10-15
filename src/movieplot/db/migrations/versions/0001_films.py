"""Table des fiches de films.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "films",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tmdb_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("imdb_id", sa.String(20)),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("original_title", sa.String(300), nullable=False),
        sa.Column("release_date", sa.String(10), nullable=False),
        sa.Column("overview", sa.Text(), nullable=False),
        sa.Column("poster_url", sa.String(500)),
        sa.Column("vote_average", sa.Float(), nullable=False),
        sa.Column("analysis", sa.JSON(), nullable=False),
        sa.Column("had_subtitles", sa.Boolean(), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("films")
