# Pipelines Screen

## Location
URL: `/qai/projects/:project_id/pipelines`

## Purpose
The Pipelines screen is the project inventory for versioned test cases. It shows mutable pipeline drafts, their active published versions, and the operational state needed to decide whether a test case is ready to publish or launch. It also hosts the project-level AI-assisted preview flow for creating one new draft pipeline from a free-form user description.

## Features
- Search and filter pipelines by name, code, status, priority, and tags
- Show draft metadata together with versioning metadata
- Display active version badges such as `v3`
- Highlight unpublished draft changes
- Create, edit, and delete pipeline drafts
- Open inline AI generation sidebar / drawer for one-session preview-based draft creation
- Start one generation session from a free-form description and review shortened trace updates
- Insert project variable placeholders into the AI request through a searchable variable picker before starting the session
- Edit, accept, reject, or regenerate the latest active preview before any draft is created
- Publish the current draft as a new immutable version
- Open the draft editor for graph changes
- Launch only the currently active published version

## Links to Other Screens
- [Projects List Screen](ProjectsListScreen.md) (URL: `/qai/projects`) - main dashboard with project entry points
- [Project Detail Screen](ProjectDetailScreen.md) (URL: `/qai/projects/:project_id`) - project overview and section navigation
- [Pipeline Detail Screen](PipelineDetailScreen.md) (URL: `/qai/projects/:project_id/pipelines/:pipeline_id`) - draft editor and full version history
- [Project Runs Screen](ProjectRunsScreen.md) (URL: `/qai/projects/:project_id/runs`) - project-wide launch history for published versions

## Design Description
The screen uses a master-detail pattern inside the shared project layout.

- **Header Area**: page title, helper text, primary action for creating a new pipeline draft, and `AI Generate` action for project-level AI generation
- **Inline AI Generation Sidebar / Drawer**:
  - opened from the header action `AI Generate`
  - accepts a free-form scenario description for one draft pipeline candidate
  - includes a searchable project variable picker that inserts placeholders such as `{{BASE_URL}}` into the request text
  - shows session status, shortened trace, preview summary, and validation warnings
  - allows preview editing, acceptance, rejection, and regeneration inside the list screen before the draft is created
- **Filter Toolbar**: search input, status/priority/tag filters, and sort controls
- **Pipeline Table**:
  - code and name
  - priority, tags, status, and actuality
  - active version badge
  - versions count
  - unpublished-draft indicator
  - last run timestamp and status
- **Detail Sidebar**:
  - draft metadata
  - version summary for the selected pipeline
  - publish action for the current draft
  - run action for the active version
  - quick path into the full editor/history screen
- **Validation Banner**: explicit warning when a pipeline has no published version and therefore cannot be launched

UI Guidelines:
- The list must distinguish clearly between draft state, published version state, and inline AI preview state
- Launch controls must always communicate which version will run
- Publish state should be visible without entering the editor
- A pipeline with no active version must not look runnable
- Inline AI generation must not silently create a pipeline draft; the preview must be visible and editable before accept
- The first-stage inline generation flow is limited to one generated pipeline per session
- Regenerate keeps the same session and replaces the active preview by superseding the previous one

## Components Used
- `ProjectSidebar.vue` - persistent left navigation for project sections
- `AppHeader.vue` - breadcrumbs and global application controls
- `PipelinesListView.vue` - main screen container
- `PipelineTable.vue` - server-driven pipeline inventory
- `PipelineDetailSidebar.vue` - selected pipeline summary and quick actions
- `PipelineCreateSidebar.vue` - create-draft flow
- `PipelineEditSidebar.vue` - draft metadata editing flow
- `StatusBadge.vue` - shared status visualization
- `PriorityBadge.vue` - shared priority visualization
- `TagChip.vue` - tag display and filtering support
- `AIGenerationSidebar.vue` - inline AI generation request and review container
- `VariableSelector.vue` - searchable project variable picker embedded into the AI request form
- `AIGenerationTrace.vue` - shortened trace renderer for visible session messages
- `AIPreviewEditor.vue` - editable preview form before accept

## System Flow

### System Interactions:
1. **Initial Load**:
   - User opens `/qai/projects/:project_id/pipelines`
   - `GET /api/qai/v1/projects/:project_id/pipelines` loads the paginated draft inventory with version summary fields
   - First row or previously selected pipeline opens in the detail sidebar

2. **Pipeline Selection Flow**:
   - User selects a pipeline row
   - `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id` loads the draft metadata
   - `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions` loads publish history summary for the sidebar

