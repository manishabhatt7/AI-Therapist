from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

from app.config import settings
from app.database.database import Base
from app.database import models  # import your models

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate'
target_metadata = models.Base.metadata

# Use synchronous URL for Alembic migrations
# Replace asyncpg with psycopg2 for Alembic
sync_url = settings.DATABASE_URL.replace("asyncpg", "psycopg2")


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = sync_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()