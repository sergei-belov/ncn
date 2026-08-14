from enum import Enum
from typing import Union


class OperationStatus(Enum):
    """Success or failure status of a storage operation."""

    success = True
    failed = False


class OperationResult:
    """Result returned by a storage read or write operation."""

    status: OperationStatus
    message: str

    def __init__(self, status: Union[OperationStatus, bool], message: str = "") -> None:
        """Initialize an operation result.

        Args:
            status: Enum member or boolean success value.
            message: Optional human-readable result detail.
        """
        self.status = OperationStatus(status)
        self.message = message

    @property
    def ok(self) -> bool:
        """Return whether the operation succeeded."""

        return self.status == OperationStatus.success

    def __str__(self) -> str:
        """Return a readable operation result."""

        message: str = f", message={self.message}" if self.message else ""
        return f"{self.__class__.__name__}: status={self.status}{message}"

    def __repr__(self) -> str:
        """Return a developer-facing operation result."""

        message: str = f", message={self.message}" if self.message else ""
        return f"{self.__class__.__name__}: status={self.status}{message}"
