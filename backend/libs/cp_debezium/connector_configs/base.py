from abc import abstractmethod


class DebeziumBaseConnectorConfig:
    microservice_name: str = "microservice-template"
    connector_name: str = "examples"
    connector_version: int = 0

    db_schema: str = "public"
    db_hostname: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_dbname: str = "postgres"

    kafka_topic_prefix: str = "dev"
    kafka_min_insync_replicas: int = 1

    config: dict[str, str] = {}
    _default_config: dict[str, str] = {}

    @classmethod
    @abstractmethod
    def to_json(cls) -> dict[str, str | dict[str, str]]:
        raise NotImplementedError()

    @classmethod
    def set_properties(cls, config: dict[str, str]) -> None:
        pass

    @classmethod
    @abstractmethod
    def _set_database_properties(cls, config: dict[str, str]) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def _set_topic_properties(cls, config: dict[str, str]) -> None:
        raise NotImplementedError()
