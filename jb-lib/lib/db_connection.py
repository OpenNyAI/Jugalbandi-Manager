import os
import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

db_name = os.getenv("POSTGRES_DATABASE_NAME")
db_user = os.getenv("POSTGRES_DATABASE_USERNAME")
db_password = os.getenv("POSTGRES_DATABASE_PASSWORD")
db_host = os.getenv("POSTGRES_DATABASE_HOST")
db_port = os.getenv("POSTGRES_DATABASE_PORT")

# Construct the SQLAlchemy connection URL using URL class
db_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_async_engine(
    db_url,
    future=True,
    echo=False,
    max_overflow=50,
    pool_size=25,
    pool_timeout=60,
    pool_recycle=3600,
    pool_pre_ping=True
)

async_session = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)

metadata = sqlalchemy.MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

Base = declarative_base(metadata=metadata)
