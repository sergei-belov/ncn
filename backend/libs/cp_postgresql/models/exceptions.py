class DatabaseException(Exception):
    """Base exception for normalized persistence failures."""

    pass


class ObjectAlreadyExistsException(DatabaseException):
    """Report a uniqueness conflict while persisting an object."""

    pass


class TableNotFoundException(DatabaseException):
    """Report a reference to a missing database table."""

    pass


class ForeignKeyNotFoundException(DatabaseException):
    """Report a missing object referenced by a foreign key."""

    pass


class IncorrectColumnValueException(DatabaseException):
    """Report a value rejected by a database column constraint."""

    pass
