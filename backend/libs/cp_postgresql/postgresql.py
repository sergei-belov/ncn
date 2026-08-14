import re
import socket
from contextlib import suppress
from typing import Literal
from urllib.parse import quote

from psycopg2 import errorcodes
from sqlalchemy import (
    MetaData,
    Table,
    select,
)
from sqlalchemy.exc import (
    DatabaseError,
    DBAPIError,
)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    engine,
    session,
)
from sqlalchemy.orm import declarative_base

from libs.cp_common import BaseService
from libs.cp_postgresql.base_database import Database
from libs.cp_postgresql.models.exceptions import (
    DatabaseException,
    ForeignKeyNotFoundException,
    IncorrectColumnValueException,
    ObjectAlreadyExistsException,
    TableNotFoundException,
)


SQLSTATE_TO_DB_EXCEPTION_HM = {
    errorcodes.UNIQUE_VIOLATION: ObjectAlreadyExistsException,
    errorcodes.UNDEFINED_TABLE: TableNotFoundException,
    errorcodes.FOREIGN_KEY_VIOLATION: ForeignKeyNotFoundException,
    errorcodes.STRING_DATA_RIGHT_TRUNCATION: IncorrectColumnValueException,
    errorcodes.NOT_NULL_VIOLATION: IncorrectColumnValueException,
    errorcodes.INVALID_TEXT_REPRESENTATION: IncorrectColumnValueException,
}


class SessionHandler:
    """Manage one transactional asynchronous session.

    Successful contexts are committed automatically. Failed contexts are
    rolled back, and known SQLAlchemy failures are normalized to shared
    database exceptions.
    """

    def __init__(self, session: session.AsyncSession):  # pylint:disable=redefined-outer-name
        """Initialize the handler with an asynchronous session.

        Args:
            session: Session managed by the context manager.
        """
        self.session = session

    async def __aenter__(self) -> session.AsyncSession:
        """Begin a transaction and return the managed session."""

        await self.session.begin()
        return self.session

    async def __aexit__(self, exception_type: type, exception: Exception, _traceback) -> None:
        """Commit success or roll back and normalize a failure."""

        if exception_type:
            await self.session.rollback()
            await self.session.close()
            if issubclass(exception_type, DatabaseError) or issubclass(exception_type, DBAPIError):
                raise self._create_strict_db_exception(exception) from exception  # type: ignore
            else:
                raise exception from exception

        try:
            await self.commit()
        except Exception as exc:
            await self.session.rollback()
            raise exc
        finally:
            with suppress(Exception):
                await self.session.close()
        return None

    async def commit(self) -> None:
        """Commit the session and normalize database errors.

        Raises:
            DatabaseException: If SQLAlchemy reports a database failure.
        """
        try:
            await self.session.commit()
        except DatabaseError as exc:
            raise self._create_strict_db_exception(exc) from exc
        return None

    @staticmethod
    def _create_strict_db_exception(common_exception: DatabaseError) -> DatabaseException:
        """Map a SQLAlchemy database error to a specific shared exception."""

        strict_exception = DatabaseException
        if hasattr(common_exception.orig, "sqlstate"):
            strict_exception = SQLSTATE_TO_DB_EXCEPTION_HM.get(common_exception.orig.sqlstate) or strict_exception
        reason = re.sub(r"<[^>]*>: ", "", str(common_exception.orig))
        return strict_exception(reason)


class PostgreSQL(BaseService, Database):  # pylint: disable=too-many-instance-attributes
    """Provide asynchronous PostgreSQL engine and transaction management."""

    _username: str
    _password: str
    _host: str
    _port: int
    _database: str
    _echo_pool: Literal["debug"] | bool
    _pool_size: int
    _connection_retry_period_sec: float
    _statement_timeout_sec: int

    _engine: engine.AsyncEngine
    _metadata: MetaData
    _session_maker: async_sessionmaker[session.AsyncSession]
    _fetched_tables: dict[str, Table]
    _session: session.AsyncSession
    _autocommit: bool

    def __init__(
        self,
        username: str,
        password: str,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        echo_pool: Literal["debug"] | bool = False,
        pool_size: int = 10,
        connection_retry_period_sec: float = 5,
        statement_timeout_sec: int = 5,
    ):
        """Initialize PostgreSQL connection and pool settings.

        Args:
            username: Database username.
            password: Database password.
            host: Database host name.
            port: Database TCP port.
            database: Database name.
            echo_pool: SQLAlchemy pool logging mode.
            pool_size: Number of persistent pooled connections.
            connection_retry_period_sec: Delay used by connection retry clients.
            statement_timeout_sec: Server-side statement timeout in seconds.
        """
        super().__init__()
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._database = database
        self._echo_pool = echo_pool
        self._pool_size = pool_size
        self._connection_retry_period_sec = connection_retry_period_sec
        self._fetched_tables = {}
        self._metadata = MetaData()
        self._base = declarative_base(metadata=self._metadata)
        self._autocommit = True
        self._statement_timeout_sec = statement_timeout_sec

    def _make_url(self) -> str:
        """Build an escaped asynchronous PostgreSQL connection URL."""

        return (
            f"postgresql+asyncpg://{quote(self._username)}:"
            f"{quote(self._password)}@{self._host}:{self._port}/{self._database}"
        )

    async def connect(self) -> None:
        """Create the asynchronous engine and session factory."""

        try:
            self._engine = create_async_engine(
                url=self._make_url(),
                pool_size=self._pool_size,
                echo_pool=self._echo_pool,
                pool_pre_ping=True,
                connect_args={
                    "server_settings": {
                        "statement_timeout": str(self._statement_timeout_sec * 1000),
                    },
                },
            )
            self._session_maker = async_sessionmaker(bind=self._engine, expire_on_commit=False)
        except socket.gaierror:
            dsn = re.sub(r":(?P<password>[^\s:]+)@", ":****@", self._make_url())
            self.logger.exception(f"Invalid postgresql connection params: {dsn}")
            raise

    def session(self) -> SessionHandler:
        """Create a transactional session context manager."""

        return SessionHandler(session=self._session_maker())

    async def start(self):
        """Start the database service by creating its engine."""

        await self.connect()

    async def stop(self):
        """Stop the database service."""

        pass

    async def ping(self) -> bool:
        """Return whether a trivial query succeeds."""

        try:
            async with self.session() as session:
                return (await session.execute(select(1))).fetchone() == (1,)
        except Exception:
            self.logger.exception("Failed when try to check postgresql health")
            return False
