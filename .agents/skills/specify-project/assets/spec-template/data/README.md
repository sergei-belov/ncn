# Data Ownership Map

## Ownership Inventory

| Data/capability | System of record | Write owner | Consumers | Access contract | Projection/cache/search | Sensitivity |
|---|---|---|---|---|---|---|
| <!-- TEMPLATE: data --> | <!-- TEMPLATE: service/external --> | <!-- TEMPLATE: service --> | <!-- TEMPLATE: consumers --> | <!-- TEMPLATE: API/event link --> | <!-- TEMPLATE: derived state --> | <!-- TEMPLATE: class --> |

## Cross-Service Data Rules

<!-- TEMPLATE: Define owner-only writes, identifiers, tenancy, timestamps, consistency, event publication, retention, deletion, audit, and rebuildable projections. -->

Physical models and tables belong in each service's `data/` contract.
