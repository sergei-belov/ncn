# General UI structure

The general UI layer defines the persistent frames around route pages. It is implemented by widgets rather than a separate layout framework.

## Shell hierarchy

```text
App.vue
├── RouterView
│   ├── WorkspaceShell
│   │   ├── Workspace navigation
│   │   └── RouterView
│   │       ├── Workspace page
│   │       └── ProjectLayout
│   │           ├── Project navigation
│   │           └── RouterView
│   │               ├── Project page
│   │               └── Settings page
│   └── NotFoundPage
└── Global toaster
```

## General components

| Component | Source | Role |
| --- | --- | --- |
| [Workspace navigation](navbar.md) | `frontend/src/widgets/app-shell/WorkspaceShell.vue` | Primary navigation layer and global session gate |
| [Project sidebar](project-sidebar.md) | `frontend/src/widgets/project-navigation/ProjectLayout.vue` | Secondary navigation layer for project routes |

## Responsive composition

| Viewport | Workspace navigation | Project navigation | Content |
| --- | --- | --- | --- |
| Below `md` | Compact top navbar | Compact sticky project header/navigation | Full-width page |
| `md` to below `lg` | Collapsible workspace sidebar | Compact sticky project header/navigation | Remaining width |
| `lg` and above | Collapsible workspace sidebar | Fixed project sidebar | Remaining width |

Detail routes may add a right-side sheet on desktop. No shared footer is implemented.

## Shared shell states

Before rendering protected routes, `WorkspaceShell` shows one of four session outcomes:

- access-check loading state;
- recoverable identity or authorization-service error with request code and retry;
- authenticated user with no workspace or project access;
- resolved session and the normal shell.

`ProjectLayout` then loads the current project. It shows project identity or a skeleton in navigation and replaces the child page with a project-load error when the project request fails.

## Related documentation

- [Frontend overview](../README.md)
- [Page catalog](../pages/README.md)
- [Components and UI](../components.md)
