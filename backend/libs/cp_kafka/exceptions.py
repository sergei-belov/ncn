__all__ = ["KafkaSerializationError"]


class KafkaSerializationError(Exception):
    """Report failure to serialize or deserialize a Kafka message."""
