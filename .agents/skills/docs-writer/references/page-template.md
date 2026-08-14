# UI Page Documentation Template

Adapt this structure to the project. Omit sections that are irrelevant or already documented canonically.

```md
# [Page name]

Route: `[route]`

Shell: [Shared shell/layout or “Standalone”](relative-link.md)

## Purpose

[One or two sentences describing who uses the page and what they accomplish.]

## Behavior

- [Primary user action and result]
- [Important rule, permission, or transition]

## Page structure

- **[Area]**: [content and placement]
- **[Area]**: [content and placement]

## States and validation

- [Loading, empty, error, disabled, or permission state]
- [Input or business validation visible to the user]

## Data and APIs

| Trigger | Request or source | Result |
| --- | --- | --- |
| [Action] | `[METHOD /path]` | [UI or state update] |

## Related documentation

- [Related page or contract](relative-link.md)
```

Keep the document concise:

- Describe observable behavior, not every component or styling detail.
- Name the shared shell or layout and link to its canonical document. Describe only page-specific structure here.
- Link to canonical API models instead of copying large contracts.
- Add a compact typed request or response model only when the page owns or clarifies that contract.
- Include accessibility, responsive variants, analytics, or optimistic updates only when they materially affect page behavior or structure.
- Verify every route, state, endpoint, and link; mark unknown contracts as documentation gaps.
