#!/usr/bin/env python3
"""Validate a generated feat-* planning package."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


FEATURE_DIR_PATTERN = re.compile(r"^feat-[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_PATTERN = re.compile(r"<!--\s*TEMPLATE:", re.IGNORECASE)
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)

REQUIRED_HEADINGS: dict[str, tuple[str, ...]] = {
    "README.md": (
        "Status",
        "Start Here",
        "Reading Routes",
        "Document Map",
        "Evidence and Decision Vocabulary",
        "Maintenance Rules",
    ),
    "AGENTS.md": (
        "Required Reading Order",
        "Authority",
        "Scope",
        "Change Propagation",
        "Validation",
    ),
    "feature.md": (
        "Executive Contract",
        "Evidence and Decision Status",
        "Problem and Opportunity",
        "Actors and Permissions",
        "Outcomes and Success Measures",
        "Scope",
        "Requirements",
        "Invariants",
        "State and Lifecycle",
        "Dependencies and Constraints",
        "Security and Privacy",
        "Failure, Recovery, and Observability",
        "Acceptance Criteria",
        "Assumptions",
        "Open Questions",
        "Traceability",
    ),
    "scenarios.md": ("Scenario Inventory",),
    "design/technical.md": (
        "Context and Current State",
        "Proposed Design",
        "Components and Responsibilities",
        "End-to-End Flows",
        "State Ownership and Consistency",
        "Dependencies and Integration",
        "Security Boundaries",
        "Failure Isolation and Recovery",
        "Observability and Operations",
        "Performance and Scale",
        "Rollout and Compatibility",
        "Alternatives",
        "Traceability",
    ),
    "design/ui-ux.md": (
        "Applicability",
        "Experience Goals",
        "Information Architecture",
        "User Flows",
        "Screen and Interaction Inventory",
        "Interaction States",
        "Content and Feedback",
        "Accessibility",
        "Responsive and Platform Behavior",
        "Analytics and Success Signals",
        "Open Design Questions",
        "Traceability",
    ),
    "interfaces/api.md": (
        "Applicability",
        "Ownership and Consumers",
        "Interface Inventory",
        "Authentication and Authorization",
        "Operations",
        "Compatibility and Versioning",
        "Limits and Performance",
        "Observability",
        "Traceability",
    ),
    "data/model.md": (
        "Applicability",
        "Ownership",
        "Entity Inventory",
        "Entities and Fields",
        "Relationships and Constraints",
        "State Transitions",
        "Consistency and Transactions",
        "Retention, Deletion, and Privacy",
        "Access Patterns and Indexing",
        "Migration and Backfill",
        "Audit and Observability",
        "Traceability",
    ),
    "decisions.md": ("Decision Inventory", "Open Decision Queue"),
    "delivery/plan.md": (
        "Delivery Strategy",
        "Dependency Map",
        "Slice Inventory",
        "Cross-Slice Validation",
        "Completion Gate",
    ),
}

REQUIRED_README_TARGETS = tuple(REQUIRED_HEADINGS)
STABLE_ID_CHECKS = {
    "feature.md": re.compile(r"\bREQ-\d{3}\b"),
    "scenarios.md": re.compile(r"^##\s+SCN-\d{3}\s*:", re.MULTILINE),
    "delivery/plan.md": re.compile(r"^##\s+SLICE-\d{3}\s*:", re.MULTILINE),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a feat-* folder's required documents, headings, navigation, "
            "links, reachability, template cleanup, and core stable IDs."
        )
    )
    parser.add_argument("feature_root", type=Path, help="Path to feat-{name}")
    return parser.parse_args()


def readable_markdown(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{path}: cannot read UTF-8 Markdown: {exc}")
        return ""


def without_fenced_code(text: str) -> str:
    visible: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in {"```", "~~~"}:
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is None:
            visible.append(line)
    return "\n".join(visible)


def clean_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    if " " in target:
        return target.split(" ", 1)[0]
    return target


def resolve_local_link(source: Path, raw_target: str) -> Path | None:
    target = clean_link_target(raw_target)
    parsed = urlparse(target)
    if (
        not target
        or target.startswith("#")
        or target.startswith("/")
        or parsed.scheme
        or parsed.netloc
    ):
        return None

    path_part = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not path_part:
        return None
    return (source.parent / path_part).resolve()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def relative_label(path: Path, feature_root: Path) -> str:
    try:
        return path.relative_to(feature_root).as_posix()
    except ValueError:
        return str(path)


def normalized_headings(text: str) -> set[str]:
    return {
        re.sub(r"\s+#+$", "", heading).strip().casefold()
        for heading in HEADING_PATTERN.findall(without_fenced_code(text))
    }


def validate(feature_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    feature_root = feature_root.resolve()

    if not feature_root.is_dir():
        return [f"{feature_root}: feature root does not exist or is not a directory"], warnings

    if not FEATURE_DIR_PATTERN.fullmatch(feature_root.name):
        errors.append(
            f"feature folder must match 'feat-{{name}}' in lowercase kebab-case: {feature_root.name}"
        )

    required_paths = {
        relative: (feature_root / relative).resolve() for relative in REQUIRED_HEADINGS
    }
    for relative, path in required_paths.items():
        if not path.is_file():
            errors.append(f"missing required file: {relative}")

    markdown_files = sorted(feature_root.rglob("*.md"))
    texts: dict[Path, str] = {}
    inbound: dict[Path, set[Path]] = {path.resolve(): set() for path in markdown_files}

    for path in markdown_files:
        resolved_path = path.resolve()
        relative = relative_label(path, feature_root)
        text = readable_markdown(path, errors)
        texts[resolved_path] = text
        visible_text = without_fenced_code(text)

        if not visible_text.strip():
            errors.append(f"{relative}: document has no prose content")
        if PLACEHOLDER_PATTERN.search(visible_text):
            errors.append(f"{relative}: unresolved <!-- TEMPLATE: ... --> marker")

        for match in LINK_PATTERN.finditer(visible_text):
            raw_target = match.group(1)
            linked_path = resolve_local_link(path, raw_target)
            if linked_path is None:
                continue
            if not is_within(linked_path, feature_root):
                errors.append(f"{relative}: local link escapes feature folder: {raw_target!r}")
                continue
            if not linked_path.exists():
                errors.append(f"{relative}: broken link {raw_target!r}")
                continue
            if linked_path.is_dir():
                index_path = (linked_path / "README.md").resolve()
                if index_path in inbound:
                    inbound[index_path].add(resolved_path)
            elif linked_path in inbound:
                inbound[linked_path].add(resolved_path)

    for relative, expected in REQUIRED_HEADINGS.items():
        path = required_paths[relative]
        headings = normalized_headings(texts.get(path, ""))
        for heading in expected:
            if heading.casefold() not in headings:
                errors.append(f"{relative}: missing heading '## {heading}'")

    readme = required_paths["README.md"]
    readme_text = without_fenced_code(texts.get(readme, ""))
    readme_links = {
        resolve_local_link(readme, match.group(1))
        for match in LINK_PATTERN.finditer(readme_text)
    }
    for relative in REQUIRED_README_TARGETS:
        if relative == "README.md":
            continue
        if required_paths[relative] not in readme_links:
            errors.append(f"README.md: must link directly to {relative}")

    agents_text = texts.get(required_paths["AGENTS.md"], "")
    for target in ("README.md", "feature.md", "delivery/plan.md"):
        if target not in agents_text:
            errors.append(f"AGENTS.md: must direct readers to {target}")

    for relative, pattern in STABLE_ID_CHECKS.items():
        text = without_fenced_code(texts.get(required_paths[relative], ""))
        if not pattern.search(text):
            errors.append(f"{relative}: missing required stable ID matching {pattern.pattern!r}")

    for path in markdown_files:
        resolved_path = path.resolve()
        if resolved_path == readme:
            continue
        if not inbound[resolved_path]:
            errors.append(
                f"{relative_label(path, feature_root)}: orphan document; link it from README.md or another document"
            )

    if not markdown_files:
        warnings.append("no Markdown files found")

    return errors, warnings


def main() -> int:
    args = parse_args()
    errors, warnings = validate(args.feature_root)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(f"Feature plan validation failed with {len(errors)} error(s).")
        return 1

    print("Feature plan validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
