class DebeziumCDCCallbackHasNotObjModelAttribute(Exception):
    pass


class DebeziumCDCCallbackHasInvalidObjModelAttributeType(Exception):
    pass


class DebeziumCDCHandlerHasNotSpecifiedCallbackForOperation(Exception):
    pass


class DebeziumCDCCallbackHasInvalidRetryOptions(Exception):
    pass


class LinkedObjectDoesNotExist(Exception):
    pass
