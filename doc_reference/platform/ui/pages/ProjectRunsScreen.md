# Project Runs Screen

## Location
URL: `/qai/projects/:project_id/runs`

## Purpose
The Project Runs screen provides one project-wide launch history for versioned test cases. It shows what was launched, when it was launched, and which concrete published pipeline version was resolved for each target at launch time.

## Features
- Search and filter project runs by title, status, pipeline, and tag
- Create a run from selected pipelines and/or tags
- Show pipeline code together with version number in the history table
- Open a run details drawer with resolved launch targets
- Auto-open a run after launch from a pipeline-related screen
- Show queued Playwright execution status and result messages
- Open execution results by run, pipeline, step, and assertion when available

## Links to Other Screens
- [Project Navigation Screen](project_navigation.md) (URL: `/qai/projects/:project_id/*`) - left sidebar entry point into runs
- [Pipelines Screen](PipelinesScreen.md) (URL: `/qai/projects/:project_id/pipelines`) - select test cases and see publish state before launching
- [Pipeline Detail Screen](PipelineDetailScreen.md) (URL: `/qai/projects/:project_id/pipelines/:pipeline_id`) - draft editor can publish and launch active versions

## Design Description
The page lives inside the shared project layout and treats run history as a project-level concern.

- **Header Area**: title, helper text, and “New Run” action
- **Info Banner**: explicit note that launches are version-aware and are queued for Playwright execution
- **Filter Toolbar**:
  - search
  - status selector
  - pipeline selector
  - tag selector
- **Runs Table**:
  - title
  - status
  - target type
  - selected pipelines with version badges such as `TC-001 v3`
  - per-pipeline execution status when result data is available
  - tags
  - created timestamp
  - open-details action
- **Create Run Sidebar**:
  - optional title
  - pipeline multi-select
  - tag multi-select
  - validation that selected pipelines have an active published version
- **Run Details Drawer**:
  - metadata
  - resolved pipeline/version pairs
  - tags
  - execution mode, queue message, result summaries, and per-pipeline error details

UI Guidelines:
- Runs must be presented as project-wide history, not only as children of one pipeline
- The screen must surface the concrete published version used at launch
- Validation errors about missing active versions should be explicit before run creation

## Components Used
- `ProjectSidebar.vue` - persistent project navigation
- `AppHeader.vue` - global header and breadcrumbs
- `ProjectRunsView.vue` - main runs screen implementation
- `RunTable.vue` - project-wide runs history table
- `RunDetailSidebar.vue` - selected run metadata and target details
- `StatusBadge.vue` - shared lifecycle state visualization

## System Flow

### System Interactions:
1. **Runs Listing Flow**:
   - User opens `/qai/projects/:project_id/runs`
   - `GET /api/qai/v1/projects/:project_id/runs` loads the current run history
   - Table renders status, target type, and resolved pipeline/version pairs

2. **Create Run Flow**:
   - User opens the New Run sidebar
   - `GET /api/qai/v1/projects/:project_id/pipelines` loads selectable pipelines and publish state
   - User selects one or more pipelines and/or tags
   - `POST /api/qai/v1/projects/:project_id/runs` creates a run and queues Playwright execution
   - The list refreshes and the created run opens in the details drawer

3. **Pipeline Launch Flow**:
   - User launches from the pipelines list or pipeline editor
   - `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run` resolves the active published version, creates a run record, and queues Playwright execution
   - Frontend redirects to `/qai/projects/:project_id/runs?run_id=...`
   - The details drawer opens automatically for the new run

4. **Run Details Flow**:
   - User opens a run from the table
   - `GET /api/qai/v1/projects/:project_id/runs/:run_id` loads the full record
   - Drawer shows pipeline names, codes, and version numbers exactly as they were resolved at launch time

5. **Run Results Flow**:
   - User opens execution results for a run
   - `GET /api/qai/v1/projects/:project_id/runs/:run_id/results` loads the run, per-pipeline status fields, and persisted step/assertion results
   - Drawer shows Playwright execution progress, messages, errors, and available result rows without changing historical launch metadata

### API Interactions:
- Page opened → `GET /api/qai/v1/projects/:project_id/runs`
- Pipeline options loaded for create flow → `GET /api/qai/v1/projects/:project_id/pipelines`
- Run created from the runs screen → `POST /api/qai/v1/projects/:project_id/runs`
- Run created from a pipeline screen → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run`
- Run details opened → `GET /api/qai/v1/projects/:project_id/runs/:run_id`
- Run execution results opened → `GET /api/qai/v1/projects/:project_id/runs/:run_id/results`

### Data Flow:
- Backend persists top-level run history in `runs`
- Selected pipeline identities, resolved version ids, and per-pipeline execution state are linked through `run_pipelines`
- Resolved published version metadata is attached to the run payload so the UI can show stable version-aware history
- Run creation stores `execution_mode: playwright` and a queue message before background Playwright execution starts
- Persisted results are read separately from the run results endpoint so history and execution output can be refreshed independently
- If the live pipeline draft is deleted later, the runs screen still resolves historical labels from the linked published version
- Pipeline launch entry points pass `run_id` through the route query so the runs screen can open the correct record immediately

## API Endpoints Used
- `GET /api/qai/v1/projects/:project_id/runs` - list project runs
- `POST /api/qai/v1/projects/:project_id/runs` - create project run
- `GET /api/qai/v1/projects/:project_id/runs/:run_id` - get run details
- `GET /api/qai/v1/projects/:project_id/runs/:run_id/results` - get run execution results
- `GET /api/qai/v1/projects/:project_id/pipelines` - load pipeline choices and publish state for run creation
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run` - create and queue a run from one pipeline using its active version