3. **Publish Flow**:
   - User clicks Publish in the detail sidebar
   - Optional publish note is entered
   - `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions` creates a new immutable version snapshot
   - The new version becomes active and the list refreshes with updated `active_version_number`, `versions_count`, and draft status

4. **Run Flow**:
   - User clicks Run from the row action menu or detail sidebar
   - UI resolves the currently active published version
   - `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run` creates a run for that version and queues Playwright execution
   - Frontend redirects to `/qai/projects/:project_id/runs?run_id=...`

5. **Edit Draft Flow**:
   - User edits pipeline metadata from the sidebar or opens the editor
   - `PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id` updates the draft metadata
   - If the draft diverges from the active published version, the screen shows an unpublished-changes indicator

6. **Delete Flow**:
   - User deletes a pipeline draft
   - `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id` removes the live draft from the active inventory
   - Published versions and recorded runs remain intact for historical resolution
   - The list refreshes and selection moves to the next available item

7. **Inline AI Generation Session Flow**:
   - User clicks `AI Generate` in the header and opens the inline generation sidebar
   - User writes a free-form description of the desired scenario
   - User may search project variables inside the sidebar and insert placeholders such as `{{BASE_URL}}` into the description before submission
   - Variable insertion only changes the local request text; the AI generation request model is not extended
   - `POST /api/qai/v1/projects/:project_id/ai/generations` creates a new AI generation session with `mode = description_to_pipeline`
   - Backend stores the session, publishes a thin Kafka task envelope, and returns `session_id`
   - Frontend starts polling the session state through:
     - `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id`
     - `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/messages?after_seq=...&view=ui`
   - When the session reaches `awaiting_review`, frontend loads the latest preview through `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id`

8. **Inline Preview Review Flow**:
   - User reviews the latest active preview inside the sidebar
   - User may edit preview fields, generated steps, generated links, assertions, and `suggested_variables`
   - `PATCH /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id` saves the edited preview state
   - `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/accept` applies the preview through backend domain managers and creates one new mutable draft pipeline
   - The list refreshes and the created pipeline becomes available as a normal draft row in the table

9. **Inline Reject / Regenerate Flow**:
   - User rejects the current preview with `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/reject`
   - Or requests a regenerate action in the same session
   - The current preview becomes `superseded`
   - The newly generated preview becomes `active`
   - Trace polling continues from the latest known `after_seq`

### API Interactions:
- Page load → `GET /api/qai/v1/projects/:project_id/pipelines`
- Pipeline selected → `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id`
- Version summary opened → `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions`
- Draft published → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions`
- Draft metadata updated → `PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id`
- Pipeline deleted → `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id`
- Active version launched → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run`
- Variables searched in AI sidebar → `GET /api/qai/v1/projects/:project_id/variables`
- Inline AI generation session created → `POST /api/qai/v1/projects/:project_id/ai/generations`
- Inline AI generation session polled → `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id`
- Inline AI generation messages polled → `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/messages`
- Inline AI preview loaded → `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id`
- Inline AI preview edited → `PATCH /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id`
- Inline AI preview accepted → `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/accept`
- Inline AI preview rejected → `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/reject`

### Data Flow:
- The list endpoint provides inventory-level draft and version metadata
- The selected pipeline keeps the draft and version history concerns separate
- Agent-generated candidates enter the inventory only after user acceptance creates a normal pipeline draft
- Publishing serializes the current draft into an immutable snapshot and refreshes the list state
- Launch actions never execute a floating draft; they resolve the active published version first
- If the live draft is deleted later, runs still resolve through `pipeline_version_id` and version snapshot data
- The variable picker inserts placeholder text into the local AI description editor; the submitted `CreateAIGenerationRequest.input.description` remains ordinary text and AI generation contracts stay unchanged
- The inline AI flow uses separate session, messages, and preview persistence and does not write to `pipelines`, `steps`, `steps_links`, or `assertions` until the user accepts the preview
- Messages are loaded incrementally by `seq_no` cursor through `after_seq`, not by offset, so the UI appends only new visible trace entries
- Acceptance applies the preview to live draft tables and then returns the created pipeline draft as a normal inventory item

