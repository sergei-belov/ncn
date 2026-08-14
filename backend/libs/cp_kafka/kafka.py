import asyncio
import logging
from functools import wraps
from typing import (
    Awaitable,
    Callable,
    Coroutine,
    get_args,
)

import aiokafka
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
    avro,
)
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    SerializationError,
)
from pydantic import BaseModel

from libs.cp_common import BaseService
from libs.cp_kafka.base import Broker
from libs.cp_kafka.exceptions import KafkaSerializationError
from libs.cp_prometheus import PrometheusCollector


CallbackType = Callable[[BaseModel | list[BaseModel]], Awaitable[None]]


class KafkaBroker(BaseService, Broker):
    """Produce and consume Avro-serialized Kafka messages."""

    _serializers_cache: dict[str, avro.AvroSerializer] = {}
    _topics: list[str] = []
    _tasks: list[Coroutine] = []
    _collector: PrometheusCollector | None
    _deserializer: avro.AvroDeserializer
    _kafka_topic_prefix: str
    producer: aiokafka.AIOKafkaProducer | None
    consumer: aiokafka.AIOKafkaConsumer | None
    producer_configs: dict
    consumer_configs: dict
    retry_sleep: int

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        schema_registry_configuration: dict,
        kafka_topic_prefix: str = "",
        producer_configs: dict = None,
        consumer_configs: dict = None,
        retry_sleep: int = 5,
        collector: PrometheusCollector | None = None,
    ):
        """Initialize Kafka and schema-registry connection settings.

        Args:
            bootstrap_servers: Kafka bootstrap server addresses.
            group_id: Consumer group identifier.
            schema_registry_configuration: Confluent schema registry settings.
            kafka_topic_prefix: Optional prefix applied to every topic.
            producer_configs: Additional aiokafka producer options.
            consumer_configs: Additional aiokafka consumer options.
            retry_sleep: Delay before retrying a failed consumer loop.
            collector: Optional Prometheus collector for broker metrics.
        """
        super().__init__()
        self.schema_registry_client: SchemaRegistryClient = SchemaRegistryClient(conf=schema_registry_configuration)
        self.producer_configs = producer_configs or dict()
        self.consumer_configs = consumer_configs or dict()
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self.__class__._collector = collector
        self.__class__._deserializer = avro.AvroDeserializer(schema_registry_client=self.schema_registry_client)
        self.__class__._kafka_topic_prefix = kafka_topic_prefix
        self.__class__.producer = None
        self.__class__.consumer = None
        self.__class__.retry_sleep = retry_sleep

    @classmethod
    def listen(
        # fmt: off
        cls,
        topic: str,
        messages_count: int = 1,
        interval_period_sec: float = 1.0,
        delay: int = 0,
        # fmt: on
    ) -> Callable:
        """Decorator maker.

        Needed only to receive message processing arguments.

        Args:
            topic: Kafka topic name
            messages_count: buffer size for accumulating messages from Kafka
            interval_period_sec: number of seconds to fill the buffer
            delay: time to wait until processing starts

        Returns:
            Decorator object
        """

        def inner(function: CallbackType) -> CallbackType:
            """Decorator.

            Prepares a mapping of the topic name and the function to which the deserialized messages should be returned.

            Args:
                function: function to which the deserialized messages should be returned

            Returns:
                Wrapper above the function
            """

            @wraps(function)
            def wrapper(*args, **kwargs):
                """Forward deserialized messages to the registered callback."""

                return function(*args, **kwargs)

            first_arg_type = next(iter(wrapper.__annotations__.values()))
            is_multiple = len(get_args(first_arg_type)) > 0
            model = get_args(first_arg_type)[0] if is_multiple else first_arg_type
            topic_with_prefix = cls._with_added_kafka_topic_prefix(topic=topic)
            cls._topics.append(topic_with_prefix)
            cls._tasks.append(
                cls.capacitor(
                    topic=topic_with_prefix,
                    function=function,
                    model=model,
                    max_buffer_size=messages_count,
                    interval_period_sec=interval_period_sec,
                    is_multiple=is_multiple,
                    delay=delay,
                )
            )
            return wrapper

        return inner

    @classmethod
    def prepare_obj(cls, src_object: aiokafka.structs.ConsumerRecord, target_model: BaseModel) -> BaseModel | None:
        """Deserializes object to decorated function argument.

        Args:
            src_object: Kafka message to deserialize
            target_model: decorated function argument to which to deserialize

        Returns:
            Deserialized object
        """
        try:
            deserialized_obj: object = cls._deserializer(
                data=src_object.value,
                ctx=SerializationContext(src_object.topic, MessageField.VALUE),
            )
        except SerializationError:
            error_message = f"Deserialization error with {src_object=}"
            logging.exception(error_message)
            raise KafkaSerializationError(error_message)

        if deserialized_obj:
            return target_model.model_validate(deserialized_obj)
        else:
            return None

    async def start(self):
        """Schedule broker startup without blocking the caller."""

        asyncio.create_task(self._start())

    async def _start(self):
        """Starts process of multiple writing Kafka messages to asynchronous queues."""

        self.__class__.producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            **self.producer_configs,
        )
        await self.__class__.producer.start()

        if not self._topics:
            return

        topic_regex = "|".join(self._topics)

        consumer = aiokafka.AIOKafkaConsumer(
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            retry_backoff_ms=1000,
            **self.consumer_configs,
        )
        consumer.subscribe(pattern=topic_regex)

        self.__class__.consumer = consumer
        await self.__class__.consumer.start()

        try:
            await asyncio.gather(*self._tasks)
        except aiokafka.errors.ConsumerStoppedError:
            pass
        finally:
            logging.info("Stopping consumer")
            if self.consumer:
                await self.consumer.stop()

    async def stop(self):
        """Stop active Kafka consumer and producer connections."""

        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()

    async def ping(self) -> bool:
        """Return whether the producer can fetch cluster metadata."""

        try:
            await self.producer.client.fetch_all_metadata()
            return True
        except Exception:
            self.logger.exception("Failed when try to check kafka health")
            return False

    @classmethod
    async def capacitor(  # pylint: disable=too-many-arguments
        cls,
        topic: str,
        function: CallbackType,
        model: BaseModel,
        max_buffer_size: int,
        interval_period_sec: float,
        is_multiple: bool,
        delay: int,
    ):
        """Reads Kafka messages and gives them to decorated functions.

        Args:
            topic: Kafka topic name
            function: function to which the deserialized messages should be returned
            model: decorated function argument to which to deserialize
            max_buffer_size: buffer size for accumulating messages from Kafka
            interval_period_sec: number of seconds to fill the buffer
            is_multiple: flag, that indicates type of function arguments
            delay: time to wait until processing starts
        """
        while True:
            if delay:
                await asyncio.sleep(delay)

            while True:

                topic_offsets: dict[aiokafka.TopicPartition, int] = {}

                partitions = [partition for partition in cls.consumer.assignment() if partition.topic == topic]

                if not partitions:
                    await asyncio.sleep(1)
                    continue

                try:
                    consumer_messages = await cls.consumer.getmany(
                        *partitions, timeout_ms=int(interval_period_sec * 1000), max_records=max_buffer_size
                    )
                    prepared_objs = []

                    for topic_partition, messages in consumer_messages.items():

                        try:
                            for message in messages:
                                prepared_obj: BaseModel = cls.prepare_obj(
                                    src_object=message,
                                    target_model=model,
                                )
                                if prepared_obj:
                                    prepared_objs.append(prepared_obj)
                            topic_offsets[topic_partition] = messages[-1].offset + 1

                        except KafkaSerializationError as deserialization_error:
                            logging.exception(deserialization_error)
                            if cls._collector:
                                cls._collector.increment_consumer_error(topic=topic)
                            raise
                    if cls._collector:
                        cls._collector.increment_consumer_total(topic=topic, count=len(prepared_objs))

                    if prepared_objs:
                        if is_multiple:
                            await function(prepared_objs)
                        else:
                            await function(prepared_objs[0])

                    if topic_offsets:
                        await cls.consumer.commit(topic_offsets)  # type: ignore[reportOptionalMemberAccess,union-attr]

                    prepared_objs.clear()
                except asyncio.exceptions.CancelledError:
                    break
                except Exception as exception:
                    if cls._collector:
                        cls._collector.increment_consumer_processing_error(topic=topic)
                    logging.error(f"Error in message processing for topic: {topic}")
                    logging.exception(exception)
                    break

            await asyncio.sleep(cls.retry_sleep)

    async def produce(self, topic: str, message: BaseModel, key: str | None = None):
        """
        Produce message to topic

        Args:
            topic: kafka topic
            key: topic key
            message: bytes serializable value
        """
        if not self.producer:
            raise ConnectionError("Producer not initialized")

        topic = self._with_added_kafka_topic_prefix(topic=topic)
        serializer = self._get_serializer(topic=topic)

        try:
            serialized_message = serializer(message.model_dump(), SerializationContext(topic, MessageField.VALUE))
        except TypeError as type_error:
            error_message: str = f"Incorrect schema: {serializer._parsed_schema=}, {topic=}, {message=}"
            logging.error(error_message)
            raise KafkaSerializationError(error_message) from type_error

        await self.producer.send(
            topic=topic,
            value=serialized_message,
            key=key,
        )

    def _get_serializer(
        self,
        topic: str,
    ) -> avro.AvroSerializer:
        """
        Gets the latest version schema

        Args:
            topic: kafka topic

        Returns:
            Latest version serializer
        """
        if topic not in self._serializers_cache:
            schema = self.schema_registry_client.get_latest_version(topic).schema
            serializer = avro.AvroSerializer(
                schema_registry_client=self.schema_registry_client,
                schema_str=schema,
            )
            self.__class__._serializers_cache[topic] = serializer  # pylint: disable=protected-access
        else:
            serializer = self._serializers_cache[topic]

        return serializer

    @classmethod
    def _with_added_kafka_topic_prefix(cls, topic: str) -> str:
        """Return a topic name with the configured prefix applied once."""

        kafka_topic_prefix = f"{cls._kafka_topic_prefix}."
        return f"{kafka_topic_prefix}{topic}" if not topic.startswith(kafka_topic_prefix) else topic
