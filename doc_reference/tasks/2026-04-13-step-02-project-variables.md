# Step 02 — Project Variables

## Goal
Add a real project-level variables module to QAi so variables can be managed from the left sidebar and inserted into pipeline steps using a stable `{{VARIABLE_NAME}}` placeholder format.

## Scope
This step intentionally does **not** add migrations. It uses the existing `variables` table and stores typed values inside the current JSON payload.

## Delivery Summary
1. **Backend CRUD for project variables**
   - Added dedicated router, manager, repository, API models, and enums.
   - Endpoints now exist under `/v1/projects/{project_id}/variables`.
   - Supported public types:
     - `string`
     - `number`
     - `integer`
     - `secret`

2. **Typed value contract without schema changes**
   - Variables are persisted in the existing `value JSON` column as:
     ```json
     {
       "type": "string",
       "value": "https://example.com"
     }
     ```
   - The legacy `secret` boolean continues to mark masked values.

3. **Uniqueness and validation**
   - Variable names are unique inside one project.
   - Names follow a gitlab-like key format:
     - Latin letters
     - digits
     - underscore
     - must not start with a digit

4. **Frontend variables screen**
   - Replaced the placeholder `/qai/projects/:project_id/variables` screen with a real management page.
   - Added list/search/create/edit/delete flows.
   - Secret values are masked after save.
   - Placeholder preview and copy action are available for each variable.

5. **Pipeline editor integration**
   - `VariableSelector` now loads project variables and inserts placeholders into step fields.
   - Current insertion format: `{{VARIABLE_NAME}}`.
   - This step adds authoring support only. Runtime execution/resolution will be finalized in later execution-related steps.

## Key Technical Decisions
- **Scope**: variables are project-level only.
- **Secrets**: stored through the current DB model; masked in the frontend and omitted from API value payloads after save.
- **Execution semantics**: placeholders are authored now, resolved later when the real run/executor domain is implemented.

## Updated Navigation
Project navigation in the left sidebar now contains a real Variables section:
- Overview
- Pipelines
- Variables
- Runs
- Settings

## Files Added
- `backend/models/enum/variable.py`
- `backend/models/pydantic/api/variable_api.py`
- `backend/api/db/variables.py`
- `backend/api/managers/variables.py`
- `backend/api/router/variables.py`
- `frontend/src/views/ProjectVariablesView.vue`
- `docs/platform/ui/pages/ProjectVariablesScreen.md`

## Files Updated
- `backend/models/enum/__init__.py`
- `backend/models/pydantic/__init__.py`
- `backend/api/db/db.py`
- `backend/api/managers/managers.py`
- `backend/api/router/router.py`
- `frontend/src/services/VariableService.js`
- `frontend/src/components/VariableSelector.vue`
- `frontend/src/views/ProjectDetailView.vue`
- `frontend/src/router/index.ts`
- `docs/platform/tables/variables.md`
- `docs/platform/ui/pages/project_navigation.md`
- `frontend/spec.md`

## Notes for Next Steps
- Pipeline versioning should snapshot or reference project variables explicitly.
- Runs/executions should resolve `{{VARIABLE_NAME}}` placeholders against the project variable set at execution time.
- Secrets should eventually move to a stronger storage model if the prototype evolves beyond internal/demo use.