## API Endpoints Used
- `GET /api/qai/v1/projects/:project_id/pipelines` - list pipeline drafts with version summary
- `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id` - get detailed draft metadata
- `PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id` - update draft metadata
- `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id` - delete pipeline draft
- `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions` - list published versions for one pipeline
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions` - publish the current draft
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run` - create and queue a run for the active published version
- `GET /api/qai/v1/projects/:project_id/variables` - load searchable project variables for frontend-only AI request placeholder insertion
- `POST /api/qai/v1/projects/:project_id/ai/generations` - create inline AI generation session for one new draft pipeline
- `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id` - get session status, progress, latest message seq, and latest preview id
- `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/messages` - poll shortened or full trace messages using `after_seq`
- `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id` - load one preview artifact
- `PATCH /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id` - edit preview before accept
- `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/accept` - apply preview and create one new draft pipeline
- `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/reject` - reject the latest active preview

### GET /api/qai/v1/projects/:project_id/pipelines
**Request Query Parameters:**
- `search` (string, optional): filter by pipeline name or code
- `status` (enum, optional): filter by draft status
- `priority` (enum, optional): filter by priority
- `tags` (array, optional): filter by tags
- `sort_by` (enum, optional): `created_at`, `name`, `priority`
- `sort_order` (enum, optional): `asc` or `desc`
- `limit` (integer, optional): page size
- `offset` (integer, optional): pagination offset

**Response:**
```json
{
  "data": [
    {
      "id": "uuid-string",
      "code": "TC-001",
      "name": "User Login Validation",
      "description": "Happy-path login scenario",
      "priority": "high",
      "tags": ["smoke", "auth"],
      "status": "pending",
      "actuality": "actual",
      "steps_count": 6,
      "created_at": "2026-04-24T09:00:00Z",
      "updated_at": "2026-04-24T10:10:00Z",
      "last_run_at": "2026-04-24T11:00:00Z",
      "last_run_status": "completed",
      "active_version_id": "uuid-string",
      "active_version_number": 3,
      "versions_count": 3,
      "has_unpublished_changes": true
    }
  ],
  "meta": {
    "total_count": 1,
    "offset": 0,
    "limit": 25
  }
}
```

### GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions
**Response:**
```json
{
  "data": [
    {
      "id": "uuid-string",
      "version_number": 1,
      "is_active": false,
      "publish_note": "Initial published draft",
      "created_at": "2026-04-17T13:00:00Z"
    },
    {
      "id": "uuid-string",
      "version_number": 3,
      "is_active": true,
      "publish_note": "Stable smoke baseline",
      "created_at": "2026-04-24T10:15:00Z"
    }
  ]
}
```

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions
**Request Body:**
```json
{
  "publish_note": "Stable smoke baseline"
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "pipeline_id": "uuid-string",
  "version_number": 3,
  "is_active": true,
  "publish_note": "Stable smoke baseline",
  "created_at": "2026-04-24T10:15:00Z"
}
```

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run
**Response:**
```json
{
  "run_id": "uuid-string",
  "run_pipeline_id": "uuid-string",
  "status": "queued",
  "execution_mode": "playwright",
  "pipeline_version_id": "uuid-string",
  "pipeline_version_number": 3,
  "message": "Pipeline version v3 queued for Playwright execution.",
  "created_at": "2026-04-24T11:00:00Z"
}
```


