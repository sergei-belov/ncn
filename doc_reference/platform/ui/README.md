# QAi Platform — Pages Documentation

This section documents the UI pages and components of the QAi platform, providing guidelines for consistent user interface design and component usage.

---

## 🏗️ General Page Structure

QAi platform pages follow a consistent structure to ensure a unified user experience:

- **Header/Navigation Bar**: Fixed top navigation present on most pages (except general pages like login and admin pages)
- **Sidebar**: Project navigation and main menu options (present on project-related pages)
- **Main Content Area**: Dynamic content specific to each page
- **Footer**: Informational elements and additional links (when applicable)

Most pages after `/qai/projects/:project_id` path typically follow the layout:
```
┌──────────────────────────────────────────────────┐
│ Header with logo, project name, breadcrumbs, user│
├──────────────────────────────────────────────────┤
│ Sidebar              │                           │
│                      │                           │
│ - Menu               │   Main Content Area       │
│ - Navigation         │                           │
│                      │                           │
└──────────────────────────────────────────────────┘
```

AI-generation flows introduced in Step 06 do **not** add a dedicated top-level route. They live inside existing Pipelines and Pipeline Detail screens as sidebars, drawers, and preview panels. These AI sidebars include frontend-only variable search controls that insert project variable placeholders into the user's request text without changing AI API contracts.

The project Graph introduced in Step 07 is a dedicated project-level route. It documents the tested application's navigable pages, DOM states, command-step graph, URL normalization rules, request diffs, and href candidates, but it does not replace pipeline authoring or run history.

Special pages (authentication, admin, setup) may have simplified layouts without standard navigation elements.

---

For detailed information about individual components, see the component documentation in the directories below:

### General Components
These components are used throughout the platform:
- [Navbar](general/Navbar.md)
- [Sidebar](general/Sidebar.md)
- [User Button](general/UserButton.md)

---
## 🌐 Application Route Structure

The currently documented pages describe the following route areas:

```
/qai
├── /projects
├── /projects/:project_id
├── /projects/:project_id/*
├── /projects/:project_id/variables
├── /projects/:project_id/runs
├── /projects/:project_id/graph
├── /projects/:project_id/pipelines
└── /projects/:project_id/pipelines/:pipeline_id
```

> Note: frontend page routes live under `/qai/projects/...`, while backend API endpoints live under `/api/qai/v1/...`.

## 📱 Available Pages

### Standard Pages (with Full Navigation)
| Page | Description |
|------|-------------|
| [🏠 Projects List](pages/ProjectsListScreen.md) | Landing page showing all available projects |
| [🧭 Project Navigation](pages/project_navigation.md) | Shared project shell with breadcrumbs and persistent sidebar |
| [📊 Project Detail](pages/ProjectDetailScreen.md) | Overview screen for project metadata and statistics |
| [🧩 Project Variables](pages/ProjectVariablesScreen.md) | Project-wide variables and secrets management |
| [🏃 Project Runs](pages/ProjectRunsScreen.md) | Project-wide launch history and run creation screen |
| [🗺️ Project Graph](pages/ProjectGraphScreen.md) | Project-level command-step information model for tested-application pages, states, href candidates, request diffs, and graph builder sessions |
| [🔗 Pipelines](pages/PipelinesScreen.md) | Pipeline list, publish state, and project-level AI generation entry |
| [🔧 Pipeline Detail](pages/PipelineDetailScreen.md) | Vue Flow redactor for one pipeline draft, dependencies, version history, and step-level AI generation |

### Special Purpose Pages (Simplified Layout)
At the moment, no simplified-layout page file is present in `platform/ui/pages`. If an authentication or admin page is documented later, it should be added here and mirrored in `spec.md`.

---

## 🎨 Design Principles

- **Consistency**: Standard pages maintain similar navigation and component patterns
- **Context-Sensitive Design**: Special pages (authentication, setup, admin) have simplified layouts when appropriate
- **Accessibility**: Components follow WCAG guidelines for accessibility
- **Responsiveness**: UI adapts to various screen sizes and devices
- **Intuitive Navigation**: Clear pathways between related functionalities on standard pages
- **Visual Hierarchy**: Proper use of typography, spacing, and emphasis
- **Hierarchical Structure**: Routes follow a logical hierarchy that reflects the relationship between entities
- **Preview-first AI UX**: AI-generated changes must be reviewed before touching live draft data
- **Read/Write Separation**: Published versions and AI previews must be visually distinct from editable draft state
- **Graph Isolation**: Project Graph data is informational in Step 07 and must remain visually separate from pipeline execution controls
