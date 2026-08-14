# Pipeline Detail Screen

## Location
URL: `/qai/projects/:project_id/pipelines/:pipeline_id`

## Purpose
The Pipeline Detail screen is the Vue Flow redactor for one versioned test case draft. It lets the user build a graph of executable steps, assertions, and scenario branches, then publish the current draft as an immutable pipeline version for controlled launches. It also supports inline AI-assisted draft and step refinement through preview sessions that are applied only after explicit user acceptance.

## Features
- Visual drag-and-drop editor for the mutable draft graph
- Step-based graph where the initial state is also a step
- Multiple start steps for different scenarios inside one pipeline
- Directed links with one incoming link per non-start step and multiple outgoing links per step
- Add, edit, delete, and connect steps
- Step action popover with settings, lock, duplicate, run, delete, and create-from-actions commands
- Hover action on the output handle for quick child-step creation
- Shift multi-select for moving or deleting several steps together
- Edge hover deletion with confirmation
- Manage assertions and variable placeholders inside the draft
- Edit pipeline draft metadata such as name, description, tags, pre-pipelines, and post-pipelines
- Run an individual step through Playwright to populate generated code and update readiness status
- Publish the current draft as a new immutable version
- List published versions and highlight the active one
- Open a read-only snapshot view for a specific version
- Activate an older version without overwriting the current draft
- Launch the active published version from the editor
- Open inline AI refinement from the pipeline header for `patch_pipeline_draft`
- Open step-level AI actions for `patch_step` and `append_after_step`
- Insert project variable placeholders into AI prompt or description fields through a searchable picker in the AI sidebar
- Review, edit, accept, reject, or regenerate preview changes before the live draft is mutated

## Links to Other Screens
- [Pipelines Screen](PipelinesScreen.md) (URL: `/qai/projects/:project_id/pipelines`) - list of all pipeline drafts and quick publish/run actions
- [Project Variables Screen](ProjectVariablesScreen.md) (URL: `/qai/projects/:project_id/variables`) - source of variable placeholders used inside the draft
- [Project Runs Screen](ProjectRunsScreen.md) (URL: `/qai/projects/:project_id/runs`) - history of launches performed from this editor
- [Project Detail Screen](ProjectDetailScreen.md) (URL: `/qai/projects/:project_id`) - project overview and section navigation

## Design Description
The screen uses a full-screen editor layout with the Vue Flow canvas as the primary work area and supporting sidebars for draft properties, dependencies, version history, and inline AI preview review.

- **Header Area**:
  - breadcrumbs
  - editable draft name
  - active-version badge such as `v3`
  - draft-state badge such as `Unpublished changes`
  - Publish action for turning the current draft into an immutable version
  - pipeline-level Run action for launching the active published version
- **Main Canvas (Draft Editor)**:
  - Vue Flow graph for the mutable draft only
  - step nodes, custom edges, grid background, minimap, and controls
  - first created step is start by default
  - graph can contain several start steps for several scenarios inside one pipeline
  - start steps show only an output handle
  - non-start steps show input and output handles
  - each non-start step accepts only one incoming edge
  - each step can have several outgoing edges for branching
  - right output-handle hover reveals a compact `+` quick-create action
- **Step Node**:
  - title and optional description are the initial editable content
  - empty/new steps are allowed to exist before HTML, selector, and generated code are filled
  - circular readiness badge in the top corner shows whether the step is ready or not ready
  - assertions list rendered at the bottom of the node
  - each assertion row is compact and readable inside the node without opening the sidebar
  - no input handle when the step is treated as a start step
  - locked state is visible on the node and prevents canvas movement
- **Step Action Popover**:
  - opens after selecting any step
  - positioned under the selected node
  - uses icon buttons for settings, lock/unlock, duplicate, run step, delete, and create-from-actions
  - settings opens the right AppSidebar-style draft sidebar
  - double-clicking the node also opens the settings sidebar
  - run step is visually distinct from the header Run action because it validates and fills one draft step, not the published pipeline version
  - create-from-actions is available from the same popover and represents possible next actions from the current page state
- **Left Dependency Sidebar**:
  - hidden/collapsible panel so dependency controls do not compete with the graph
  - pre-pipeline selector for setup pipelines that run before the current pipeline
  - post-pipeline selector for follow-up or cleanup pipelines that run after the current pipeline
  - used for setup pipelines that must run before this pipeline and follow-up pipelines that must run after it
- **Bottom Selection Toolbar**:
  - appears when several steps are selected with Shift
  - stays attached to the bottom area of the Vue Flow canvas
  - uses icon buttons consistent with the single-step action popover
  - supports dragging the selected group together
  - current documented bulk action is delete
