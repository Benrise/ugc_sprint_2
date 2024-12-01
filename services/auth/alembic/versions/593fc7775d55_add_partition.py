"""add_partition

Revision ID: 593fc7775d55
Revises: 7909ba6c0209
Create Date: 2024-08-18 09:12:09.827383

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '593fc7775d55'
down_revision: Union[str, None] = '7909ba6c0209'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS partman;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_partman WITH SCHEMA partman;")

    op.execute("""
        CREATE TABLE IF NOT EXISTS login_history_temporary (
            id uuid NOT NULL,
            user_id uuid NOT NULL,
            logged_at timestamp without time zone NOT NULL,
            PRIMARY KEY (id, logged_at),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) PARTITION BY RANGE (logged_at);
    """)
    op.execute("""
        INSERT INTO login_history_temporary (id, user_id, logged_at)
        SELECT id, user_id, logged_at FROM login_history;
    """)

    op.execute("ALTER TABLE login_history RENAME TO history_history_old;")
    op.execute("ALTER TABLE login_history_temporary RENAME TO login_history;")

    op.execute("""
        SELECT partman.create_parent
        (
            'public.login_history',
            'logged_at',
            'native',
            'monthly'
        );
    """)

    op.execute("DROP TABLE IF EXISTS history_history_old;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pg_partman;")
    op.execute("DROP SCHEMA IF EXISTS partman CASCADE;")

    op.execute("""
        CREATE TABLE IF NOT EXISTS login_history_temporary (
            id uuid NOT NULL,
            user_id uuid NOT NULL,
            logged_at timestamp without time zone NOT NULL,
            PRIMARY KEY (id, logged_at),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    op.execute("""
        INSERT INTO login_history_temporary (id, user_id, logged_at)
        SELECT id, user_id, logged_at FROM login_history;
    """)

    op.execute("ALTER TABLE login_history RENAME TO history_history_old;")
    op.execute("ALTER TABLE login_history_temporary RENAME TO login_history;")

    op.execute("DROP TABLE IF EXISTS history_history_old;")
