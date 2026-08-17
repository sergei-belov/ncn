from copy import deepcopy

from libs.cp_debezium.connector_configs.base import DebeziumBaseConnectorConfig
from libs.cp_debezium.models.enum import KafkaTopicPolicy


class DebeziumPostgresConnectorConfig(DebeziumBaseConnectorConfig):
    _default_config = {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "plugin.name": "pgoutput",
        "publication.autocreate.mode": "filtered",
        "errors.max.retries": "-1",
        "retriable.restart.connector.wait.ms": "30000",
        "slot.max.retries": "60",
        "slot.retry.delay.ms": "60000",
        "database.query.timeout.ms": "0",
        "heartbeat.interval.ms": "10000",
        "topic.creation.default.replication.factor": -1,
        "topic.creation.default.partitions": 1,
        "topic.creation.default.compression.type": "lz4",
        "snapshot.mode": "when_needed",
    }
    _properties_with_db_schema = [
        "table.include.list",
        "table.exclude.list",
        "column.include.list",
        "column.exclude.list",
    ]

    cleanup_policy: KafkaTopicPolicy = KafkaTopicPolicy.COMPACT
    heartbeat_table: str = ""

    @classmethod
    def to_json(cls) -> dict[str, str | dict[str, str]]:
        config = deepcopy(cls._default_config)
        config.update(cls.config)
        cls._set_database_properties(config)
        cls._set_topic_properties(config)
        cls._add_schema_to_properties(config)
        cls.set_properties(config)
        return {
            "name": f"{cls.microservice_name}.export.{cls.connector_name}.{cls.connector_version}",
            "config": config,
        }

    @classmethod
    def _set_database_properties(cls, config: dict[str, str]) -> None:
        config["database.server.name"] = cls.microservice_name
        config["database.hostname"] = cls.db_hostname
        config["database.port"] = str(cls.db_port)
        config["database.user"] = cls.db_user
        config["database.password"] = cls.db_password
        config["database.dbname"] = cls.db_dbname
        config["slot.name"] = f"export__{cls.connector_name}__{cls.connector_version}"
        config["publication.name"] = config["slot.name"] + "__publication"
        if cls.heartbeat_table:
            config["heartbeat.action.query"] = (
                f"INSERT INTO {cls.db_schema}.{cls.heartbeat_table} (id, heartbeat_ts) "
                "VALUES (1, NOW()) "
                "ON CONFLICT(id) "
                "DO UPDATE SET heartbeat_ts=EXCLUDED.heartbeat_ts;"
            )

    @classmethod
    def _set_topic_properties(cls, config: dict[str, str]) -> None:
        config["topic.prefix"] = cls.kafka_topic_prefix
        transforms = config.get("transforms") or ""
        add_prefix = "AddPrefix" if len(transforms) == 0 else ",AddPrefix"
        config["transforms"] = transforms + add_prefix
        config["transforms.AddPrefix.type"] = "org.apache.kafka.connect.transforms.RegexRouter"
        config["transforms.AddPrefix.regex"] = f"(.*).{cls.db_schema}.(.*)"
        config["transforms.AddPrefix.replacement"] = f"$1.debezium.cdc.$2.{cls.connector_version}"
        config["topic.creation.default.cleanup.policy"] = cls.cleanup_policy.value
        config["topic.creation.default.min.insync.replicas"] = cls.kafka_min_insync_replicas

    @classmethod
    def _add_schema_to_properties(cls, config: dict[str, str]) -> None:
        for prop in cls._properties_with_db_schema:
            enumeration = config.get(prop) or ""
            if len(enumeration) > 0:
                config[prop] = cls.__add_schema_to_enumeration(enumeration)
        if cls.heartbeat_table:
            config["table.include.list"] = config["table.include.list"] + f",{cls.db_schema}.{cls.heartbeat_table}"
            if "column.include.list" in config:
                debezium_columns = (
                    f"{cls.db_schema}.{cls.heartbeat_table}.id,{cls.db_schema}.{cls.heartbeat_table}.heartbeat_ts"
                )
                config["column.include.list"] = config["column.include.list"] + f",{debezium_columns}"

    @classmethod
    def __add_schema_to_enumeration(cls, enumeration: str | list[str]) -> str:
        schema = f"{cls.db_schema}."
        if isinstance(enumeration, str):
            enumeration = enumeration.replace(" ", "").split(",")
        return ",".join(i if i.startswith(schema) else schema + i for i in enumeration)
