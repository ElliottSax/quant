"""Add 2FA and email verification fields.

Revision ID: 005
Revises: 004
Create Date: 2025-01-22
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add email verification and 2FA fields to users table."""
    # Email verification fields
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "users",
        sa.Column("email_verification_token", sa.String(255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("email_verification_sent_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Two-Factor Authentication fields
    op.add_column(
        "users",
        sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "users",
        sa.Column("totp_secret", sa.String(64), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("totp_backup_codes", sa.Text(), nullable=True),
    )

    # Index for email verification token lookups
    op.create_index(
        "ix_users_email_verification_token",
        "users",
        ["email_verification_token"],
        unique=False,
    )


def downgrade() -> None:
    """Remove email verification and 2FA fields."""
    op.drop_index("ix_users_email_verification_token", table_name="users")
    op.drop_column("users", "totp_backup_codes")
    op.drop_column("users", "totp_secret")
    op.drop_column("users", "totp_enabled")
    op.drop_column("users", "email_verification_sent_at")
    op.drop_column("users", "email_verification_token")
    op.drop_column("users", "email_verified")
