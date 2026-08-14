import logging


__all__ = [
    "BaseCache",
]


class BaseCache:
    """Base cache component with a class-scoped logger."""

    logger: logging.Logger

    def __init__(self):
        """Initialize the cache logger."""

        self.logger = logging.getLogger(self.__class__.__name__)
