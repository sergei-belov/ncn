from enum import StrEnum


class DebeziumCDCType(StrEnum):
    CREATE: str = "c"
    READ: str = "r"
    UPDATE: str = "u"
    DELETE: str = "d"
