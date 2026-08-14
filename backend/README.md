# NCN PMS Backend

FastAPI service for NCN project management: projects, board states, work items,
epics, and per-user board preferences.

The current cross-stack implementation and API inventory are documented in
[`../docs/README.md`](../docs/README.md). [`spec.md`](./spec.md) is retained as an
earlier PMS-focused snapshot. Backend-specific conventions are in
[`AGENTS.md`](./AGENTS.md).

## Development commands

Run commands from `backend/` through Poetry:

```text
poetry install
poetry run poe test
poetry run poe format
```

Database migration tasks use `.env.local`; application startup expects its
configuration in the process environment unless the launcher loads an env file.