### GET /api/qai/v1/projects/:project_id/runs
**Request Query Parameters:**
- `search` (string, optional): search by run title or tags
- `status` (string, optional): `queued`, `running`, `completed`, `failed`, `canceled`
- `pipeline_id` (uuid, optional): filter by pipeline family
- `tag` (string, optional): filter by tag
- `sort_by` (string, optional): `created_at`, `status`, `title`
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
      "title": "Smoke auth run",
      "status": "queued",
      "target_type": "pipelines",
      "execution_mode": "playwright",
      "message": "Playwright execution queued.",
      "pipeline_ids": ["uuid-1"],
      "tags": ["smoke"],
      "pipelines": [
        {
          "run_pipeline_id": "uuid-run-pipeline-1",
          "id": null,
          "code": "TC-001",
          "name": "User Login Validation",
          "tags": ["smoke", "auth"],
          "pipeline_version_id": "uuid-version-3",
          "pipeline_version_number": 3
        }
      ],
      "requested_by_user": "Jane Doe",
      "created_at": "2026-04-24T11:00:00Z",
      "started_at": null,
      "finished_at": null
    }
  ],
  "meta": {
    "total_count": 1,
    "offset": 0,
    "limit": 25
  }
}
```

### POST /api/qai/v1/projects/:project_id/runs
**Request Body:**
```json
{
  "title": "Checkout regression",
  "pipeline_ids": ["uuid-1", "uuid-2"],
  "tags": ["regress"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "project_id": "uuid-project",
  "title": "Checkout regression",
  "status": "queued",
  "target_type": "mixed",
  "execution_mode": "playwright",
  "message": "Playwright execution queued.",
  "pipeline_ids": ["uuid-1", "uuid-2"],
  "tags": ["regress"],
  "pipelines": [
    {
      "run_pipeline_id": "uuid-run-pipeline-1",
      "id": "uuid-1",
      "code": "TC-010",
      "name": "Checkout flow",
      "tags": ["regress"],
      "pipeline_version_id": "uuid-version-7",
      "pipeline_version_number": 7
    }
  ],
  "created_at": "2026-04-24T11:30:00Z"
}
```

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run
**Response:**
```json
{
  "run_id": "uuid",
  "run_pipeline_id": "uuid-run-pipeline-1",
  "status": "queued",
  "execution_mode": "playwright",
  "pipeline_version_id": "uuid-version-3",
  "pipeline_version_number": 3,
  "message": "Pipeline version v3 queued for Playwright execution.",
  "created_at": "2026-04-24T11:00:00Z"
}
```

### GET /api/qai/v1/projects/:project_id/runs/:run_id/results
**Response Model:**
```txt
type RunResultsResponse = {
  run_id: uuid
  project_id: uuid
  title: str
  status: enum(queued, running, completed, failed, canceled)
  execution_mode: enum(record_only, playwright)
  message: null | str
  started_at: null | datetime
  finished_at: null | datetime
  pipelines: RunPipelineResult[]
}

type RunPipelineResult = {
  run_pipeline_id: uuid
  pipeline_id: null | uuid
  pipeline_version_id: uuid
  pipeline_version_number: null | int
  code: null | str
  name: null | str
  status: enum(queued, running, passed, failed, skipped)
  message: null | str
  error: null | json
  started_at: null | datetime
  finished_at: null | datetime
  steps: RunStepResult[]
}

type RunStepResult = {
  id: uuid
  run_id: uuid
  run_pipeline_id: uuid
  pipeline_version_id: uuid
  step_id: uuid
  step_name: str
  step_index: int
  status: enum(queued, running, passed, failed, skipped)
  input: json
  output: json
  logs: json[]
  error: null | json
  started_at: null | datetime
  finished_at: null | datetime
  created_at: datetime
  assertions: RunAssertionResult[]
}

type RunAssertionResult = {
  id: uuid
  run_id: uuid
  run_step_result_id: uuid
  assertion_id: uuid
  assertion_name: str
  status: enum(queued, running, passed, failed, skipped)
  input: json
  output: json
  error: null | json
  started_at: null | datetime
  finished_at: null | datetime
  created_at: datetime
}
```

Notes:
- If the run does not belong to the current project or cannot be found, the backend returns `404` with detail `Run not found`.
- Step result rows come from `run_step_results` and are grouped under their `run_pipeline_id`.
- Assertion result rows come from `run_assertion_results` and are grouped under their parent `run_step_result_id`.
