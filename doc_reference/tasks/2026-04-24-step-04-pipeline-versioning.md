# Step 04 — Pipeline Versioning

## Goal
Turn a mutable pipeline into a versioned test case with an editable draft, immutable published versions, and an explicit active version used for launches.

## Delivery Scope

### Backend
- introduce published versions for project pipelines
- keep the existing pipeline editor route as the draft editor
- define lifecycle rules:
  - draft vs published version
  - immutable version snapshot
  - current active version
- add API for:
  - create version
  - list versions
  - get version
  - make version active
- serialize version snapshots with:
  - pipeline metadata
  - steps
  - links
  - assertions
  - dependencies
  - variable reference manifest
- make launches resolve a concrete published version instead of a floating draft

### Frontend
- add version UI inside existing pipeline-related screens:
  - version list
  - version switch / activate action
  - version metadata view
  - create new version from current draft
- show which published version is used for launch
- keep published versions read-only in UI

### Documentation
- describe test-case lifecycle
- describe the distinction between pipeline draft and pipeline version
- describe edit restrictions for immutable published versions
- update table, screen, and specification docs consistently

## Product Rules
1. **Draft is the only editable representation**
   - `pipelines` remains the mutable project-scoped entity
   - all graph editing continues to happen in the current pipeline editor

2. **Published versions are immutable**
   - once a version is created, its snapshot cannot be edited in place
   - historical versions can be viewed and activated, but not modified

3. **One pipeline has at most one active published version**
   - a pipeline may have zero published versions
   - after the first publish, exactly one version is marked as active

4. **Runs target a published version, not the live draft**
   - run actions from the pipelines list, pipeline editor, and project runs flow must resolve the current active version
   - the resolved version must be persisted explicitly in the run-to-pipeline link record, not only reconstructed in API responses
   - if a pipeline has no published version yet, the run action should be disabled in UI or rejected by API with a clear validation error

5. **Rollback does not overwrite the draft**
   - activating an older version changes what future runs execute
   - the current draft stays untouched and may still contain unpublished changes

6. **Historical runs survive pipeline deletion**
   - deleting or archiving a live pipeline draft must not remove published versions that are already referenced by run history
   - run history must be anchored to `pipeline_version_id`
   - the live `pipeline_id` reference inside run-target links is optional convenience metadata and may become `null` after pipeline deletion

7. **Version snapshots do not copy secret values**
   - step structure is snapshotted
   - variable placeholders remain references
   - secret values are never embedded into a pipeline version snapshot

## Backend Model

### Core entities
- **`pipelines`**: mutable draft head for one test case inside a project
- **`pipeline_versions`**: immutable published snapshots linked to one pipeline
- **`run_pipelines`**: run target links that persist both `pipeline_id` and the exact `pipeline_version_id` used for that launch

### Historical retention rule
Published versions and recorded runs are historical artifacts. The schema should therefore preserve them even if the live pipeline draft is removed from the active project inventory.

- `run_pipelines.pipeline_version_id` is the source of truth for history
- `run_pipelines.pipeline_id` is a nullable pointer to the current live pipeline family
- `pipeline_versions.pipeline_id` may become `null` if the live draft is deleted later

### Snapshot contents
Each published version stores a full immutable snapshot of:

- pipeline metadata:
  - `code`
  - `name`
  - `description`
  - `priority`
  - `tags`
  - `status`
  - `actuality`
- step graph:
  - `steps`
  - `steps_links`
  - `assertions`
- pipeline dependencies:
  - `pre_pipelines`
  - `post_pipelines`
- variable usage metadata:
  - placeholder names used in the draft
  - whether the referenced variable is secret
  - reference mode instead of copied runtime values
- audit metadata:
  - `version_number`
  - `is_active`
  - `publish_note`
  - `snapshot_schema_version`
  - `created_at`
  - `published_by_user_id`

### Variable rule for the prototype
Step 02 introduced project-level variables only. For step 04 the prototype versioning rule is:

- keep placeholders such as `{{BASE_URL}}` and `{{ADMIN_PASSWORD}}` inside the published snapshot
- store variable reference metadata for traceability
- do not duplicate actual variable values into the version payload
- do not duplicate secrets into any version payload

This keeps versioning safe for secrets, but it also means variable value changes can affect future executions of the same published version. Full environment reproducibility is intentionally deferred.

## Planned API Contract

