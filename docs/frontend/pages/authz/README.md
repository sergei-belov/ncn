# Authz frontend pages

These pages administer access records owned by the backend `authz` logical service. They reuse shared workspace/project shells but their primary data, permissions, mutations, errors, and recovery behavior are authorization concerns.

| Page | Route | Definition | Page structure |
| --- | --- | --- | --- |
| [Workspace access](workspace-access.md) | `/:workspaceSlug/settings/access` | Administer workspace roles for existing users. | Access heading/notices → search/actions → membership table or cards → pagination/dialogs |
| [Project access](project-access.md) | `/:workspaceSlug/projects/:projectId/settings/access` | Administer project roles and per-service restrictions. | Project settings header → page-local tabs → notices/search → membership table or cards → dialogs |

## Shared behavior

- Workspace management requires an `owner` or `admin` workspace role.
- Project management requires the project `admin` role.
- Membership mutations use optimistic entity versions and protect critical final-owner/final-admin invariants in the backend.
- `AccessManagementView` supplies desktop tables, mobile cards, search, cursor navigation, offline/read-only states, stale-data recovery, and permission-loss handling.

## Related documentation

- [All frontend services](../README.md)
- [Authz backend service](../../../backend/services/authz/README.md)
- [Components and UI](../../components.md)
