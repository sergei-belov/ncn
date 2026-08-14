# Not found

Route: `/:pathMatch(.*)*`

Shell: Standalone; outside `WorkspaceShell` and `ProjectLayout`.

## Purpose

The fallback page gives users a safe recovery path from an unknown URL.

## Behavior

- Show “Page not found” guidance in Russian.
- Link to `/{VITE_WORKSPACE_SLUG}/projects` for recovery.

## Page structure

- **Centered recovery panel**: compass icon, title, explanation, and project-catalog link.

## States and APIs

The page is static and makes no API requests. It is outside the workspace and project shells.

## Related documentation

- [Frontend page catalog](README.md)
