from enum import StrEnum


class KafkaTopicPolicy(StrEnum):
    DELETE: str = "delete"
    COMPACT: str = "compact"
    MULTI: str = "delete,compact"
