import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base


class DBSessionHandler:
    __async_session__ = None
    __sync_session__ = None
    __db_name__ = os.getenv("POSTGRES_DATABASE_NAME")
    __db_user__ = os.getenv("POSTGRES_DATABASE_USERNAME")
    __db_password__ = os.getenv("POSTGRES_DATABASE_PASSWORD")
    __db_host__ = os.getenv("POSTGRES_DATABASE_HOST")
    __db_port__ = os.getenv("POSTGRES_DATABASE_PORT")

    # Construct the SQLAlchemy connection URL
    async_db_url = f"postgresql+asyncpg://{__db_user__}:{__db_password__}@{__db_host__}:{__db_port__}/{__db_name__}"
    sync_db_url = f"postgresql://{__db_user__}:{__db_password__}@{__db_host__}:{__db_port__}/{__db_name__}"

    @classmethod
    def __initialise_async_session__(cls):
        if cls.__async_session__ is None:
            engine = create_async_engine(
                cls.async_db_url,
                future=True,
                echo=False,
                max_overflow=50,
                pool_size=25,
                pool_timeout=60,
                pool_recycle=3600,
                pool_pre_ping=True,
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
            cls.__async_session__ = async_session

    @classmethod
    def __initialise_sync_session__(cls):
        if cls.__sync_session__ is None:
            engine = create_engine(
                cls.sync_db_url,
                future=True,
                echo=False,
                max_overflow=50,
                pool_size=25,
                pool_timeout=60,
                pool_recycle=3600,
                pool_pre_ping=True,
            )
            sync_session = sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
            cls.__sync_session__ = sync_session

    @classmethod
    def get_async_session(cls):
        if cls.__async_session__ is None:
            cls.__initialise_async_session__()
        return cls.__async_session__()

    @classmethod
    def get_sync_session(cls):
        if cls.__sync_session__ is None:
            cls.__initialise_sync_session__()
        return cls.__sync_session__()