- **Right Draft Sidebar**:
  - AppSidebar-style panel opened by the settings icon or node double-click
  - step name, step description, and test case description fields
  - HTML/code-related fields
  - assertions
  - variable insertion buttons for step text and assertion text fields
  - placeholder insertion uses project variables such as `{{BASE_URL}}`
  - draft metadata editing
- **Edges**:
  - rendered as solid directed lines between handles
  - created through the standard Vue Flow drag-from-handle interaction
  - hover reveals a delete icon on the edge
  - delete opens a confirmation modal before removing the link
- **AI Preview Sidebar / Drawer**:
  - opened from the pipeline header AI action or step-level AI actions
  - displays the current generation mode: `patch_pipeline_draft`, `patch_step`, or `append_after_step`
  - includes a searchable project variable picker that inserts placeholders such as `{{BASE_URL}}` into the current AI prompt or description field
  - shows session status and shortened trace
  - shows preview diff summary and validation warnings
  - supports inline editing of generated steps, links, assertions, and suggested variables
  - supports `Accept`, `Reject`, and `Regenerate`
- **Versions Panel / Drawer**:
  - ordered list of published versions
  - active marker
  - publish note and timestamps
  - open snapshot action
  - activate action
- **Version Snapshot View**:
  - read-only rendering of the selected published version
  - no inline editing controls while a snapshot is being inspected
- **Validation Banner**:
  - shown when the pipeline has no active published version and therefore cannot be launched

UI Guidelines:
- The draft editor and version history must never be conflated
- Editing controls belong only to the draft view
- Snapshot views must be visually read-only
- Start-step state must be visually obvious because start steps have no input handle
- A non-start step must not accept more than one incoming edge
- Outgoing branching is allowed and should remain easy to scan on the canvas
- Locked steps must show a visual locked state and must not move during drag operations
- Destructive edge and step actions require explicit confirmation when they can remove graph structure
- Step-level Run and pipeline-level Run must use different labels, tooltips, or placement so the user does not confuse draft-step validation with active-version launch
- Variable insertion must be available at the exact field being edited, not only as a generic sidebar action
- Multi-select mode must keep selected nodes visually grouped while the user drags them
- Inline LLM-agent actions such as chat and automatic action choice are not part of this editor contract; project-level new-pipeline generation lives on the Pipelines screen
- The Run button must always indicate that it launches the active published version, not the live draft

## Components Used
- `ProjectSidebar.vue` - persistent project navigation
- `AppHeader.vue` - global header and breadcrumbs
- `PipelineEditorView.vue` - main editor container
- `VueFlow` - graph editor for the mutable draft
- `StepNode.vue` - visual representation of one draft step
- `StepActionPopover.vue` - icon action set shown for a selected step
- `CustomEdge.vue` - graph connection rendering
- `DependencySidebar.vue` - collapsible selector for pre/post pipelines
- `StepDetailSidebar.vue` - right-side draft editing panel
- `GraphSelectionToolbar.vue` - bottom toolbar for multi-step actions
- `VariableSelector.vue` - placeholder insertion UI for project variables in draft fields and AI request inputs
- `ConfirmDialog.vue` - confirmation dialog for destructive graph operations
- `FlowToolbar.vue` - canvas controls and editing shortcuts
- `VersionsPanel.vue` - published version history and activation controls
- `AIGenerationSidebar.vue` - generation session status and preview review
- `AIPreviewEditor.vue` - editable preview graph payload fields
- `AIGenerationTrace.vue` - shortened trace list fed from `messages` polling

## System Flow

### System Interactions:
1. **Initial Load**:
   - User opens `/qai/projects/:project_id/pipelines/:pipeline_id`
   - `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id` loads the draft metadata
   - `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps` loads all draft steps, links, and assertions without pagination
   - `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines` loads pre/post dependencies
   - `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions` loads published version history

2. **Step Creation Flow**:
   - First step in an empty pipeline is created as a start step
   - User can create a child step from the `+` action on an output handle
   - New steps start with name and description only; HTML, selectors, generated code, and status are filled later by step execution
   - Created step is persisted through `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps`

3. **Step Editing Flow**:
   - User selects a step and opens the settings sidebar from the popover or by double-clicking the node
   - Sidebar edits step name, description, selector/HTML-related fields, generated code metadata, and assertions
   - Variable insertion is available in step text fields, selector fields, and assertion fields
   - Draft mutations use the step and assertion endpoints under `/api/qai/v1/projects/:project_id/pipelines/:pipeline_id/...`
   - The screen marks the draft as changed if it diverges from the active published version

