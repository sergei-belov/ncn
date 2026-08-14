# Project Variables Screen

## Location
URL: `/qai/projects/:project_id/variables`

## Purpose
The Project Variables screen manages reusable project-level configuration values that can be referenced from any pipeline in the current project. It is the canonical place for storing non-secret and secret inputs such as base URLs, usernames, environment IDs, build numbers, and passwords.

## Features
- List project variables in a searchable table
- Create a new variable with one of four supported types
- Edit an existing variable
- Delete a variable from the project
- Copy placeholder syntax for insertion into pipeline steps
- Mask secret values after they are saved

## Links to Other Screens
- [Project Detail Screen](ProjectDetailScreen.md) (URL: `/qai/projects/:project_id`) - Overview card links into the variables module
- [Pipeline Detail Screen](PipelineDetailScreen.md) (URL: `/qai/projects/:project_id/pipelines/:pipeline_id`) - Step field editors can insert project variable placeholders

## Design Description
The page lives inside the shared project layout and uses the persistent left sidebar for section navigation.

- **Header Area**: screen title, explanatory text, refresh action, and “Add Variable” button
- **Filter Area**: search field and summary chips for totals and secrets
- **Variables Table**: typed values, placeholder preview, timestamps, and row actions
- **Variable Dialog**: create/edit form with type-aware value input and placeholder preview
- **Delete Dialog**: confirmation before destructive removal

UI Guidelines:
- Secret values must remain masked after save
- Placeholder syntax is always shown as `{{VARIABLE_NAME}}`
- Variables are project-wide and should not be visually framed as pipeline-scoped entities

## Components Used
- `ProjectSidebar` - persistent left navigation between project sections
- `AppHeader` - global header and breadcrumbs
- `ProjectVariablesView` - full variables management page implementation
- `VariableSelector` - compact selector used inside pipeline step editing UIs

## System Flow

### System Interactions:
1. **Variable Listing Flow**:
   - User opens the Variables section from the left sidebar
   - `GET /api/qai/v1/projects/:project_id/variables` loads the current project variable set
   - Table renders typed values and placeholder tokens

2. **Variable Creation Flow**:
   - User clicks “Add Variable”
   - Dialog collects name, type, description, and value
   - `POST /api/qai/v1/projects/:project_id/variables` creates the variable
   - The table refreshes and the new placeholder becomes available in pipeline step editors

3. **Variable Editing Flow**:
   - User clicks edit on a row
   - Existing metadata is loaded into the dialog
   - For secret variables, the current value remains hidden and can optionally be replaced
   - `PATCH /api/qai/v1/projects/:project_id/variables/:variable_id` updates the record

4. **Variable Usage in Pipeline Flow**:
   - User opens a step in the pipeline editor
   - `VariableSelector` loads project variables
   - User picks a variable and the placeholder is inserted into the field as `{{VARIABLE_NAME}}`

### API Interactions:
- Page opened → `GET /api/qai/v1/projects/:project_id/variables`
- Variable created → `POST /api/qai/v1/projects/:project_id/variables`
- Variable edited → `PATCH /api/qai/v1/projects/:project_id/variables/:variable_id`
- Variable deleted → `DELETE /api/qai/v1/projects/:project_id/variables/:variable_id`

### Data Flow:
- Backend stores the public type and concrete value inside the existing JSON column
- Secret values are not returned through the public API after save; only masked display text is returned
- Frontend caches variable options for reuse in the pipeline editor selector
- Step fields store placeholders, not resolved values

## API Endpoints Used
- `GET /api/qai/v1/projects/:project_id/variables` - List project variables
- `POST /api/qai/v1/projects/:project_id/variables` - Create variable
- `PATCH /api/qai/v1/projects/:project_id/variables/:variable_id` - Update variable
- `DELETE /api/qai/v1/projects/:project_id/variables/:variable_id` - Delete variable

### GET `/api/qai/v1/projects/:project_id/variables`
**Request Query Parameters:**
- `search` (string, optional): search by variable name
- `sort_by` (string, optional): `name`, `created_at`, `updated_at`
- `sort_order` (string, optional): `asc` or `desc`
- `limit` (integer, optional): page size
- `offset` (integer, optional): pagination offset

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "project_id": "uuid",
      "name": "BASE_URL",
      "description": "Base environment url",
      "type": "string",
      "value": "https://demo.example.com",
      "display_value": "https://demo.example.com",
      "placeholder": "{{BASE_URL}}",
      "secret": false,
      "masked": false,
      "created_at": "2026-04-13T20:00:00Z",
      "updated_at": "2026-04-13T20:00:00Z"
    }
  ],
  "meta": {
    "total_count": 1,
    "offset": 0,
    "limit": 100
  }
}
```

### POST `/api/qai/v1/projects/:project_id/variables`
**Request Body:**
```json
{
  "name": "BASE_URL",
  "description": "Base environment url",
  "type": "string",
  "value": "https://demo.example.com"
}
```

### PATCH `/api/qai/v1/projects/:project_id/variables/:variable_id`
**Request Body:**
```json
{
  "description": "Updated description",
  "value": "https://staging.example.com"
}
```
