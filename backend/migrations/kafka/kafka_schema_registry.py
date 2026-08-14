import asyncio
import functools
import inspect
from types import ModuleType
from typing import Type

import py_avro_schema as pas
from confluent_kafka.admin import (
    AdminClient,
    ClusterMetadata,
    NewPartitions,
    NewTopic,
    TopicMetadata,
)
from confluent_kafka.schema_registry import (
    Schema,
    SchemaRegistryClient,
    SchemaRegistryError,
)
from loguru import logger

from models.enum import TopicType
from models.exceptions import (
    CompatibilityError,
    ValidationError,
)
from models.pydantic.schema.base import Model


class ModelCollector:
    """Discover schema-producing broker models in a Python module."""

    def __init__(self, package: ModuleType):
        """Collect and validate broker models exported by a package.

        Args:
            package: Module whose concrete schema models are inspected.
        """
        self.namespace = package.__name__
        self.models = [
            member[1]
            for member in inspect.getmembers(package)
            if inspect.isclass(member[1])
               and issubclass(member[1], Model)
               and member[1] is not Model
               and member[1].create_schema()
        ]

        self.validate_fields(self.models)

    @classmethod
    def validate_fields(cls, models: list[Type[Model]]) -> None:
        """Validate topic shape and type for collected schema models.

        Args:
            models: Broker models to validate.

        Raises:
            ValidationError: If a topic does not contain four name segments.
            ValueError: If a topic type segment is unknown.
        """
        for model in models:
            topic_part = model.Meta.topic.split(".")
            if len(topic_part) != 4:
                raise ValidationError(model)
            TopicType(topic_part[1])


