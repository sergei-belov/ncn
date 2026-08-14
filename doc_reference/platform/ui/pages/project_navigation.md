# Project Navigation Screen

## Location
URL: `/qai/projects/:project_id/*`

## Purpose
The project navigation layer defines how users move between the stabilized sections of a project. It combines the global application header breadcrumbs and the persistent left sidebar so that all core transitions stay in one predictable place.

## Features
- Global breadcrumbs in `AppHeader`
- Persistent left sidebar for project sections
- Sidebar entries for Overview, Graph, Pipelines, Agent Generation, Variables, Runs, Settings
- Variables section is a real screen
- Runs section is now a real project-wide history screen
- Graph section is a real project-level information model screen
- Settings remains an honest placeholder

## Links to Other Screens
- [Projects List Screen](ProjectsListScreen.md) (URL: `/qai/projects`) - entry point into a selected project
- [Project Detail Screen](ProjectDetailScreen.md) (URL: `/qai/projects/:project_id`) - overview screen inside the selected project
- [Project Graph Screen](ProjectGraphScreen.md) (URL: `/qai/projects/:project_id/graph`) - navigable information model for tested-application pages and states
- [Pipelines Screen](PipelinesScreen.md) (URL: `/qai/projects/:project_id/pipelines`) - active working area for test-case editing

## Design Description
The navigation layer is split into two visible areas:

- **App Header**: contains the logo, “All projects” shortcut, and breadcrumbs for project-level navigation
- **Project Sidebar**: contains all internal project transitions and remains visible inside `ProjectLayout`

UI Guidelines:
- Breadcrumbs are global and should not be duplicated inside content pages
- Left sidebar is the canonical place for switching project sections
- Unimplemented sections must use explicit placeholders instead of broken or misleading screens

## Components Used
- `AppHeader.vue` - global top navigation and breadcrumbs
- `ProjectSidebar.vue` - persistent left sidebar for project sections
- `ProjectGraphView.vue` - project-level Graph screen
- `ProjectRunsView.vue` - real project-wide runs history screen
- `ProjectSectionPlaceholderView.vue` - shared placeholder for disabled sections
- `ProjectLayout.vue` - wrapper combining sidebar and routed project content

## System Flow

### System Interactions:
1. **Project navigation flow**: User opens a project and switches between sections from the sidebar.
2. **Breadcrumb flow**: Route changes trigger `AppHeader` to rebuild breadcrumb items and resolve human-readable labels.

### API Interactions:
- Route change to a project page → `GET /api/qai/v1/projects/{project_id}` for breadcrumb/sidebar label resolution
- Route change to the graph page → `GET /api/qai/v1/projects/{project_id}/graph` for graph summary, backend start-command status, and derived start-state status
- Route change to a pipeline editor page → `GET /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}` for the last breadcrumb label
- Route change to the runs page → `GET /api/qai/v1/projects/{project_id}/runs` for the runs history list

### Data Flow:
- Route metadata defines section labels for placeholders and breadcrumb sections
- Sidebar links update the route
- Header reacts to route changes and updates breadcrumb items

## API Endpoints Used
- `GET /api/qai/v1/projects/{project_id}` - resolve project name for header and sidebar
- `GET /api/qai/v1/projects/{project_id}/graph` - load project graph summary for the Graph section
- `GET /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}` - resolve pipeline name for editor breadcrumbs
- `GET /api/qai/v1/projects/{project_id}/runs` - load project-wide run history