4. **Graph Linking Flow**:
   - User creates links by dragging from a step output handle to another step input handle
   - Backend rejects a second incoming link for the same downstream non-start step
   - A step with no incoming links may become a start step, which removes its input handle
   - One step may have multiple outgoing links for branching scenarios

5. **Step Action Flow**:
   - Selecting a step opens the icon popover under the node
   - Settings opens the right sidebar
   - Lock prevents the node from moving on the canvas
   - Duplicate creates a copy of the selected step and its editable properties
   - Run executes the individual step through Playwright and updates generated code and readiness status
   - Delete removes the step after confirmation
   - Create-from-actions requests possible next actions from the current browser/page state

6. **Bulk Selection Flow**:
   - User Shift-selects multiple steps
   - The selected group can be moved together on the canvas
   - Bottom toolbar appears with the supported multi-step action set
   - The current documented multi-step action is delete

7. **Edge Deletion Flow**:
   - User hovers over a solid edge
   - Delete icon appears on the edge
   - Confirmation dialog opens before `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps-links/:link_id`

8. **Dependency Flow**:
   - User opens the left dependency sidebar
   - User selects pre-pipelines that run before this pipeline and post-pipelines that run after it
   - Connected-pipeline endpoints update prerequisite and follow-up relationships
   - The next publish operation snapshots those relationships into the published version

9. **Publish Flow**:
   - User clicks Publish from the header or versions panel
   - Optional publish note is submitted
   - `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions` serializes the current draft into a new immutable snapshot
   - The new version becomes active and the versions list refreshes

10. **Version Inspection Flow**:
   - User selects a published version from the versions panel
   - `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions/:version_id` loads the snapshot
   - Screen switches to a read-only version view without mutating the current draft

11. **Activate Flow**:
   - User chooses an older published version and clicks Activate
   - `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions/:version_id/activate` updates the active version marker
   - Draft content remains unchanged; only future launches target the newly active version

12. **Pipeline Launch Flow**:
   - User clicks Run in the header
   - UI validates that an active published version exists
   - `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run` creates a run for the active version and queues Playwright execution
   - Frontend redirects to `/qai/projects/:project_id/runs?run_id=...`

13. **Variable Usage Flow**:
   - User opens the variable selector while editing a draft field
   - `GET /api/qai/v1/projects/:project_id/variables` loads available project variables
   - Placeholder syntax such as `{{BASE_URL}}` is inserted into the draft

14. **AI Request Variable Insertion Flow**:
   - User opens the AI preview sidebar from a pipeline-level or step-level AI action
   - User searches existing project variables inside the sidebar request form
   - Selecting a variable inserts placeholder syntax such as `{{BASE_URL}}` into the current prompt or description text
   - This is a frontend-only composition step; the subsequent AI generation request still uses the existing `input.prompt` or `input.description` fields

15. **Draft-level AI Refinement Flow**:
   - User clicks the header AI action to refine existing draft steps, descriptions, or generated code in the current pipeline
   - `POST /api/qai/v1/projects/:project_id/ai/generations` creates a session with `mode = patch_pipeline_draft`
   - Backend enqueues a thin Kafka request and the UI begins polling session status and visible messages
   - When preview is ready, the sidebar loads the latest preview and displays editable changes

16. **Step-level AI Patch Flow**:
   - User clicks `AI improve step` for the selected step
   - The session is created with `mode = patch_step` and the current `step_id`
   - Agent reads the target step, related assertions, pipeline graph context, and existing step HTML snapshot if present
   - The preview may update only the target step and its local assertions or suggested variables
   - Previous steps remain read-only context and are never mutated by the preview

17. **Step-level Append Flow**:
   - User clicks `AI continue after step`
   - The session is created with `mode = append_after_step`
   - Agent may reuse existing HTML from the target step or trigger pipeline/Playwright execution to get current page context
   - Agent generates one or more following steps, links, and assertions
   - The preview automatically includes the first link from the target step to the first generated step

18. **Preview Review / Accept Flow**:
   - User reviews shortened trace, preview warnings, and the generated graph diff
   - User may edit generated steps, links, assertions, and `suggested_variables` before save
   - `PATCH /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id` persists preview edits
   - `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/accept` applies the preview to live draft tables
   - Editor reloads the current draft graph after a successful apply

19. **Reject / Regenerate Flow**:
   - User rejects the current preview or requests another attempt within the same session
   - The current preview becomes `superseded`
   - The newly generated preview becomes `active`
   - Visible trace polling continues from the latest known `after_seq`