### New versioning endpoints
- `POST /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}/versions` — publish the current draft as a new immutable version
- `GET /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}/versions` — list published versions for one pipeline
- `GET /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}/versions/{version_id}` — get one published version snapshot
- `POST /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}/versions/{version_id}/activate` — make a published version active

### Existing endpoints that should expose version state
- `GET /api/qai/v1/projects/{project_id}/pipelines`
- `GET /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}`
- `POST /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}/run`
- `GET /api/qai/v1/projects/{project_id}/runs`
- `POST /api/qai/v1/projects/{project_id}/runs`

These responses should include enough version state to show:

- active version number
- active version id
- total published versions
- whether the draft has unpublished changes
- which concrete version was resolved for every run target

### Publish example
`POST /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}/versions`

Request:
```json
{
  "publish_note": "Stable login happy path for smoke suite"
}
```

Response:
```json
{
  "id": "8c2b84a9-d0cc-4d8f-a1df-0f0f8d63d224",
  "pipeline_id": "4f7c4d56-0b1a-4e7b-a7e6-7360e5044de4",
  "version_number": 3,
  "is_active": true,
  "publish_note": "Stable login happy path for smoke suite",
  "snapshot_schema_version": 1,
  "created_at": "2026-04-24T10:15:00Z",
  "published_by_user_id": "67f3a4c7-86d6-47d1-a4a0-bdd4c3b2a16f",
  "snapshot": {
    "pipeline": {
      "code": "TC-001",
      "name": "User Login Validation",
      "description": "Happy-path login test case",
      "priority": "high",
      "tags": [
        "smoke",
        "auth"
      ],
      "status": "pending",
      "actuality": "actual"
    },
    "variables": {
      "mode": "reference",
      "items": [
        {
          "name": "BASE_URL",
          "secret": false
        },
        {
          "name": "ADMIN_PASSWORD",
          "secret": true
        }
      ]
    }
  }
}
```

### Versions list example
`GET /api/qai/v1/projects/{project_id}/pipelines/{pipeline_id}/versions`

Response:
```json
{
  "data": [
    {
      "id": "2f6b50f1-ef59-42ab-b586-332e7fe2d2f9",
      "version_number": 1,
      "is_active": false,
      "publish_note": "Initial published draft",
      "created_at": "2026-04-17T13:00:00Z"
    },
    {
      "id": "8c2b84a9-d0cc-4d8f-a1df-0f0f8d63d224",
      "version_number": 3,
      "is_active": true,
      "publish_note": "Stable login happy path for smoke suite",
      "created_at": "2026-04-24T10:15:00Z"
    }
  ]
}
```

## Frontend Scope

### Pipelines list
The pipelines list at `/qai/projects/:project_id/pipelines` should expose version state for each test case:

- active version badge such as `v3`
- draft state badge such as `Draft changed`
- publish action from the current draft
- run action labeled or described with the active version that will be launched
- validation that a pipeline with no published version cannot be launched

### Pipeline editor
The pipeline editor at `/qai/projects/:project_id/pipelines/:pipeline_id` remains the draft editor and gains version-specific UI:

- versions panel, drawer, or tab with published history
- publish action for the current draft
- read-only view for a selected published version snapshot
- activate action for rollback/roll-forward
- indicator showing:
  - current active version
  - whether the draft differs from the active published version

### Project runs
The runs screen at `/qai/projects/:project_id/runs` should show which published version each launch used:

- create-run flow resolves the active version of every selected pipeline
- run details show both pipeline code and version number
- history remains stable even if the active version changes later

## Editing Restrictions
- A published version is always read-only.
- The draft may diverge from the active version.
- Activating an older version does not change draft content.
- Automatic version creation on every draft edit is out of scope for the prototype.
- Branching drafts are out of scope for the prototype.
- Removing a live pipeline draft must not erase published versions or recorded runs.

## Result of the Step
After step 04, a pipeline becomes a proper test case with controlled history:

- editing stays fast in the draft
- publishing creates an immutable checkpoint
- one explicit active version defines what gets launched
- users can inspect history and switch execution back to an older published version without losing current draft work

## Notes for Next Steps
- Step 05 execution should consume the already-persisted `pipeline_version_id` from the run target links so run history never drifts.
- If strict reproducibility becomes a product requirement, variables will need their own versioning or environment snapshot model.
- A future improvement may add diff and restore-to-draft flows, but they are not required for the prototype.
