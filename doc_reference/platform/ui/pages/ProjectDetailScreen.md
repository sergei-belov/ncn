# Project Detail Screen

## Location
URL: `/qai/projects/:project_id`

## Purpose
Displays detailed information about one project and provides project-level entry points into the main working areas. The screen combines core project metadata with lightweight overview statistics so the user can quickly understand the project scope before opening pipelines, runs, or variables.

## Features
- Project metadata (name, description, creation date)
- Project statistics cards (pipelines, runs, users)
- Navigation to project-specific features
- Quick access to related project resources
- Display of lightweight project overview counters

## Links to Other Screens
- [Projects List Screen](ProjectsListScreen.md) (URL: `/qai/projects`) - Return to the main projects dashboard
- [Pipelines Screen](PipelinesScreen.md) (URL: `/qai/projects/:project_id/pipelines`) - View pipeline drafts and published versions for this project
- [Project Variables Screen](ProjectVariablesScreen.md) (URL: `/qai/projects/:project_id/variables`) - Configure project variables and secrets
- [Project Runs Screen](ProjectRunsScreen.md) (URL: `/qai/projects/:project_id/runs`) - Open project-wide run history
- [Project Graph Screen](ProjectGraphScreen.md) (URL: `/qai/projects/:project_id/graph`) - Open the tested-application information model for pages, states, actions, and graph builder sessions

## Design Description
Main project detail view featuring statistics cards and project overview information with quick access to related resources:

- **Sidebar Navigation**: Position on the left side of the screen, contains navigation links to other platform sections and project-specific pages. Implements the general Sidebar component with collapsible menu items.
- **Header Section**: Displays project name, description and basic metadata at the top of the page, positioned below the main navbar
- **Statistics Cards Section**: Shows project statistics in three distinct cards:
  - Pipelines statistics card showing the total number of pipelines in the project
  - Runs statistics card showing the total number of created runs in the project
  - Users statistics card showing the total number of users in the project
- **Quick Access Panel**: Provides links to all project-specific features and resources
- **Content Area**: Central area where project statistics and related resources are displayed

UI Guidelines:
- Use consistent card-based design with appropriate spacing between components
- Implement responsive grid layout for statistics cards that adapts to different screen sizes
- Highlight important project counters with visual indicators and clear typography
- Ensure consistent styling with other platform screens using Vuetify components
- Position sidebar navigation consistently on the left for project-related pages

## Components Used
- Navbar component - Provides platform-wide navigation at the top of the screen
- Sidebar component - Implements left-side navigation for project-specific pages
- Statistics cards component - Shows key metrics and project activity in card format
- Project details viewer - Displays all project information in a structured format
- Navigation buttons to sub-features - Quick access to related project resources

## System Flow

### System Interactions:
1. **Project Loading**:
   - Page loads and calls `GET /api/qai/v1/projects/:project_id` to retrieve project data
   - Retrieved data is displayed in the project detail view
   - Header and overview blocks are populated with project metadata

2. **Statistics Loading**:
   - Page calls `GET /api/qai/v1/projects/:project_id/pipelines_stats` to retrieve the total pipelines count
   - Page calls `GET /api/qai/v1/projects/:project_id/runs_stats` to retrieve the total runs count
   - Page calls `GET /api/qai/v1/projects/:project_id/users_stats` to retrieve the total users count
   - Retrieved totals are displayed in dedicated overview cards

3. **Navigation Flow**:
   - User can navigate to project-specific features using sidebar navigation
   - Each navigation item links to related project resources and screens

### API Interactions:
- Page load → `GET /api/qai/v1/projects/:project_id` retrieves project details to display
- Page load → `GET /api/qai/v1/projects/:project_id/pipelines_stats` retrieves the total pipelines count
- Page load → `GET /api/qai/v1/projects/:project_id/runs_stats` retrieves the total runs count
- Page load → `GET /api/qai/v1/projects/:project_id/users_stats` retrieves the total users count
- Navigation event → Route to various project-specific URLs like `/pipelines`, `/variables`, and `/runs`

### Data Flow:
- Project ID is passed via route parameter to identify which project to display
- API response data populates the project detail fields and statistics cards
- Statistics cards display lightweight totals from dedicated stats endpoints
- User can click on navigation items to access project-specific features

## API Endpoints Used
- `GET /api/qai/v1/projects/:project_id` - retrieve project details
- `GET /api/qai/v1/projects/:project_id/pipelines_stats` - retrieve the total pipelines count
- `GET /api/qai/v1/projects/:project_id/runs_stats` - retrieve the total runs count
- `GET /api/qai/v1/projects/:project_id/users_stats` - retrieve the total users count

### Shared API Models
```txt
type ProjectDetailResponse = {
  id: uuid
  name: str
  description: null | str
  created_at: datetime
  role: enum(owner, admin, user)
}

type ProjectOverviewStatsResponse = {
  total_count: int
}
```

### GET /api/qai/v1/projects/:project_id
**Response Model:**
```txt
ProjectDetailResponse
```

### GET /api/qai/v1/projects/:project_id/pipelines_stats
**Response Model:**
```txt
ProjectOverviewStatsResponse
```

### GET /api/qai/v1/projects/:project_id/runs_stats
**Response Model:**
```txt
ProjectOverviewStatsResponse
```

### GET /api/qai/v1/projects/:project_id/users_stats
**Response Model:**
```txt
ProjectOverviewStatsResponse
```
