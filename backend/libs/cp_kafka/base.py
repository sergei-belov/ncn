from abc import abstractmethod
from typing import (
    Callable,
    Protocol,
)

from pydantic import BaseModel


class Broker(Protocol):
    """Protocol for producing and consuming typed broker messages."""

    @abstractmethod
    async def start(self):
        """Start broker connections and registered listeners."""

    @abstractmethod
    async def stop(self):
        """Stop listeners and close broker connections."""

    @abstractmethod
    async def produce(self, topic: str, message: BaseModel, key: str | None = None):
        """Produce a typed message to a broker topic."""

    @classmethod
    @abstractmethod
    def listen(cls, topic: str, messages_count: int = 1, interval_period_sec: float = 1.0, delay: int = 0) -> Callable:
        """Register a decorated callback for typed topic messages."""

        pass
