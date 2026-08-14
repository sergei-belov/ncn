import prometheus_client
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from libs.cp_common import BaseService
from libs.cp_prometheus.models import CollectorConsumerType


__all__ = ["PrometheusCollector"]


class PrometheusCollector(BaseService):
    """Collect in-process application and Kafka consumer metrics."""

    consumer_objects: prometheus_client.Counter  # Metrics for objects created in the database
    authorization_operations: prometheus_client.Counter

    def __init__(self):
        """Initialize labeled counters for consumer outcomes."""

        self.consumer_objects = prometheus_client.Counter(
            "consumer_objects",
            "Consumer processing results",
            labelnames=["type"],
        )
        self.authorization_operations = prometheus_client.Counter(
            "authorization_operations",
            "Authorization decisions and access mutations",
            labelnames=["operation", "result", "reason"],
        )
        super().__init__()

    def record_authorization(self, operation: str, result: str, reason: str) -> None:
        """Increment a bounded authorization operation metric.

        Args:
            operation: Stable operation family.
            result: Stable success, denial, or error outcome.
            reason: Stable machine-readable result reason.
        """

        self.authorization_operations.labels(
            operation=operation,
            result=result,
            reason=reason,
        ).inc()

    def increment_consumer_total(self, topic: str, count: int = 1) -> None:
        """Increment the number of messages consumed from a topic."""

        label = f"{topic}.{CollectorConsumerType.TOTAL}"
        self.consumer_objects.labels(label).inc(count)

    def increment_consumer_error(self, topic: str) -> None:
        """Increment the deserialization failure count for a topic."""

        label = f"{topic}.{CollectorConsumerType.DESERIALIZATION_ERROR}"
        self.consumer_objects.labels(label).inc()

    def increment_consumer_processing_error(self, topic: str) -> None:
        """Increment the processing failure count for a topic."""

        label = f"{topic}.{CollectorConsumerType.PROCESSING_ERROR}"
        self.consumer_objects.labels(label).inc()

    async def start(self) -> None:
        """Start the in-process collector, which requires no external work."""

        pass

    async def stop(self) -> None:
        """Stop the in-process collector, which owns no external resources."""

        pass

    async def ping(self) -> bool:
        """The in-process collector is healthy once it is constructed."""
        return True

    @staticmethod
    def add_instrumentator_to_app(app: FastAPI):
        """Instrument a FastAPI application and expose its metrics endpoint."""

        Instrumentator().instrument(app).expose(app)

    @staticmethod
    def generate() -> bytes:
        """Generate the current Prometheus exposition payload."""

        return prometheus_client.generate_latest()
