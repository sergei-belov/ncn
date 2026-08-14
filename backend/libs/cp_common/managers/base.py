import logging


__all__ = ["BaseManager"]


class BaseManager:
    """Base manager component with a class-scoped logger."""

    logger: logging.Logger

    def __init__(self):
        """Initialize the manager logger."""

        self.logger = logging.getLogger(self.__class__.__name__)
