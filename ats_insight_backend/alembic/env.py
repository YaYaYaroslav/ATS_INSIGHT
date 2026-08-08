from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Імпортуємо застосунок, щоб мати доступ до settings і Base.metadata.
# Завдяки app/models/__init__.py всі моделі (User, Resume, Job, Analysis)
# вже зареєстровані на Base.metadata на момент цього імпорту.
from app.core.config import settings
from app.core.database import Base
from app.models import user, resume, job, analysis  # noqa: F401

config = context.config

# Підставляємо реальний URL з settings (.env), а не з alembic.ini —
# єдине джерело правди для конфігурації залишається app/core/config.py.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Генерує SQL-скрипти без підключення до БД (alembic upgrade --sql)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Стандартний режим: підключається до БД і застосовує міграції напряму."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
