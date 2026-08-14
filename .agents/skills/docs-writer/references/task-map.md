# Documentation Task Map

For every task, read the applicable project instructions, target document, nearest comparable document, `checklist.md`, and `validation.md`.

## Full Feature or Implementation Documentation

- Complete the initial-task, claim-ledger, and cross-boundary contract matrices; classify every row before finishing.
- Trace behavior from user scenario and UI entry point through frontend state/adapters, backend registration/contracts, persistence, runtime selection, and operational effects.
- Document design and UI/UX at the level needed by the audience; keep shared behavior canonical.
- Reconcile accepted decisions and delivery phases with current behavior. Mark unavailable evidence or out-of-scope layers explicitly instead of silently omitting them.
- Publish or link a compact current/declaration/target summary when accepted decisions or delivery phases exist.
- When frontend/backend interaction is in scope, publish or link a compatibility matrix with separately classified rows for activation; client base; resource path; frontend proxy/gateway prefix; backend application prefix; path-parameter schema/requiredness/meaning; method; authentication; headers; content type; request; response/status; errors; versioning/concurrency; and a compatibility verdict. Use unknown/unestablished rather than mismatch when semantics are not evidenced.
- When browser or backend persistence is in scope, publish or link a persistence-boundary matrix covering store and owner; workspace/user scoping; retention and cleanup; privacy/security; migrations/provisioning; transactions/idempotency; and separate rows for jobs, events, notifications, and other material side effects. Classify each side effect by mock behavior, declaration, backend wiring, execution, operational state, and evidence gap; use an explicit gap or justified not-applicable result rather than omission.

## Documentation Set or Restructure

- Read `structure-and-state.md` and inventory the complete documentation tree before choosing paths.
- Identify product, service, domain, shared, and leaf ownership boundaries; write the intended document map before editing.
- Preserve existing organization unless the user requests a restructure or it cannot represent the requested scope. Do not move a small shared subject into its own document when the established shared overview or inventory remains clear. When restructuring, update every affected index and search for stale paths and duplicated canonical content.
- Validate the full documentation root after adding, removing, or moving files.

## Current-State Audit

- Read `structure-and-state.md` and define whether “current” means the working tree, a commit, a release, or a deployed environment.
- Inspect registration and wiring, not only definitions. Compare both sides of cross-boundary contracts and trace the selected path, configuration, and activation preconditions between them.
- Separate implemented, configured, verified, integrated, deployed, planned, and unknown states.
- State important evidence boundaries and record unresolved conflicts as documentation gaps.

## UI Page or Screen

- Read `page-template.md`, the route/navigation source, shared shell or layout sources, design/UX sources, and canonical API or state docs when available.
- Update page indexes or navigation inventories when adding, removing, or renaming a page.
- Verify routes, shells, visible page structure, responsive variants, states, permissions, actions, links, and API references.
- Keep shared navigation and shell behavior in a canonical shared document when several pages use it; link to that document from each page.

## Database Table

- Read `table-template.md` and the authoritative schema or migration when local rules permit it.
- Update schema indexes or diagrams when the table inventory changes.
- Verify names, types, nullability, defaults, keys, constraints, indexes, and relationships.

## API, Architecture, or Concept

- Read the owning specification or contract and only the implementation needed to verify behavior.
- Compare frontend and backend contracts plus activation and registration before claiming client/server, event, storage, or runtime integration.
- Follow the established local structure; do not force the page or table templates.
- Update cross-references when a public contract, component boundary, or workflow changes.

## README, Guide, or Task Note

- Test commands when safe and practical; otherwise state that they were not run.
- Keep prerequisites, steps, expected results, and limitations explicit.
- Distinguish current behavior from proposals or future work.
