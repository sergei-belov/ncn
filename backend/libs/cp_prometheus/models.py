from enum import StrEnum


__all__ = ["CollectorConsumerType"]


class CollectorConsumerType(StrEnum):
    """Outcome labels recorded for Kafka consumer processing."""

    TOTAL = "total"
    DESERIALIZATION_ERROR = "deserialization_error"
    PROCESSING_ERROR = "processing_error"
