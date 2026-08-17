#!/usr/bin/env python3
"""Validate a compact feat-* implementation-planning package."""

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
CHECKBOX_PATTERN = re.compile(r"^\s*-\s+\[(?: |x|X)\]\s+\S", re.MULTILINE)
CODE_FENCE_PATTERN = re.compile(r"^\s*(?:```|~~~)", re.MULTILINE)
LEGACY_ID_PATTERN = re.compile(r"\b(?:REQ|SCN|UX|API|DATA|DEC|SLICE)-\d{3}\b")

REQUIRED_HEADINGS: dict[str, tuple[str, ...]] = {
    "README.md": (
        "Goal",
        "Current behavior",
        "Target behavior",
        "Scope",
        "User scenarios",
        "Requirements",
        "Acceptance criteria",
        "Existing documentation",
        "Plan map",
        "Decisions and open questions",
    ),
    "architecture.md": (
        "Existing constraints",
        "Proposed design",
        "Boundaries and flow",
        "Implementation patterns",
        "Contracts and data",
        "Security, failure handling, and observability",
        "Rollout and rollback",
        "Validation approach",
    ),
    "implementation.md": ("Checklist", "Completion criteria"),
}

REQUIRED_README_TARGETS = ("architecture.md", "implementation.md")
LINE_TARGETS = {
    "README.md": 150,
    "architecture.md": 250,
    "implementation.md": 150,
}
PACKAGE_LINE_TARGET = 800


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a feat-* folder's compact baseline, headings, checklist, "
            "repository-local links, reachability, and template cleanup."
        )
    )
    parser.add_argument("feature_root", type=Path, help="Path to feat-{name}")
    parser.add_argument(
        "--repository-root",
        type=Path,
        help="Repository boundary for project links (default: nearest .git ancestor or plan root)",
    )
    return parser.parse_args()


def discover_repository_root(feature_root: Path) -> Path:
    for candidate in (feature_root, *feature_root.parents):
        if (candidate / ".git").exists():
            return candidate
    return feature_root.parent


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


def reachable_from(start: Path, adjacency: dict[Path, set[Path]]) -> set[Path]:
    visited: set[Path] = set()
    pending = [start]
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        pending.extend(adjacency.get(current, set()) - visited)
    return visited


def validate(
    feature_root: Path, repository_root: Path | None = None
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    feature_root = feature_root.resolve()

    if not feature_root.is_dir():
        return [f"{feature_root}: feature root does not exist or is not a directory"], warnings

    if not FEATURE_DIR_PATTERN.fullmatch(feature_root.name):
        errors.append(
            f"feature folder must match 'feat-{{name}}' in lowercase kebab-case: {feature_root.name}"
        )

    repository_root = (
        repository_root.resolve()
        if repository_root is not None
        else discover_repository_root(feature_root)
    )
    if not repository_root.is_dir():
        errors.append(f"repository root does not exist or is not a directory: {repository_root}")

    required_paths = {
        relative: (feature_root / relative).resolve() for relative in REQUIRED_HEADINGS
    }
    for relative, path in required_paths.items():
        if not path.is_file():
            errors.append(f"missing required file: {relative}")

    markdown_files = sorted(feature_root.rglob("*.md"))
    resolved_markdown = {path.resolve() for path in markdown_files}
    texts: dict[Path, str] = {}
    adjacency: dict[Path, set[Path]] = {path: set() for path in resolved_markdown}

    for path in markdown_files:
        resolved_path = path.resolve()
        relative = relative_label(path, feature_root)
        text = readable_markdown(path, errors)
        texts[resolved_path] = text
        visible_text = without_fenced_code(text)

        if not visible_text.strip():
            errors.append(f"{relative}: document has no prose content")
        if PLACEHOLDER_PATTERN.search(text):
            errors.append(f"{relative}: unresolved <!-- TEMPLATE: ... --> marker")

        for match in LINK_PATTERN.finditer(visible_text):
            raw_target = match.group(1)
            linked_path = resolve_local_link(path, raw_target)
            if linked_path is None:
                continue
            if not (
                is_within(linked_path, feature_root)
                or is_within(linked_path, repository_root)
            ):
                errors.append(
                    f"{relative}: local link escapes package/repository boundaries: {raw_target!r}"
                )
                continue
            if not linked_path.exists():
                errors.append(f"{relative}: broken link {raw_target!r}")
                continue

            graph_target = linked_path
            if linked_path.is_dir():
                graph_target = (linked_path / "README.md").resolve()
            if graph_target in resolved_markdown:
                adjacency[resolved_path].add(graph_target)

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
        if required_paths[relative] not in readme_links:
            errors.append(f"README.md: must link directly to {relative}")

    architecture_text = texts.get(required_paths["architecture.md"], "")
    if len(CODE_FENCE_PATTERN.findall(architecture_text)) < 2:
        errors.append("architecture.md: include at least one fenced architecture or code example")

    implementation_text = without_fenced_code(
        texts.get(required_paths["implementation.md"], "")
    )
    if not CHECKBOX_PATTERN.search(implementation_text):
        errors.append("implementation.md: include at least one Markdown checkbox task")

    reachable = reachable_from(readme, adjacency)
    for path in markdown_files:
        resolved_path = path.resolve()
        if resolved_path not in reachable:
            errors.append(
                f"{relative_label(path, feature_root)}: document is not reachable from README.md"
            )

    package_lines = sum(len(text.splitlines()) for text in texts.values())
    if package_lines > PACKAGE_LINE_TARGET:
        warnings.append(
            f"package has {package_lines} lines; compact or justify exceeding the {PACKAGE_LINE_TARGET}-line target"
        )
    for relative, target in LINE_TARGETS.items():
        count = len(texts.get(required_paths[relative], "").splitlines())
        if count > target:
            warnings.append(
                f"{relative}: {count} lines exceeds the default {target}-line target"
            )

    legacy_ids = sorted(
        {
            identifier
            for text in texts.values()
            for identifier in LEGACY_ID_PATTERN.findall(without_fenced_code(text))
        }
    )
    if legacy_ids:
        warnings.append(
            "synthetic cross-document IDs found; prefer direct links and headings: "
            + ", ".join(legacy_ids)
        )

    if not markdown_files:
        warnings.append("no Markdown files found")

    return errors, warnings


def main() -> int:
    args = parse_args()
    errors, warnings = validate(args.feature_root, args.repository_root)

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
