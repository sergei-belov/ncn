import asyncio

from api.settings import get_settings
from migrations.kafka.kafka_schema_registry import KafkaSchemaRegistryClient
from models.pydantic import schema


settings = get_settings()


async def migrate() -> None:
    """Synchronize configured Kafka topics and schemas."""

    kafka_schema_registry = KafkaSchemaRegistryClient(
        schema_registry_url=settings.KAFKA_SCHEMA_REGISTRY_URL,
        schema_registry_type="AVRO",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        schema_registry_model_modules=[schema],
    )
    await kafka_schema_registry.register_all()



if __name__ == "__main__":
    asyncio.run(migrate())
