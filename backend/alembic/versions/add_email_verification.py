"""Add email verification fields to User

Revision ID: add_email_verification
Revises: e67294b4d1a8
Create Date: 2026-04-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_email_verification'
down_revision = 'e67294b4d1a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add verification_token column
    op.add_column('users', sa.Column('verification_token', sa.String(), nullable=True))
    
    # Add verification_token_expires column
    op.add_column('users', sa.Column('verification_token_expires', sa.DateTime(), nullable=True))
    
    # Create unique index on verification_token
    op.create_unique_constraint('uq_users_verification_token', 'users', ['verification_token'])


def downgrade() -> None:
    # Drop unique constraint
    op.drop_constraint('uq_users_verification_token', 'users', type_='unique')
    
    # Drop columns
    op.drop_column('users', 'verification_token_expires')
    op.drop_column('users', 'verification_token')
