# Documentation Structure and State

Use this guide for a current-state audit, a new documentation set, or any change that adds, removes, moves, or regroups documents.

## Match Claims to Evidence

Use the narrowest accurate state language.

| State | Required evidence | Safe wording |
| --- | --- | --- |
| Requested or decided | User requirement or accepted decision | “will”, “must”, “is intended to” |
| Declared contract | Accepted specification, schema, or generated contract | “the contract defines” |
| Implemented | Current source exists and is registered or reachable through the relevant entry point | “the implementation provides” |
| Configured or defaulted | Current configuration and selection logic | “is configured”, “defaults to” |
| Verified runnable | The relevant command or scenario completed in the stated environment | “verified by”, with the command or scope |
| Integrated end to end | Both sides are compatible or an end-to-end check passed | “works end to end” |
| Deployed or operational | Deployment or live-runtime evidence | “is deployed”, “is operational” |
| Gap or conflict | Missing evidence or authoritative sources disagree | “is not verified”, “differs”, “is a gap” |

- Treat the current working tree, including relevant untracked files, as the implementation state unless the user selects a commit or release.
- Do not describe uncommitted code as released or deployed.
- Do not infer a cross-boundary state from one side. Compare client and server contracts, ORM declarations and migrations/runtime schema, producers and consumers, or configured middleware and emitted behavior.
- Trace activation before promoting a source-visible difference to an active gap: mode selection, defaults, call sites, feature flags, route registration, proxy or origin topology, and conditional request options. State unverified preconditions explicitly.
- Treat transport claims with special care. For example, a CORS allow-list matters only for a cross-origin browser path, and a conditional header matters only where a caller supplies it.
- Scope negative claims to the inspected evidence. Prefer “no checked-in migration defines this table” over “the database has no table.”
- Trace wiring as well as definitions before claiming a route, handler, component, or service is implemented.
- Use tests as supporting evidence. A test name or fixture alone does not prove the tested path passed; run it before saying it passed.
- Add an evidence scope or verification date to a broad audit only when it helps readers understand freshness. A date does not replace evidence.

## Design the Documentation Map

Preserve an established project structure. Do not reorganize it merely because another valid taxonomy exists. When no adequate structure exists or the user requests a restructure, organize from broad ownership to specific artifacts:

```text
documentation root
├── README.md                 # scope, status, and map
├── shared or cross-cutting   # architecture, runtime, shared UI, relationships
└── owned area
    ├── README.md             # complete local inventory
    ├── contract or flow docs
    └── leaf documents
```

- Choose the primary grouping axis from stable product ownership: product area, service, bounded domain, or subsystem. Do not group only by file type when readers navigate by owner or capability.
- Put cross-cutting material at the nearest common parent. Link to it from owned documents instead of copying it.
- Give each folder README a clear scope and a complete inventory of its direct areas or documents.
- Keep one canonical home for each fact. Let indexes summarize and link; let leaf documents own detail.
- Give shared shells, navigation, or workflows one canonical shared home when several pages depend on them. Use a dedicated document only when the material is substantial; otherwise keep it in the established shared overview or component inventory.
- Group a cross-domain page with the service or domain that owns its primary behavior, then cross-link it from other relevant route or feature indexes.
- Split service material into overview, API, and flows only when each document has substantive, distinct content.
- For a database reference, keep a table inventory and cross-table relationships or provisioning status above per-table schema documents.
- Do not create empty directories, placeholder sections, or parallel taxonomies solely for symmetry.
- Add or move a document only when the requested scope does not fit its current canonical owner without conflating distinct subjects.

## Apply Structural Changes Safely

1. Write the intended path and ownership map before moving files.
2. Distinguish moves from deletions and preserve file history when practical.
3. Update root maps, local indexes, inbound links, outbound links, and source references in the same change.
4. Search for old paths, filenames, titles, routes, and anchors after the move.
5. Validate the entire documentation root when paths or shared anchors change; validating only edited files cannot detect every stale inbound link.
6. Inspect staged and unstaged diffs separately so a reorganization does not discard pre-existing work.