### API Interactions:
- Draft metadata load → `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id`
- Draft graph load → `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps`
- Pre/post dependency load → `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines`
- Version history load → `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions`
- Version snapshot load → `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions/:version_id`
- Draft published → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions`
- Version activated → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions/:version_id/activate`
- Draft step created → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps`
- Draft step updated → `PUT /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id`
- Draft step patched → `PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id`
- Draft step deleted → `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id`
- Draft step duplicated → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/duplicate`
- Draft step executed → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/run`
- Draft next actions created → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/create-from-actions`
- Draft link created → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps-links`
- Draft link deleted → `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps-links/:link_id`
- Bulk step positions updated → `PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/bulk-position`
- Bulk steps deleted → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/bulk-delete`
- Assertion created → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/assertions`
- Assertion updated → `PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/assertions/:assertion_id`
- Assertion deleted → `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/assertions/:assertion_id`
- Pipeline options loaded for dependencies → `GET /api/qai/v1/projects/:project_id/pipelines`
- Dependencies updated → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines`
- Dependency removed → `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines/:connected_pipeline_id`
- Run queued → `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run`
- Variables loaded or searched for draft fields and AI request inputs → `GET /api/qai/v1/projects/:project_id/variables`
- Draft-level or step-level AI session created → `POST /api/qai/v1/projects/:project_id/ai/generations`
- Session polled → `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id`
- Messages polled → `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/messages`
- Preview loaded → `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id`
- Preview edited → `PATCH /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id`
- Preview accepted → `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/accept`
- Preview rejected → `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/reject`

### Data Flow:
- Draft state comes from the mutable `pipelines`, `steps`, `assertions`, and `steps_links` records
- Canvas placement and frontend step settings are stored in the step `meta` JSON payload using the `position` and `locked` keys
- Start-step state is graph-derived: a step with no incoming link is rendered as a start step and no separate `meta.is_start` flag is persisted
- The first created step is treated as start by default because it has no incoming links
- New steps may be created with `name`, `description`, and the optional `case` test case description
- Step readiness badge mapping is derived from `status`: `success` is ready, while `redacting` and `failure` are not ready
- Step execution fills or updates `html`, `code`, assertion code, and step `status`
- Step deletion removes connected links and assertions, clears any active selection for that step, and closes the right sidebar if the deleted step was open
- Published state comes from immutable `pipeline_versions` snapshots
- Snapshot inspection never mutates the draft
- Publishing captures draft metadata, graph structure, dependencies, and variable reference metadata using a variable reference manifest without copying secret values
- Launch registration resolves the active published version, queues Playwright execution, and passes that context into the runs history
- AI request variable insertion is frontend-only input composition: the selector inserts placeholders into `input.prompt` or `input.description`, and the backend receives the unchanged AI generation request model
- AI generation context is resolved from the session refs, pipeline graph, variables metadata, and step HTML snapshot or step execution result
- Messages are polled incrementally using `after_seq`, so UI appends only new shortened trace messages without offset drift
- Preview payload is stored separately from draft tables until the user accepts it
- Accept applies the preview through backend domain managers to `pipelines`, `steps`, `steps_links`, and `assertions`
- After accept, the editor reloads the live draft and clears or closes the preview review state

## Screen Contract Decisions

- Start steps are not a separate node type; they are regular `PipelineStep` records without incoming links.
- `case` stores the test case description for the step and is not an action type marker.
- Locked-node state is stored in `meta.locked`.
- Canvas placement is stored in `meta.position`.
- The step readiness badge is a UI mapping over `status`: `success` means ready; `redacting` and `failure` mean not ready.
- Step duplication uses a dedicated duplicate endpoint, copies editable step fields and assertions, does not copy incoming/outgoing links, and offsets `meta.position` for the new node.
- Step execution is synchronous for the prototype: the response returns the updated step after Playwright validation completes.
- Assertion order is creation order; the current screen supports create, update, and delete, but not manual assertion reordering.
- Bulk movement uses one bulk-position endpoint with optimistic UI update and rollback if the API returns validation or persistence errors.
- Bulk deletion uses one bulk-delete endpoint so the UI can confirm once and remove selected steps, connected links, and assertions together.
- Pre/post dependency selection uses the existing pipeline list endpoint as the option source and `connected-pipelines` for persisted relationships.
- AI request variable insertion reuses the existing project variables endpoint and does not add fields to AI generation request or response models.
- Inline LLM-agent actions such as chat and automatic action choice are out of scope for this editor; project-level new-pipeline generation is handled by the Pipelines screen.

