"""add security fields for token rotation and account lockout

Revision ID: 003
Revises: 002
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Add security fields to users table."""
    # Add refresh token version for token rotation
    op.add_column('users',
        sa.Column('refresh_token_version', sa.Integer(),
                  nullable=False, server_default='0')
    )

    # Add account lockout fields
    op.add_column('users',
        sa.Column('failed_login_attempts', sa.Integer(),
                  nullable=False, server_default='0')
    )
    op.add_column('users',
        sa.Column('locked_until', sa.DateTime(timezone=True),
                  nullable=True)
    )


def downgrade():
    """Remove security fields from users table."""
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'refresh_token_version')
