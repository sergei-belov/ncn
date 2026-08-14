---
name: backend-review
description: Review backend code in `backend/**` against the repository architecture, templates, and Python style. Use when Codex needs to review newly written or modified backend models, DTOs, repositories, managers, routers, migrations, or related wiring for correctness, missing registrations, API and DB consistency, and code style based on `backend/AGENTS.md`, `backend/templates/`, and `backend/pyproject.toml`.
---

# Backend Reviewer

## Overview

Review backend changes the way this repository expects: compare the changed code to `backend/AGENTS.md`, the matching template, and the nearest existing backend module, then report concrete findings.

## Review Workflow

1. Read `backend/AGENTS.md`, `backend/pyproject.toml`, and `references/review-checklist.md`.
2. Inspect the changed backend files and any linked registration files.
3. Open the matching template under `backend/templates/`.
4. Compare the change to the nearest working module in the same layer.
5. Trace the feature end-to-end before concluding.

## Review Priorities

- Report bugs, regressions, missing wiring, and contract mismatches first.
- Focus on real backend risks:
  missing exports or registrations, missing migration for schema changes, router or manager or db responsibility leaks, async or session misuse, auth or project-scope gaps, API and DTO and SQLAlchemy and enum fields drifting apart, incorrect response models or path params or route prefixes, nullable or default mismatches, and custom repository helper methods that should have been plain `BaseDatabaseGeneric` calls from manager logic.
- Check style after behavior:
  import order, line length `120`, Black or isort or flake8 compatibility, and consistent naming.

## Output Format

- Return findings first, ordered by severity, with file references.
- Keep summaries brief.
- If no findings are discovered, say so explicitly and mention residual risk or missing verification.

## References

- Read `references/review-checklist.md` for the repo-specific review checklist and common misses.
