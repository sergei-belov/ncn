# PMS logical service

PMS owns project-management behavior for projects, workflow states, cards, epics, agents, board reads, and personal board preferences. It runs inside the shared `ncn-pms` FastAPI process and uses authz identity and project membership to derive domain capabilities.

## Responsibilities

- create, update, archive, restore, list, and read projects;
- bootstrap project states, creator access, and the required coordinator;
- manage agent configuration and lifecycle;
- manage workflow-state creation, ordering, defaults, replacement, and deletion;
- create, edit, move, filter, and delete work items;
- create, edit, filter, relate, and delete epics;
- assemble column-oriented board snapshots and per-user preferences;
- enforce archive state, project scope, optimistic versions, rank allocation, rich-text sanitization, and domain invariants.

## Implementation map

| Layer | Main modules |
| --- | --- |
| Routers | `backend/api/router/projects.py`, `agents.py`, `states.py`, `work_items.py`, `board.py`, `epics.py` |
| Managers | `backend/api/managers/projects.py`, `agents.py`, `states.py`, `work_items.py`, `board.py`, `epics.py` |
| Repositories | `backend/api/db/projects.py`, `agents.py`, `states.py`, `work_items.py`, `board_preferences.py`, `epics.py` |
| Public models | `backend/models/pydantic/api/project_api.py`, `agent_api.py`, `state_api.py`, `work_item_api.py`, `board_api.py`, `epic_api.py` |
| Domain enums | `backend/models/enum/pms.py` |

## Data ownership

| Table | Role |
| --- | --- |
| [`pms_projects`](../../../database/tables/pms_projects.md) | Project root, counters, archive state, and concurrency versions |
| [`pms_agents`](../../../database/tables/pms_agents.md) | Coordinator and worker configuration |
| [`pms_states`](../../../database/tables/pms_states.md) | Ordered project workflow |
| [`pms_work_items`](../../../database/tables/pms_work_items.md) | Kanban cards |
| [`pms_work_item_assignees`](../../../database/tables/pms_work_item_assignees.md) | Card assignments |
| [`pms_epics`](../../../database/tables/pms_epics.md) | Planning epics |
| [`pms_epic_assignees`](../../../database/tables/pms_epic_assignees.md) | Epic assignments |
| [`pms_board_preferences`](../../../database/tables/pms_board_preferences.md) | Per-user board presentation state |

Project and workspace membership tables are authz-owned dependencies rather than PMS-owned data.

## Current boundary gaps

- The frontend HTTP board and epic adapters do not match the current FastAPI response models.
- Agent execution/session UI has no backend execution engine.
- Domain events are structured logs rather than durable messages or outbox rows.

## References

- [PMS API](api.md)
- [PMS flows](flows.md)
- [Shared API conventions](../../api.md)
- [Cross-service flows](../../flows.md)
- [Authz logical service](../authz/README.md)
