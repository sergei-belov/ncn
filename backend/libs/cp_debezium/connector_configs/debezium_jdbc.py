from copy import deepcopy

from libs.cp_debezium.connector_configs.base import DebeziumBaseConnectorConfig


class DebeziumJdbcConnectorConfig(DebeziumBaseConnectorConfig):
    tables: list[str]
    exclude_fields: list[str] | None = None

    _default_config = {
        "connector.class": "io.debezium.connector.jdbc.JdbcSinkConnector",
        "tasks.max": "1",
        "primary.key.fields": "id",
        "primary.key.mode": "record_key",
        "insert.mode": "upsert",
        "delete.enabled": "true",
        "errors.tolerance": "all",
        "errors.log.enable": "true",
        "transforms": "unwrap,ReplaceField",
        "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
        "transforms.unwrap.drop.tombstones": "false",
        "transforms.unwrap.delete.handling.mode": "none",
        "transforms.ReplaceField.type": "org.apache.kafka.connect.transforms.ReplaceField$Value",
        "transforms.ReplaceField.exclude": "",
    }

    @classmethod
    def to_json(cls) -> dict[str, str | dict[str, str]]:
        config = deepcopy(cls._default_config)
        config.update(cls.config)
        cls._set_database_properties(config)
        cls._set_topic_properties(config)
        cls.set_properties(config)
        return {
            "name": f"{cls.microservice_name}.import.{cls.connector_name}.{cls.connector_version}",
            "config": config,
        }

    @classmethod
    def _set_database_properties(cls, config: dict[str, str]) -> None:
        config[
            "connection.url"
        ] = f"jdbc:postgresql://{cls.db_hostname}:{cls.db_port}/{cls.db_dbname}?currentSchema={cls.db_schema}"
        config["connection.username"] = cls.db_user
        config["connection.password"] = cls.db_password
        transforms = config.get("transforms") or ""
        route = "route" if len(transforms) == 0 else ",route"
        config["transforms"] = transforms + route
        config["transforms.route.type"] = "org.apache.kafka.connect.transforms.RegexRouter"
        config["transforms.route.replacement"] = "$4"
        if cls.exclude_fields:
            config["transforms.ReplaceField.exclude"] = ",".join(cls.exclude_fields)

    @classmethod
    def _set_topic_properties(cls, config: dict[str, str]) -> None:
        config["topics"] = ",".join(
            f"{cls.kafka_topic_prefix}.debezium.cdc.{table}.{cls.connector_version}" for table in cls.tables
        )
        config["topic.creation.enable"] = "false"
        config["transforms.route.regex"] = "([^.]+)\\.([^.]+)\\.([^.]+)\\.([^.]+)\\.([^.]+)"
