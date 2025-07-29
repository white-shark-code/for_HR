from atexit import register
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from sys import stderr

from flask import Flask
from flask.app import App
from flask.logging import default_handler
from loguru._defaults import LOGURU_AUTOINIT
from loguru._logger import Core, Logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session
from werkzeug.utils import cached_property

from database import sync_session_maker
from settings import cfg


def create_logger(app: App) -> Logger:
    """Get the Flask app's logger and configure it if needed.

    The logger name will be the same as
    :attr:`app.import_name <flask.Flask.name>`.

    When :attr:`~flask.Flask.debug` is enabled, set the logger level to
    :data:`logging.DEBUG` if it is not set.

    If there is no handler for the logger's effective level, add a
    :class:`~logging.StreamHandler` for
    :func:`~flask.logging.wsgi_errors_stream` with a basic format.
    """
    logger: Logger = Logger(
        core=Core(),
        exception=None,
        depth=0,
        record=False,
        lazy=False,
        colors=False,
        raw=False,
        capture=True,
        patchers=[],
        extra={},
    )

    if LOGURU_AUTOINIT and stderr:
        logger.add(stderr)

    if app.debug and not logger.level:
        logger.level('DEBUG')

    logger.add(sink=default_handler, colorize=True, enqueue=True)
    logger.add(
        sink='test.log',
        level='INFO',
        format='{time} {level} {message}',
        enqueue=True
    )

    register(logger.remove)

    return logger


class TunnedFlask(Flask):
    """My Solution with loguru for logs & sqlalchemy"""

    @cached_property
    def logger(self) -> Logger:
        return create_logger(self)

    @staticmethod
    def get_sync_session() -> Generator[Session]:
        with sync_session_maker as session:
            yield session

    @staticmethod
    @asynccontextmanager
    async def get_async_session() -> AsyncGenerator[AsyncSession]:
        async_engine: AsyncEngine = create_async_engine(
            url = cfg.DATABASE_URL_ASYNC_ENGINE
        )
        async_session_maker: async_sessionmaker = async_sessionmaker(
            bind=async_engine,
            expire_on_commit=False
        )
        async with async_session_maker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
