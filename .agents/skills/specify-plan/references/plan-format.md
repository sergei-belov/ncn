# Compact Feature Plan Format

## Contents

- [Document map](#document-map)
- [README contract](#readme-contract)
- [Architecture contract](#architecture-contract)
- [Optional docs-shaped detail](#optional-docs-shaped-detail)
- [Implementation checklist](#implementation-checklist)
- [Evidence and links](#evidence-and-links)
- [Compactness rules](#compactness-rules)

## Document map

Create this baseline:

```text
feat-{feature-slug}/
├── README.md
├── architecture.md
└── implementation.md
```

The baseline deliberately has no separate scenario, UI/UX, API, data, decision, delivery, or agent-context documents. Put concise feature behavior in `README.md`, implementation design in `architecture.md`, and work sequencing in `implementation.md`.

Add detail only for a material contract that needs independent review. Mirror the repository's canonical documentation hierarchy so readers can compare the plan with current docs:

```text
docs/backend/services/authz/api.md
  -> feat-example/backend/services/authz/api.md

docs/frontend/pages/authz/workspace-access.md
  -> feat-example/frontend/pages/authz/workspace-access.md

docs/database/tables/workspace_users.md
  -> feat-example/database/tables/workspace_users.md
```

Do not reproduce every affected docs file. A checklist entry is enough when the change is mechanical or already specified by the baseline files.

For a legacy package built from separate `feature`, `scenarios`, `design`, `interfaces`, `data`, `decisions`, and `delivery` documents:

- merge unique behavior, requirements, acceptance, decisions, and material questions into `README.md`;
- merge implementation design and still-useful contract detail into `architecture.md` or a justified docs-shaped file;
- convert incomplete delivery work into ordered checkboxes in `implementation.md` and preserve completed state;
- delete superseded documents only after updating all inbound links and confirming that no unique requirement or decision was lost.

## README contract

Make `README.md` the complete entry point. Include:

- **Goal**: one paragraph naming the actor, change, value, and defining boundary.
- **Current behavior**: only facts needed to understand the change, each linked to canonical docs or exact source evidence.
- **Target behavior**: observable behavior, permissions, state changes, errors, recovery, and material non-functional constraints.
- **Scope**: short in-scope and out-of-scope lists.
- **User scenarios**: a few end-to-end examples, not one section per edge case.
- **Requirements**: testable obligations without generated IDs.
- **Acceptance criteria**: observable end states and failure protections.
- **Existing documentation**: canonical current references and whether each must be updated.
- **Plan map**: every plan document and its purpose.
- **Decisions and open questions**: settled choices plus only material unresolved issues; mark blockers plainly.

Keep current and target behavior separate. Do not duplicate architecture or contract detail already owned by another file.

## Architecture contract

Write for implementers and reviewers. Cover only applicable concerns:

1. Existing repository constraints and reusable patterns.
2. Proposed boundaries, ownership, and dependency direction.
3. Important control, data, and state flows.
4. Changed interfaces and persistence effects.
5. Security, authorization, concurrency, failure, and recovery behavior.
6. Observability, compatibility, rollout, and rollback.
7. Validation strategy.

### Pattern examples

Use focused code examples to remove architectural ambiguity. A useful example shows a destination and the intended seam:

````markdown
### Resource port (`frontend/src/entities/example/api/example.resource.ts`)

```ts
export interface ExampleResource {
  list(scope: ScopeId, signal?: AbortSignal): Promise<Example[]>;
  update(command: UpdateExample): Promise<Example>;
}
```
````

The example should demonstrate dependency direction, types, ownership, error behavior, or composition. Do not include complete boilerplate, invent unrelated frameworks, or copy large existing implementations. When a neighboring module is the model, link it and show only the intended delta.

Use Mermaid only when a multi-step or cross-boundary flow is materially clearer as a diagram. A diagram does not replace concrete interface or code examples.

## Optional docs-shaped detail

Match the canonical document's tone and headings where practical, but write the target delta rather than a second full copy of current documentation. Begin with links to:

- the canonical current document;
- relevant architecture section;
- affected source or schema evidence.

Suitable detail documents include an API with multiple operations, a page with several interaction states, a table with a non-trivial migration, or a cross-service flow with independent failure paths.

Do not create a detail document to hold `Not applicable`, one table row, one endpoint, one decision, or material already clear in the baseline.

## Implementation checklist

Use Markdown checkboxes for every implementation task:

```markdown
- [ ] Add the typed resource method in `path/to/port.ts` and both adapters; preserve the mapping described in [Architecture](architecture.md#resource-boundary). Verify with `pnpm test -- resource` and an HTTP fixture covering the error envelope.
```

Checklist rules:

- Order tasks by dependency and keep blockers before dependent work.
- Make each task small enough to complete and verify as one coherent change.
- Name exact verified paths when known; otherwise name the verified parent module and make path discovery the first subtask.
- Include validation in the task or an immediately nested checkbox.
- Preserve `[x]` items when revising an active plan; add new work as `[ ]`.
- Include contract, integration, negative/failure, migration/rollback, accessibility/security when applicable, and canonical docs updates.
- Do not use abstract delivery-slice IDs or repeat full requirements in each task.

## Evidence and links

Use this precedence:

1. the user's current request for target behavior;
2. accepted project documentation and decisions for declared contracts;
3. registered and wired source for current implementation;
4. tests actually run for verified results;
5. clearly named assumptions or open questions.

Link existing Markdown directly rather than citing a bare path. Links may leave the feature folder when they remain inside the repository. Keep source citations as repository-relative paths or local links following repository convention.

Do not call planned behavior current, source presence runnable, a declared schema integrated, or an unrun test passing. Scope negative claims to what was inspected.

## Compactness rules

- Prefer short paragraphs, bullets, compact tables, and focused examples.
- Remove any section that contains no feature-specific information.
- Use one direct link instead of repeating a contract or building an ID graph.
- Avoid inventories whose only purpose is to point at other inventories.
- Split a file only when independent review becomes easier after the split.
- Treat the 150/250/150 baseline line targets and 800-line package target as a review trigger, not permission to compress unreadably.