class KafkaSchemaRegistryClient:
    """Synchronize broker topics, partitions, and Avro schemas."""

    _schema_registry_client: SchemaRegistryClient
    _schema_registry_type: str
    _admin_client: AdminClient
    _schema_registry_model_modules: list[ModuleType] | None

    def __init__(
        self,
        schema_registry_url: str,
        schema_registry_type: str,
        bootstrap_servers: str,
        schema_registry_model_modules: list[ModuleType] | None = None,
    ):
        """Initialize schema registry and Kafka administration clients.

        Args:
            schema_registry_url: Schema registry endpoint.
            schema_registry_type: Schema type submitted to the registry.
            bootstrap_servers: Kafka bootstrap server addresses.
            schema_registry_model_modules: Optional modules containing broker
                schema models.
        """
        self._schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
        self._schema_registry_type = schema_registry_type
        self._admin_client = AdminClient({"bootstrap.servers": bootstrap_servers})
        self._schema_registry_model_modules = schema_registry_model_modules

    async def register_all(self) -> None:
        """Collect and register schemas from every configured model module."""

        if self._schema_registry_model_modules:
            for module in self._schema_registry_model_modules:
                collector = ModelCollector(module)
                await self.register(*collector.models, namespace=collector.namespace)
        return None

    async def register(self, *models: Type[Model], namespace: str | None = None) -> None:
        """Register models without blocking the active event loop.

        Args:
            *models: Broker schema models to synchronize.
            namespace: Optional namespace displayed in migration logs.
        """
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            executor=None,
            func=functools.partial(self._register, *models, namespace=namespace),
        )
        return None

    def _register(self, *models: Type[Model], namespace: str | None = None) -> None:  # noqa C901
        """Synchronize topics, partition counts, and schemas for models.

        Args:
            *models: Broker schema models to synchronize.
            namespace: Optional namespace displayed in migration logs.
        """
        schemas_to_register: list[tuple] = list()
        new_partitions: list[NewPartitions] = list()
        topics_to_create: list[NewTopic] = list()

        metadata: ClusterMetadata = self._admin_client.list_topics()

        # Проверка совместимости всех схем, которые есть в регистри
        if namespace:
            logger.info(f"##################       Registering {namespace:18} ##################")

        for m in models:
            topic = m.topic()
            current_partitions: int = m.Meta.partitions
            config: dict = m.config()

            try:
                current_avro_schema_str: str = pas.generate(py_type=m, options=pas.Option.NO_AUTO_NAMESPACE).decode()
            except TypeError:
                logger.error(f"Bad parameters typing for model {m}.")
                raise TypeError


            (
                create_topic,
                schema,
                partitions,
            ) = self._register_topic(
                topic=topic,
                metadata=metadata,
                current_avro_schema_str=current_avro_schema_str,
                config=config,
                current_partitions=current_partitions,
            )
            if create_topic:
                topics_to_create.append(create_topic)
            if schema:
                schemas_to_register.append(schema)
            if partitions:
                new_partitions.append(partitions)

        # Создание новых топиков
        if topics_to_create:
            self._admin_client.create_topics(new_topics=topics_to_create)
            for topic in topics_to_create:
                logger.info(f"Topic '{topic.topic}' is created.")

        # Создание новых партиций
        if new_partitions:
            self._admin_client.create_partitions(new_partitions=new_partitions)
            for partition in new_partitions:
                logger.info(
                    f"Number of partitions is increased to {partition.new_total_count} for topic '{partition.topic}'."
                )

        # Регистрация схем после создания топиков
        for topic_name, schema in schemas_to_register:
            schema_id: int = self._schema_registry_client.register_schema(subject_name=topic_name, schema=schema)
            logger.info(f"New schema is registered under topic '{topic_name}', schema_id: {schema_id}.")
            logger.debug(f"Registered schema: {schema}.")

    def _register_topic(
        self,
        topic: str,
        metadata: ClusterMetadata,
        current_avro_schema_str: str,
        config: dict,
        current_partitions: int,
    ) -> tuple[NewTopic | None, tuple | None, NewPartitions | None]:
        """Determine topic, schema, and partition changes for one model.

        Args:
            topic: Kafka topic name.
            metadata: Current Kafka cluster metadata.
            current_avro_schema_str: Generated Avro schema text.
            config: Desired Kafka topic configuration.
            current_partitions: Desired topic partition count.

        Returns:
            Optional topic creation, schema registration, and partition
            expansion operations.

        Raises:
            CompatibilityError: If the generated schema is incompatible.
            ValueError: If the requested partition count would decrease.
        """
        create_topic = None
        register_schema = None
        new_partitions = None

        current_avro_schema: Schema = Schema(
            schema_str=current_avro_schema_str,
            schema_type=self._schema_registry_type,
        )

        # Проверка совместимости новой схемы со старым именем топика. Если имя топика новое, то True.
        # Прекращаем миграцию в случае ошибки:
        is_compatible: bool = self._schema_registry_client.test_compatibility(
            subject_name=topic, schema=current_avro_schema
        )
        if not is_compatible:
            logger.error(
                f"Model schema for topic {topic} is not compatible. "
                "Change schema version or change parameters to optional."
            )
            raise CompatibilityError(topic, current_avro_schema_str)

        current_topic: TopicMetadata | None = metadata.topics.get(topic)
        if not current_topic:
            # Добавление топика в список
            logger.info(f"Topic '{topic}' doesn't exist.")
            create_topic = NewTopic(
                topic,
                num_partitions=current_partitions,
                config=config,
            )
        else:
            old_partitions = len(current_topic.partitions)

            if current_partitions < old_partitions:
                logger.error(
                    f"Cannot decrease the number of partitions for '{topic}'. "
                    f"Please change it to be more or equal to {old_partitions}."
                )
                raise ValueError
            elif current_partitions > old_partitions:
                logger.info(f"Topic '{topic}' has different partition number.")
                new_partitions = NewPartitions(topic=topic, new_total_count=current_partitions)
            elif current_partitions == old_partitions:
                logger.info(f"Topic '{topic}' already exists.")

        # Поиск в регистри схемы на наличие новой схемы.
        try:
            avro_schema_str: str | None = self._schema_registry_client.lookup_schema(
                topic, current_avro_schema
            ).schema.schema_str
            logger.info(f"Current schema for topic '{topic}' is already registered.")
            logger.debug(f"Current schema: {avro_schema_str}.")
        except SchemaRegistryError:
            logger.info(f"Current schema for topic '{topic}' is not registered.")
            register_schema = (topic, current_avro_schema)

        return create_topic, register_schema, new_partitions
