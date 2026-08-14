# Project sidebar — secondary navigation

Component: `ProjectLayout`

Source: `frontend/src/widgets/project-navigation/ProjectLayout.vue`

## Purpose

The project sidebar is the secondary navigation layer inside the primary `WorkspaceShell` navigation. It loads and identifies the routed project, groups project destinations, and provides the content outlet for all project pages.

## Desktop structure

- **Back link**: returns to the workspace project catalog.
- **Project identity**: color tile, project name, identifier, or Archived badge.
- **Agent group**: Assistants and Sessions.
- **Management group**: Board, Epics, and conditional Settings.
- **Content outlet**: the selected project page.

At `lg` and above, the sidebar is sticky, full viewport height, and uses `w-52` (13 rem). It appears beside the workspace sidebar, creating two persistent desktop navigation columns.

## Compact structure

Below `lg`, project navigation becomes a sticky header above page content. The first row contains a back button, project color tile, and truncated project name. Grouped Agent and Management links render in compact rows below it.

## Visibility and state

- Settings is included only when the loaded project exposes `permissions.canEditProject`.
- Assistants, Sessions, Board, and Epics remain visible to project members.
- Archived projects display an Archived badge in the desktop identity block.
- While the project loads, desktop identity uses a skeleton and the compact header uses the fallback label “Проект”.
- A project-query error replaces the active child page with an error message.

## Accessibility

Both desktop and compact navigation expose the label “Project sections”. The back control has a specific accessible label in compact mode, and active route styling identifies the selected section.

## Related documentation

- [General UI structure](README.md)
- [Workspace navbar](navbar.md)
- [`SettingsTabs` component](../components.md#settingstabs)
- [PMS pages](../pages/pms/README.md)
