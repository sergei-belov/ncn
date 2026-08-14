# ncn-pms Service Scenarios

## Scenario Inventory

| Scenario | Actor/system | Requirement/feature | Interfaces | Models/tables |
|---|---|---|---|---|
| [SCN-001](#scn-001-manage-project-work) | Admin/member/viewer | PMS-REQ-001..003; FEAT-001 | UX-PMS-001..003; API-PMS-001..006 plus API-AUTHZ-003 | MODEL-PMS-001..005; PMS tables plus TABLE-AUTHZ-001/002 |
| [SCN-002](#scn-002-change-workflow-safely) | Admin | PMS-REQ-004/005 | UX-PMS-004; API-PMS-003/004 | Project/State/WorkItem tables |
| [SCN-003](#scn-003-consume-a-common-authorized-actor) | Authenticated user/admin/member/viewer | PMS-REQ-006..008; FEAT-004 consumer | Existing denied/read-only states; API-PMS-001..007 plus API-AUTHZ-003 | PMS models plus MODEL/TABLE-AUTHZ |

## SCN-001: Manage Project Work

### Actor and Goal

An authorized project user wants to find a project, understand the board, and create or update work at an exact position.

### Preconditions and Permissions

Bearer identity resolves to a persisted user and the user has a matching project relation. The user can view the project; mutations require the corresponding role-derived and backend-enforced action. Archived projects are read-only.

### Trigger

The user opens the project list/board or invokes an equivalent owner API operation.

### Happy Path

1. PMS returns projects or a board snapshot with project, permissions, ordered stages/cards, included epics/members, preferences, and `board_version`.
2. The UI shows loading then populated state and reflects filters in the route.
3. The user creates or edits a work item/epic, or moves a card using drag/drop or the explicit dialog.
4. A move sends target stage, one optional anchor, expected work-item/board versions, and client mutation UUID in JSON.
5. PMS validates scope, permission, dates, relationships, versions, and ordering; commits atomically; returns canonical state.
6. UI replaces optimistic state with owner state and refetches affected queries.

### Alternatives and Edge Cases

Empty project lists/columns/epics show an actionable empty state. Viewer and archived modes omit mutation controls. Direct detail links and mobile use full pages; contextual desktop navigation may use a sheet. Duplicate client IDs return the original semantic result or a stable conflict. Concurrent stale movement/update is rejected. Search/filter/pagination never changes canonical order.

### Failure and Recovery

Validation remains attached to fields; not-found/permission/archive errors show safe messages. A failed optimistic move restores all snapshots, then refetches. Network retry is user-controlled unless the operation is proven idempotent. Unknown owner state is resolved by GET, not by repeating a non-idempotent command.

### Accessibility

All actions have keyboard-reachable semantic controls. Movement has a dialog alternative to drag/drop and announces successful position changes. Dialog/sheet focus is trapped and restored; errors are associated with fields.

### Observable Result

The owner database and refreshed board agree on project scope, card/epic links, order, versions, and permissions. The action outcome is measurable against persisted user identity.

### Traceability

PMS-REQ-001..003/005; PMS-INV-001/002/004..006; FEAT-001; UX-PMS-001..003; API-PMS-001..006; MODEL/TABLE-PMS; service acceptance.

## SCN-002: Change Workflow Safely

### Actor and Goal

A project admin wants to add, edit, reorder, select a default, or delete a stage without losing work.

### Preconditions and Permissions

The project is active, admin action is authorized, and at least one stage exists. Reorder/delete uses the expected board version.

### Trigger

The admin submits stage settings or confirms a delete with a replacement stage.

### Happy Path

1. PMS validates unique name/position, allowed group, project scope, and version.
2. Reorder/default changes are applied atomically and increment relevant versions.
3. For deletion, PMS locks/validates both stages, transfers every work item to the replacement, removes the stage, and updates board version in one transaction.
4. The response returns canonical stages/board version and UI invalidates board/state queries.

### Alternatives and Edge Cases

Default or sole stage deletion is rejected. Replacement cannot equal the deleted stage or belong to another project. A concurrent reorder/delete produces a conflict. A zero-card stage still requires invariant validation.

### Failure and Recovery

Any transaction failure leaves the prior workflow and card assignments intact. UI keeps the dialog open with a stable error and reload option.

### Accessibility

Reorder has keyboard controls; delete confirmation names the stage, impact, and replacement. Focus returns to the stage list after completion/cancellation.

### Observable Result

Exactly one default stage remains, all cards have a valid stage, order is unique, and refreshed board state matches the response.

### Traceability

PMS-REQ-004/005; PMS-INV-001/003/004/006; UX-PMS-004; API-PMS-003/004; MODEL-PMS-002/003; TABLE-PMS-001/003/004.

## SCN-003: Consume a Common Authorized Actor

### Actor and Goal

An externally authenticated or local user wants PMS to list/create projects or access a related project using the common persisted actor and stored role.

### Preconditions and Permissions

The common `ncn-authz` flow has resolved a persisted User. Project-scoped access additionally requires its exact ProjectUser relation and role. Token claims and runtime settings contain no application grants.

### Trigger

The caller requests `/api/v1/auth/me`, a workspace project collection, or any project-scoped route.

### Happy Path

1. `ncn-authz` produces a workspace or project actor from canonical User/ProjectUser state and uses the persisted UUID for common logging/rate identity.
2. The PMS route receives that actor before its manager.
3. The PMS manager rechecks project scope, current relation/action, archive state, and domain references.
4. A list query returns only projects related through the authz relation.
5. Creation by a persisted workspace actor writes the project and creator admin relation through the common authz layer in the same current shared transaction.
6. PMS returns canonical domain state and role-derived permission projections.

### Alternatives and Edge Cases

Identity/local-auth alternatives are owned by SCN-001/003. A viewer receives read-only PMS representations; member/admin capabilities follow common policy plus PMS rules. A relation for another project or workspace does not authorize the path. Concurrent project creation resolves by client project UUID and workspace identifier rules.

### Failure and Recovery

Authn/authz failures come from `ncn-authz` before PMS work. Missing relation or disallowed action returns `403 FORBIDDEN`; callers wait for authorized data change and do not blind retry. Database failure rolls back project bootstrap. Stale PMS writes reload canonical state and resubmit with the current JSON version only when the user chooses.

### Accessibility

No new UI surface is introduced. Existing frontend routes must distinguish authentication failure, permission denial, and read-only state with text, semantic alerts, keyboard-reachable recovery, and focus-preserving navigation. They must not rely on hidden controls as enforcement.

### Observable Result

The authz actor, PMS actor context, role-derived permission projection, and safe PMS log agree on the same persisted user UUID. No token/config grant or custom request metadata changes the result.

### Traceability

PMS-REQ-006..008; PMS-INV-008/009; FEAT-004 consumer; AUTHZ-REQ-001..010; API-AUTHZ-003; PMS API-PMS-001..007; MODEL/TABLE-AUTHZ; PMS domain models/tables.
