# Projects List Screen

## Location
URL: `/qai/projects`

## Purpose
The main dashboard screen showing all projects a user has access to. This is typically the landing page after login.

## Features
- List view of user projects with key statistics
- Search and filtering capabilities
- Sorting options (by name, creation date)
- Ability to create new projects
- Quick access to project details

## Links to Other Screens
- [Project Detail Screen](ProjectDetailScreen.md) (URL: `/qai/projects/:project_id`) - Open a selected project workspace
- [Project Navigation Screen](project_navigation.md) (URL: `/qai/projects/:project_id/*`) - Shared layout after entering a project

## Design Description
The page layout follows a clean, card-based design with a responsive structure using Vuetify components:

- **Header Section**: Positioned at the top, contains the page title "Мои проекты" (My Projects) and a primary "Создать проект" (Create Project) button aligned to the right
- **Search Bar**: Below the header, a prominent text field with a search icon and clearable functionality for filtering projects
- **Project Table**: Main content area displaying projects in a tabular format with statistics columns and infinite scroll
- **Modal Dialog**: Overlay component that appears when creating a new project

UI Guidelines:
- Uses the primary color palette for action buttons
- Responsive container with padding (pa-4 class)
- Consistent typography with text-h5 heading
- Debounced search with 400ms delay for smooth user experience
- Card-style layout with proper spacing between elements

## Components Used
- ProjectTable component to display projects
- ProjectCreateDialog component for creating new projects
- Search and filtering controls

## System Flow

### System Interactions:
1. **Initial Load**: On loading of page `/qai/projects`, `GET /api/qai/v1/projects` is triggered. The projects are displayed in Project Table component.
2. **Project Creation Flow**:
   - User clicks "Создать проект" button on page
   - Create Project Dialog opens for user input on page
   - User submits project data → `POST /api/qai/v1/projects` is triggered
   - After successful creation, the project list is refreshed by calling `GET /api/qai/v1/projects`
3. **Project Navigation**:
   - User clicks on a project in the table on page
   - System navigates from `/qai/projects` to `/qai/projects/:project_id` for the selected project ID
4. **Search Flow**:
   - User enters search terms in the search field on Search Bar
   - After 400ms delay (debounced input), `GET /api/qai/v1/projects` is called with search parameters
   - Filtered results are displayed in the Project Table on page

### API Interactions:
- Page `/qai/projects` loads → `GET /api/qai/v1/projects` retrieves all projects with statistics
- New project created on `/qai/projects` → `POST /api/qai/v1/projects` adds project to the system
- Search executed on `/qai/projects` → `GET /api/qai/v1/projects` filters projects based on search criteria
- Project selected on `/qai/projects` → Navigation to `/qai/projects/:project_id` for further interactions

### Data Flow:
- API responses populate the project list shown in the UI
- User inputs are validated and sent to API endpoints
- System updates UI based on API responses and user selections

## API Endpoints Used
- `GET /api/qai/v1/projects` - Fetch list of projects
- `POST /api/qai/v1/projects` - Create new project


### GET /api/qai/v1/projects
**Request Query Parameters:**
- `search` (string, optional): Search term for filtering projects
- `sort_by` (enum): Sort by 'name' or 'created_at' (default: 'created_at' in actual implementation)
- `sort_order` (enum): Sort order 'asc' or 'desc' (default: 'desc' in actual implementation)
- `limit` (integer): Maximum number of results to return (default: 1000)

**Response:**
```json
{
  "data": [
    {
      "id": "uuid-string",
      "name": "string (max 100 chars)",
      "description": "string or null",
      "created_at": "ISO 8601 datetime string",
      "stats": {
        "pipelines": "integer",
        "last_run_at": "ISO 8601 datetime string or null"
      },  
      "role": "enum (owner, admin, user)"
    }
  ],
  "meta": {
    "total_count": "integer",
    "offset": "integer",
    "limit": "integer"
  }
}
```

### POST /api/qai/v1/projects
**Request Body:**
```json
{
  "name": "string (3-100 chars)",
  "description": "string (max 500 chars) or null"
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "name": "string",
  "description": "string or null",
  "created_at": "ISO 8601 datetime string"
}
```