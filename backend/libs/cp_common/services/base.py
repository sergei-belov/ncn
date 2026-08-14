import logging
from abc import abstractmethod


__all__ = ["BaseService"]


class BaseService:
    """Abstract lifecycle interface for an external service integration."""

    logger: logging.Logger

    def __init__(self):
        """Initialize the service logger."""

        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def start(self):
        """Start the service and acquire its external resources."""

        raise NotImplementedError()

    @abstractmethod
    async def stop(self):
        """Stop the service and release its external resources."""

        raise NotImplementedError()

    @abstractmethod
    async def ping(self):
        """Return whether the service is currently healthy."""

        raise NotImplementedError()