## API Endpoints Used
- `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id` - get draft metadata
- `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps` - get draft graph
- `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines` - get pre/post dependencies
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines` - add dependency
- `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines/:connected_pipeline_id` - remove dependency
- `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions` - list published versions
- `GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions/:version_id` - get one immutable version snapshot
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions` - publish the current draft
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions/:version_id/activate` - activate a published version
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps` - create draft step
- `PUT /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id` - update draft step
- `PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id` - patch draft step fields
- `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id` - delete draft step
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/duplicate` - duplicate a draft step
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/run` - execute and validate one draft step
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/create-from-actions` - create possible next steps from current page actions
- `PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/bulk-position` - persist positions for several selected steps
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/bulk-delete` - delete several selected steps together
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps-links` - create draft link
- `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps-links/:link_id` - delete draft link
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/assertions` - create assertion
- `PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/assertions/:assertion_id` - update assertion
- `DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/assertions/:assertion_id` - delete assertion
- `GET /api/qai/v1/projects/:project_id/pipelines` - load pipeline choices for dependency selectors
- `POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run` - create and queue a run for the active version
- `GET /api/qai/v1/projects/:project_id/variables` - fetch project variables for draft field insertion and AI request placeholder insertion
- `POST /api/qai/v1/projects/:project_id/ai/generations` - create AI generation session for draft refinement
- `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id` - get generation status, latest message seq, and latest preview info
- `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/messages` - poll trace messages with `after_seq`
- `GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id` - load one preview artifact
- `PATCH /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id` - edit preview before accept
- `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/accept` - apply preview to the live draft graph
- `POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/reject` - reject the active preview

### Shared API Models
```txt
type ApiError = {
  code: str
  message: str
  details?: json
}

type FlowPosition = {
  x: float
  y: float
}

type StepMeta = {
  position: FlowPosition
  locked: bool
}

type StepMetaUpdate = {
  position?: FlowPosition
  locked?: bool
}

type StepAssertion = {
  id: uuid
  name: str
  description: null | str
  code: json
}

type PipelineStep = {
  id: uuid
  name: str
  description: null | str
  case: str
  html: null | str
  code: json
  meta: StepMeta
  status: enum(redacting, success, failure)
  created_at: datetime
  assertions: StepAssertion[]
}

type StepsLink = {
  id: uuid
  upstream: uuid
  downstream: uuid
}

type StepsGraphResponse = {
  data: PipelineStep[]
  steps_links: StepsLink[]
}

type PipelineDraftDetail = {
  id: uuid
  project_id: uuid
  code: str
  name: str
  description: null | str
  priority: str
  tags: str[]
  status: str
  actuality: str
  steps_count: int
  created_at: datetime
  updated_at: null | datetime
  last_run_at: null | datetime
  last_run_status: null | str
  active_version_id: null | uuid
  active_version_number: null | int
  versions_count: int
  has_unpublished_changes: bool
}

type CreateStepRequest = {
  name: str
  description?: null | str
  case?: str
  meta?: StepMetaUpdate
}

type UpdateStepRequest = {
  name?: str
  description?: null | str
  case?: str
  html?: null | str
  code?: json
  meta?: StepMetaUpdate
  status?: enum(redacting, success, failure)
}

type DeleteStepResponse = {
  deleted_step_id: uuid
  deleted_link_ids: uuid[]
  deleted_assertion_ids: uuid[]
}

type DuplicateStepRequest = {
  position?: FlowPosition
}

type DuplicateStepResponse = {
  step: PipelineStep
}

type StepRunRequest = {
  mode?: enum(validate_and_fill)
}

type StepValidationError = {
  target: enum(step, selector, assertion)
  target_id: null | uuid
  message: str
}

type StepRunResponse = {
  step: PipelineStep
  status: enum(success, failure)
  message: null | str
  validation_errors: StepValidationError[]
}

type CreateFromActionsRequest = {
  max_actions?: int
  include_buttons?: bool
  include_inputs?: bool
}

type CreateFromActionsResponse = {
  source_step_id: uuid
  created_steps: PipelineStep[]
  created_links: StepsLink[]
}

type BulkStepPositionItem = {
  step_id: uuid
  position: FlowPosition
}

type BulkStepPositionRequest = {
  items: BulkStepPositionItem[]
}

type BulkStepPositionResponse = {
  data: PipelineStep[]
}

type BulkDeleteStepsRequest = {
  step_ids: uuid[]
}

type BulkDeleteStepsResponse = {
  deleted_step_ids: uuid[]
  deleted_link_ids: uuid[]
  deleted_assertion_ids: uuid[]
}

type CreateStepsLinkRequest = {
  upstream: uuid
  downstream: uuid
}

type UpdateAssertionRequest = {
  name?: str
  description?: null | str
  code?: json
}

type CreateAssertionRequest = {
  name: str
  description?: null | str
  code?: json
}

type PipelineDependencyType = enum(pre, post)

type ConnectedPipelineItem = {
  id: uuid
  type: PipelineDependencyType
  pipeline_id: uuid
  linked_pipeline_id: uuid
  linked_pipeline_code: str
  linked_pipeline_name: str
}

type ConnectedPipelinesResponse = {
  data: ConnectedPipelineItem[]
}

type CreateConnectedPipelineRequest = {
  type: PipelineDependencyType
  linked_pipeline_id: uuid
}

type PipelineSelectorItem = {
  id: uuid
  code: str
  name: str
  active_version_id: null | uuid
  active_version_number: null | int
}

type PipelineVersionListItem = {
  id: uuid
  version_number: int
  is_active: bool
  publish_note: null | str
  created_at: datetime
}

type PipelineVersionListResponse = {
  data: PipelineVersionListItem[]
}

type PipelineVersionVariableReference = {
  name: str
  secret: bool
}

type PipelineVersionVariableManifest = {
  mode: enum(reference)
  items: PipelineVersionVariableReference[]
}

type PipelineSnapshotMetadata = {
  code: str
  name: str
  description: null | str
  priority: str
  tags: str[]
  status: str
  actuality: str
}

type PipelineSnapshotStep = {
  id: uuid
  name: str
  description: null | str
  case: str
  html: null | str
  code: json
  meta: StepMeta
  status: enum(redacting, success, failure)
}

type PipelineSnapshotAssertion = {
  id: uuid
  step_id: uuid
  name: str
  description: null | str
  code: json
}

type PipelineSnapshotDependency = {
  type: PipelineDependencyType
  linked_pipeline_id: uuid
}

type PipelineVersionSnapshot = {
  pipeline: PipelineSnapshotMetadata
  steps: PipelineSnapshotStep[]
  steps_links: StepsLink[]
  assertions: PipelineSnapshotAssertion[]
  dependencies: PipelineSnapshotDependency[]
  variables: PipelineVersionVariableManifest
}

type PublishPipelineVersionRequest = {
  publish_note?: null | str
}

type PipelineVersionResponse = {
  id: uuid
  pipeline_id: uuid
  version_number: int
  is_active: bool
  publish_note: null | str
  snapshot_schema_version?: int
  created_at: datetime
}

type PipelineVersionSnapshotResponse = {
  id: uuid
  pipeline_id: uuid
  version_number: int
  is_active: bool
  publish_note: null | str
  snapshot_schema_version: int
  created_at: datetime
  snapshot: PipelineVersionSnapshot
}

type LaunchPipelineRunResponse = {
  run_id: uuid
  run_pipeline_id: uuid
  status: enum(queued, running, completed, failed, canceled)
  execution_mode: enum(record_only, playwright)
  pipeline_version_id: uuid
  pipeline_version_number: int
  message: str
  created_at: datetime
}
```

