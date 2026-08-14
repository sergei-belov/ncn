from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    TypeVar,
)

from sqlalchemy.ext.asyncio.session import AsyncSession

from libs.cp_postgresql import PostgreSQL


F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def get_session(db_instance: PostgreSQL):
    """Create a dependency generator for database sessions.

    Args:
        db_instance: Database service that creates sessions.

    Returns:
        An asynchronous generator function yielding managed sessions.
    """

    async def session_generator():
        """Yield one transaction-managed asynchronous session."""

        async with db_instance.session() as session:
            yield session

    return session_generator


def db_session(db_instance: PostgreSQL):
    """
    Decorator to provide a database session to an asynchronous function.

    This decorator ensures that the decorated function receives an `AsyncSession`
    object either from the function call or by creating a new session if one is not provided.

    Args:
        db_instance (PostgreSQL): The database instance used to create sessions.

    Returns:
        Callable: The decorated asynchronous function with session management.

    Example:
        @db_session(db_instance)
        async def fetch_data(param1: str, session: AsyncSession):
            # Use the session to perform database operations
            result = await session.execute(...)
            return result

        # Usage without explicitly providing a session
        await fetch_data("example_param")

        # Usage with an existing session
        async with db_instance.session() as session:
            await fetch_data("example_param", session=session)
    """

    def decorator(func: F) -> F:
        """Wrap an asynchronous function with optional session injection."""

        @wraps(func)
        async def wrapper(*args, session: AsyncSession | None = None, **kwargs):
            """Call the function with the supplied or a newly created session."""

            if not session:
                async with db_instance.session() as session:
                    return await func(*args, **kwargs, session=session)
            else:
                return await func(*args, **kwargs, session=session)

        return wrapper

    return decorator
