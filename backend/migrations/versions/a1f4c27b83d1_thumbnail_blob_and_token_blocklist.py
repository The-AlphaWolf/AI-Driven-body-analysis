"""Store thumbnails in the database and persist the JWT blocklist

Thumbnails previously lived on the local filesystem, which is ephemeral on
the hosts this app is deployed to — every redeploy silently orphaned them.
The revoked-token set was process-local, so a logout was undone by any
restart and invisible to sibling workers.

Revision ID: a1f4c27b83d1
Revises: 9e10b85b789f
Create Date: 2026-07-24 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1f4c27b83d1'
down_revision = '9e10b85b789f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('thumbnail', sa.LargeBinary(), nullable=True))
        batch_op.drop_column('thumbnail_path')

    op.create_table(
        'token_blocklist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(length=36), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('token_blocklist', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_token_blocklist_jti'), ['jti'], unique=True)
        batch_op.create_index(
            batch_op.f('ix_token_blocklist_expires_at'), ['expires_at'], unique=False
        )


def downgrade():
    with op.batch_alter_table('token_blocklist', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_token_blocklist_expires_at'))
        batch_op.drop_index(batch_op.f('ix_token_blocklist_jti'))

    op.drop_table('token_blocklist')

    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('thumbnail_path', sa.String(length=500), nullable=True))
        batch_op.drop_column('thumbnail')