### Shared API Models For Inline AI Generation
```txt
type AIGenerationSessionStatus = enum(created, queued, running, awaiting_review, accepted, rejected, failed, cancelled)
type AIGenerationTargetScope = enum(project)
type AIGenerationMode = enum(description_to_pipeline)

type AIGenerationVisibleStage = enum(input, planning, execution, validation, result, error)
type AIGenerationMessageView = enum(ui, full)

type AIGenerationMessage = {
  id: uuid
  session_id: uuid
  seq_no: int
  agent_role: enum(user, planner, qai_agent, validator, tool, system)
  stage: AIGenerationVisibleStage
  message_type: enum(text, json, event)
  is_visible_in_ui: bool
  summary_text: null | str
  content_text: null | str
  content_json: null | json
  created_at: datetime
}

type AIGenerationSuggestedVariable = {
  name: str
  secret: bool
  description: null | str
}

type AIPreviewStep = {
  temp_id: str
  step_id: null | uuid
  name: str
  description: null | str
  case: null | str
  code: json
}

type AIPreviewLink = {
  temp_id: str
  link_id: null | uuid
  upstream_ref: str
  downstream_ref: str
  condition_type: enum(always)
}

type AIPreviewAssertion = {
  temp_id: str
  assertion_id: null | uuid
  step_ref: str
  name: str
  description: null | str
  code: json
}

type AIGenerationPreviewPayload = {
  schema_version: int
  kind: enum(pipeline_draft_create)
  pipeline: {
    pipeline_id: null | uuid
    name: str
    description: null | str
    priority: null | str
    tags: str[]
  }
  steps: AIPreviewStep[]
  steps_links: AIPreviewLink[]
  assertions: AIPreviewAssertion[]
  suggested_variables: AIGenerationSuggestedVariable[]
}

type AIGenerationValidationReport = {
  is_valid: bool
  warnings: str[]
  fallback_used: bool
}

type AIGenerationPreview = {
  id: uuid
  session_id: uuid
  preview_kind: enum(pipeline_draft_create)
  status: enum(draft, active, accepted, rejected, superseded)
  normalized_payload: AIGenerationPreviewPayload
  validation_report: AIGenerationValidationReport
  created_at: datetime
  updated_at: datetime
}

type CreateAIGenerationRequest = {
  mode: enum(description_to_pipeline)
  target_scope: enum(project)
  pipeline_id?: null
  step_id?: null
  input: {
    description: str
  }
  options?: {
    preview_only?: bool
    model_profile?: null | str
  }
}

type AIGenerationSessionResponse = {
  id: uuid
  project_id: uuid
  pipeline_id: null | uuid
  step_id: null | uuid
  mode: AIGenerationMode
  target_scope: AIGenerationTargetScope
  status: AIGenerationSessionStatus
  latest_preview_id: null | uuid
  latest_message_seq: int
  progress_stage: null | str
  progress_percent: null | int
  error_payload: null | json
  created_at: datetime
  updated_at: datetime
}

type AIGenerationMessagesResponse = {
  session_id: uuid
  messages: AIGenerationMessage[]
  next_after_seq: int
  has_more: bool
}

type PatchAIPreviewRequest = {
  normalized_payload?: AIGenerationPreviewPayload
}

type AcceptAIPreviewRequest = {
  preview_id: uuid
  apply_mode: enum(create_pipeline_draft)
}

type AcceptAIPreviewResponse = {
  preview_id: uuid
  pipeline_id: uuid
  status: enum(draft_created)
  redirect_url: str
}

type RejectAIPreviewResponse = {
  preview_id: uuid
  status: enum(rejected)
  rejected_at: datetime
}
```

### POST /api/qai/v1/projects/:project_id/ai/generations
**Request Body Model:**
```txt
CreateAIGenerationRequest
```

**Response Model:**
```txt
AIGenerationSessionResponse
```

Notes:
- The list-screen inline generation flow uses `mode = description_to_pipeline`.
- `target_scope` is always `project` on this screen.
- The first implementation stage allows at most one generated pipeline per session.
- Variable placeholders selected in the sidebar are inserted into `input.description` before this request is sent; no additional request fields are introduced.

### GET /api/qai/v1/projects/:project_id/variables
Notes:
- The AI sidebar reuses the existing project variables list endpoint documented by [Project Variables Screen](ProjectVariablesScreen.md).
- The optional `search` query filters variables by name for the sidebar picker.
- Selecting a variable inserts its placeholder into the local AI request text; this does not create, update, or resolve variable values.

### GET /api/qai/v1/projects/:project_id/ai/generations/:session_id
**Response Model:**
```txt
AIGenerationSessionResponse
```

Notes:
- Frontend polls this endpoint while status is `queued` or `running`.
- `latest_preview_id` becomes non-null when the session reaches `awaiting_review`.

### GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/messages
**Request Query Parameters:**
- `after_seq` (integer, optional): return only messages with `seq_no > after_seq`
- `limit` (integer, optional): page size for incremental polling, recommended `1..200`
- `view` (enum, optional): `ui` returns only shortened visible trace, `full` returns the full audit trail

**Response Model:**
```txt
AIGenerationMessagesResponse
```

Notes:
- UI polling uses cursor-based incremental loading by `after_seq`, not offset pagination.
- The next request should pass `next_after_seq` from the previous response.

### GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id
**Response Model:**
```txt
AIGenerationPreview
```

Notes:
- The response returns the active preview artifact and validation metadata for sidebar review.

### PATCH /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id
**Request Body Model:**
```txt
PatchAIPreviewRequest
```

**Response Model:**
```txt
AIGenerationPreview
```

Notes:
- Users may edit pipeline metadata, steps, `steps_links`, assertions, and `suggested_variables` before accept.

### POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/accept
**Request Body Model:**
```txt
AcceptAIPreviewRequest
```

**Response Model:**
```txt
AcceptAIPreviewResponse
```

Notes:
- Accept applies the preview to live draft tables and creates one new mutable pipeline draft.
- The flow does not auto-publish a version.

### POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/reject
**Response Model:**
```txt
RejectAIPreviewResponse
```

Notes:
- Reject marks the current preview as rejected and keeps the session history available for audit.
