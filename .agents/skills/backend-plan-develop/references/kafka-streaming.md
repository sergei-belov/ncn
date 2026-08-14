# Kafka Streaming Reference

Use this when adding or changing stream models, Kafka listeners, or Kafka producers in backend services.

This reference embeds the stream model, listener, manager, producer, and wiring patterns needed for Kafka work.

## Stream Models

Define Kafka payloads as Pydantic models and put the topic name on `Meta.topic`.

```python
class ExternalTagUnitsStream(OrmModel):
    units: str
    source_id: UUID
    tag_name: str

    class Meta:
        topic = "external.fct.tag-units.0"
```

Export new stream models from `backend/models/pydantic/stream/__init__.py` and the top-level `backend/models/pydantic/__init__.py` if neighboring code does so.

## Listeners

Keep listener modules under `backend/api/stream/`. The application imports `api.stream` in `backend/api/main.py`, and `backend/api/stream/__init__.py` imports concrete stream modules so decorators run at startup.

```python
@Services.broker.listen(topic=pydantic.ExternalTagUnitsStream.Meta.topic, messages_count=200)
async def check_pi_tags_units(update_data: list[pydantic.ExternalTagUnitsStream]) -> None:
    logger.info("Received PI tag units stream batch: count={}", len(update_data))
    await Managers.pi_units.sync_pi_unit(data=update_data)
```

Listener rules:

- annotate the function argument with the exact stream model type
- use `list[Model]` when batching with `messages_count > 1`
- keep listeners thin: log receipt and delegate to a manager
- use the same broker hub as neighboring code, usually `Services.broker`
- import the module from `backend/api/stream/__init__.py`

The broker decorator introspects the first argument annotation to choose the deserialization model and whether the callback receives one model or a list.

## Producers

Produce Kafka messages from managers or services after business decisions are made.

```python
await Services.broker.produce(
    topic=pydantic.UpdateBaseTagAnnotationStream.Meta.topic,
    message=pydantic.UpdateBaseTagAnnotationStream(
        base_tag_id=base_tag_id,
        annotation={settings.APP_PI_DIMENSION_ANNOTATION: unit},
    ),
)
```

For event messages, build the full stream DTO before producing:

```python
event = pydantic.DatalakeEventStream(
    id=uuid4(),
    name=settings.APP_PI_DIMENSION_CHANGED_EVENT_NAME,
    priority=enum.EventPriority.LOW,
    start=int(datetime.now().timestamp()) * 1000,
    project_id=project_id,
    description="\n".join(descriptions),
    tags=tags,
)
await Services.broker.produce(topic=pydantic.DatalakeEventStream.Meta.topic, message=event)
```

Producer rules:

- use `Model.Meta.topic` rather than duplicating topic strings at call sites
- pass a Pydantic model instance as `message`
- produce multiple messages in a loop when needed, then flush once after the batch
- call `await Services.broker.producer.flush()` after a batch when downstream work depends on the messages being sent
- guard empty input batches before doing database work or producing messages
- keep DB reads/writes inside `async with Services.database.session()` and keep cross-repository orchestration in the manager

## Manager Orchestration Example

Use a manager for batching, database reads, decision-making, production, and flush behavior.

```python
class PiUnitsManager(BaseManager):
    @classmethod
    async def sync_pi_unit(cls, data: list[pydantic.ExternalTagUnitsStream]) -> None:
        if not data:
            return

        units_by_external_tag = {(unit.source_id, unit.tag_name): unit.units for unit in data}
        changed_by_project: dict[UUID, list[tuple[pydantic.BaseTagDTO, str, str]]] = defaultdict(list)

        async with Services.database.session() as session:
            base_tag_matches = await Database.base_tags.get_by_external_tags(
                external_tags=list(units_by_external_tag.keys()),
                session=session,
            )

            for match in base_tag_matches:
                base_tag = match.base_tag
                new_unit = units_by_external_tag[(match.source_id, match.tag_name)]
                previous_unit = cls._get_annotation_value(base_tag=base_tag, key=settings.APP_PI_DIMENSION_ANNOTATION)

                await Services.broker.produce(
                    topic=pydantic.UpdateBaseTagAnnotationStream.Meta.topic,
                    message=pydantic.UpdateBaseTagAnnotationStream(
                        base_tag_id=base_tag.id,
                        annotation={settings.APP_PI_DIMENSION_ANNOTATION: new_unit},
                    ),
                )

                if previous_unit is not None and previous_unit != new_unit:
                    changed_by_project[base_tag.project_id].append((base_tag, previous_unit, new_unit))

        for project_id, changes in changed_by_project.items():
            await cls._send_dimension_changed_event(project_id=project_id, changes=changes)

        await Services.broker.producer.flush()
```

## Wiring Checklist

- Add stream payload classes in `backend/models/pydantic/stream/`
- Export them from stream and top-level Pydantic import hubs
- Add listener modules under `backend/api/stream/`
- Import listener modules from `backend/api/stream/__init__.py`
- Ensure `backend/api/main.py` imports `api.stream` using the existing local pattern
- Put production logic in managers and flush once per produced batch
