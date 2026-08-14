class MultipleGetParamsException(Exception):
    """Report mutually exclusive parameter strategies supplied together."""

    pass


class NotEnoughParamsException(Exception):
    """Report insufficient parameters to resolve a storage key."""

    pass


class OrmNotInitializedException(Exception):
    """Report an ORM operation attempted before storage initialization."""

    pass