### Shared API Models For Inline AI Refinement
```txt
type AIGenerationSessionStatus = enum(created, queued, running, awaiting_review, accepted, rejected, failed, cancelled)
type AIGenerationMode = enum(patch_pipeline_draft, patch_step, append_after_step)
type AIGenerationTargetScope = enum(pipeline, step)

type AIGenerationMessage = {
  id: uuid
  session_id: uuid
  seq_no: int
  agent_role: enum(user, planner, qai_agent, validator, tool, system)
  stage: enum(input, planning, execution, validation, result, error)
  message_type: enum(text, json, event)
  is_visible_in_ui: bool
  summary_text: null | str
  content_text: null | str
  content_json: null | json
  created_at: datetime
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

type AIPreviewPipelinePatch = {
  schema_version: int
  kind: enum(pipeline_draft_patch, step_patch, step_tail_patch)
  pipeline: {
    pipeline_id: uuid
    name: str
    description: null | str
  }
  steps: {
    temp_id: str
    step_id: null | uuid
    name: str
    description: null | str
    case: null | str
    code: json
  }[]
  steps_links: {
    temp_id: str
    link_id: null | uuid
    upstream_ref: str
    downstream_ref: str
    condition_type: enum(always)
  }[]
  assertions: {
    temp_id: str
    assertion_id: null | uuid
    step_ref: str
    name: str
    description: null | str
    code: json
  }[]
  suggested_variables: {
    name: str
    secret: bool
    description: null | str
  }[]
}

type AIGenerationPreview = {
  id: uuid
  session_id: uuid
  preview_kind: enum(pipeline_draft_patch, step_patch, step_tail_patch)
  status: enum(draft, active, accepted, rejected, superseded)
  normalized_payload: AIPreviewPipelinePatch
  validation_report: {
    is_valid: bool
    warnings: str[]
    fallback_used: bool
  }
  created_at: datetime
  updated_at: datetime
}

type CreateAIGenerationRequest = {
  mode: enum(patch_pipeline_draft, patch_step, append_after_step)
  target_scope: enum(pipeline, step)
  pipeline_id: uuid
  step_id?: null | uuid
  input: {
    prompt?: null | str
    description?: null | str
  }
  options?: {
    preview_only?: bool
    model_profile?: null | str
  }
}

type AIGenerationMessagesResponse = {
  session_id: uuid
  messages: AIGenerationMessage[]
  next_after_seq: int
  has_more: bool
}

type PatchAIPreviewRequest = {
  normalized_payload?: AIPreviewPipelinePatch
}

type AcceptAIPreviewRequest = {
  preview_id: uuid
  apply_mode: enum(patch_pipeline_draft, patch_step, append_after_step)
}

type AcceptAIPreviewResponse = {
  preview_id: uuid
  pipeline_id: uuid
  updated_step_ids: uuid[]
  created_step_ids: uuid[]
  created_link_ids: uuid[]
  created_assertion_ids: uuid[]
  status: enum(draft_updated)
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
- `mode = patch_pipeline_draft` is used from the pipeline header AI action.
- `mode = patch_step` is used for improving only the selected step.
- `mode = append_after_step` is used for generating following steps from the selected step.
- Previous steps are always read-only context and cannot be modified by AI preview on this screen.
- Variable placeholders selected in the sidebar are inserted into the existing `input.prompt` or `input.description` text before this request is sent; no additional request fields are introduced.

### GET /api/qai/v1/projects/:project_id/ai/generations/:session_id
**Response Model:**
```txt
AIGenerationSessionResponse
```

### GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/messages
**Request Query Parameters:**
- `after_seq` (integer, optional): return only messages with `seq_no > after_seq`
- `limit` (integer, optional): page size for incremental polling
- `view` (enum, optional): `ui` for shortened visible trace, `full` for full audit trail

**Response Model:**
```txt
AIGenerationMessagesResponse
```

Notes:
- The editor uses cursor-based polling by `after_seq` and appends only new visible messages.

### GET /api/qai/v1/projects/:project_id/ai/generations/:session_id/previews/:preview_id
**Response Model:**
```txt
AIGenerationPreview
```

Notes:
- The preview payload contains generated steps, `steps_links`, assertions, and `suggested_variables`.

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
- The user may edit generated business content, including `suggested_variables`, before accept.

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
- `patch_step` updates only the target step and its local assertions or suggested variables in the preview scope.
- `append_after_step` creates following steps and automatically persists the first link from the target step.
- Accept changes only the mutable draft and does not publish a version.

### POST /api/qai/v1/projects/:project_id/ai/generations/:session_id/reject
**Response Model:**
```txt
{
  preview_id: uuid
  status: enum(rejected)
  rejected_at: datetime
}
```

Notes:
- Reject keeps the session history for audit and allows the same session to regenerate a new active preview later.

### GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id
**Response Model:**
```txt
PipelineDraftDetail
```

Notes:
- The editor header uses `name`, `code`, `active_version_number`, and `has_unpublished_changes`.
- The launch validation banner uses `active_version_id`.

### GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps
**Response Model:**
```txt
StepsGraphResponse
```

Notes:
- The endpoint returns all steps and links for the selected pipeline without pagination.
- Each step includes its assertions so the canvas can render assertion lists at the bottom of each node.

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps
**Request Body Model:**
```txt
CreateStepRequest
```

**Response Model:**
```txt
PipelineStep
```

Notes:
- In an empty pipeline, the first created step is the default start step.
- A newly created step may contain only `name` and `description` in the request, with `case` filled later from the sidebar.
- `case` is the step test case description.
- When `meta` is omitted, the API stores the current canvas drop position and `locked: false`.

### PUT /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id
**Request Body Model:**
```txt
UpdateStepRequest
```

**Response Model:**
```txt
PipelineStep
```

Notes:
- `PUT` replaces the editable draft-step fields shown in the settings sidebar.
- `meta.locked` is the persisted lock state for canvas movement.

### PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id
**Request Body Model:**
```txt
UpdateStepRequest
```

**Response Model:**
```txt
PipelineStep
```

Notes:
- `PATCH` is used for partial updates such as lock/unlock, individual field edits, status updates, and single-node position changes.

### DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id
**Response Model:**
```txt
DeleteStepResponse
```

Notes:
- Deleting a step also deletes its assertions and connected links.
- If the deleted step is selected, the UI clears that selection and closes the right sidebar.

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/duplicate
**Request Body Model:**
```txt
DuplicateStepRequest
```

**Response Model:**
```txt
DuplicateStepResponse
```

Notes:
- The duplicate copies name, description, test case description (`case`), HTML, code, meta, status, and assertions.
- Incoming and outgoing links are not copied.
- If `position` is omitted, the duplicate is offset from the source step.

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/run
**Request Body Model:**
```txt
StepRunRequest
```

**Response Model:**
```txt
StepRunResponse
```

Notes:
- The prototype treats this as a synchronous Playwright validation action.
- On success, the returned step has `status: success` and updated `html`, `code`, and assertion code as applicable.
- On failure, the returned step has `status: failure` and `validation_errors` explains selector or assertion failures.

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/create-from-actions
**Request Body Model:**
```txt
CreateFromActionsRequest
```

**Response Model:**
```txt
CreateFromActionsResponse
```

Notes:
- The endpoint creates possible next action steps relative to the current page state after the source step.
- Created steps are linked from the source step and returned together with the new links.

### PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/bulk-position
**Request Body Model:**
```txt
BulkStepPositionRequest
```

**Response Model:**
```txt
BulkStepPositionResponse
```

Notes:
- The UI applies optimistic movement to the selected group immediately.
- If the API returns `ApiError`, the UI restores the previous positions.

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/bulk-delete
**Request Body Model:**
```txt
BulkDeleteStepsRequest
```

**Response Model:**
```txt
BulkDeleteStepsResponse
```

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps-links
**Request Body Model:**
```txt
CreateStepsLinkRequest
```

**Response Model:**
```txt
StepsLink
```

Validation notes:
- `downstream` must not already have another incoming link unless it is being reconnected by an explicit operation.
- A start step is a step without incoming links.
- A step may have more than one outgoing link.
- Rejected graph mutations return `ApiError` with codes such as `downstream_has_incoming_link`, `self_link_not_allowed`, `upstream_step_not_found`, or `downstream_step_not_found`.

### DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps-links/:link_id
**Response Model:**
```txt
204 No Content
```

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/assertions
**Request Body Model:**
```txt
CreateAssertionRequest
```

**Response Model:**
```txt
StepAssertion
```

### PATCH /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/assertions/:assertion_id
**Request Body Model:**
```txt
UpdateAssertionRequest
```

**Response Model:**
```txt
StepAssertion
```

Notes:
- Assertion text fields may contain variable placeholders such as `{{BASE_URL}}`.
- Assertion order is creation order; no manual reorder endpoint is part of the current screen contract.

### DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/steps/:step_id/assertions/:assertion_id
**Response Model:**
```txt
204 No Content
```

### GET /api/qai/v1/projects/:project_id/pipelines
Documentation note:
- The dependency sidebar reuses the pipeline list endpoint as its option source.
- The selector consumes the `PipelineSelectorItem` subset from the canonical pipeline list contract in [Pipelines Screen](PipelinesScreen.md).
- The current pipeline and already connected pipelines are filtered out in the selector.

### GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines
**Response Model:**
```txt
ConnectedPipelinesResponse
```

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines
**Request Body Model:**
```txt
CreateConnectedPipelineRequest
```

**Response Model:**
```txt
ConnectedPipelineItem
```

Validation notes:
- `type: pre` writes to `pre_pipelines`.
- `type: post` writes to `post_pipelines`.
- The API rejects connecting the current pipeline to itself and rejects duplicate relationships.

### DELETE /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/connected-pipelines/:connected_pipeline_id
**Response Model:**
```txt
204 No Content
```

### GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions
**Response Model:**
```txt
PipelineVersionListResponse
```

### GET /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions/:version_id
**Response Model:**
```txt
PipelineVersionSnapshotResponse
```

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions
**Request Body Model:**
```txt
PublishPipelineVersionRequest
```

**Response Model:**
```txt
PipelineVersionResponse
```

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/versions/:version_id/activate
**Response Model:**
```txt
PipelineVersionResponse
```

### POST /api/qai/v1/projects/:project_id/pipelines/:pipeline_id/run
**Response Model:**
```txt
LaunchPipelineRunResponse
```

### GET /api/qai/v1/projects/:project_id/variables
Documentation note:
- Variable management is documented on [Project Variables Screen](ProjectVariablesScreen.md).
- This screen uses project variables as insertion options for step, selector, and assertion fields.
- Placeholder syntax inserted into draft fields is `{{VARIABLE_NAME}}`.
- Secret values are not copied into published pipeline version snapshots.
