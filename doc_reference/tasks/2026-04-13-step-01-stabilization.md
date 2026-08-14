# Step 01 — Stabilization and Navigation Cleanup

## Purpose
Bring the current QAi codebase to a consistent prototype-ready baseline before implementing variables, runs, and versioning.

## Scope of the step
- remove misleading UI actions that do not work end-to-end
- align project navigation around the left sidebar
- move breadcrumbs to the global application header
- stabilize authentication behavior in frontend
- document the temporary placeholder sections honestly

## Implemented decisions
1. **Breadcrumbs moved to `AppHeader`**
   - project pages no longer render local breadcrumbs
   - header builds breadcrumbs from the current route and loads project / pipeline names when needed

2. **Project navigation lives in the left sidebar**
   - sidebar now includes:
     - overview
     - pipelines
     - variables
     - runs
     - settings
   - `flows` route redirects to `runs`

3. **Unimplemented sections are exposed as placeholders**
   - variables, runs, and settings now have dedicated placeholder screens
   - these screens describe in which future step the functionality will appear

4. **Frontend auth stabilized**
   - bearer token is attached on every request
   - login saves the token through `AuthService`
   - logout clears the token cookie
   - guest/protected route guards were added

5. **Misleading pipeline execution logic removed**
   - frontend run actions were removed from current pipeline screens
   - backend `run_pipeline` now responds with explicit `501 Not Implemented`

6. **Broken variable/assertion editing paths disabled**
   - variable selector is temporarily disabled instead of calling missing backend APIs
   - assertion editing was removed because backend supports only create/delete right now

## Result
After this step, QAi is in a more honest and stable state:
- navigation is consistent
- placeholders do not pretend to be implemented features
- project screens no longer call obviously broken flows/settings logic
- frontend authentication behaves predictably
- pipeline editor focuses on the parts that actually work today
