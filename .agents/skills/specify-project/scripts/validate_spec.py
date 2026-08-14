#!/usr/bin/env python3
"""Validate a service-oriented living project specification."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_PATTERN = re.compile(r"<!--\s*TEMPLATE:", re.IGNORECASE)
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)

PROJECT_HEADINGS: dict[str, tuple[str, ...]] = {
    "README.md": (
        "Start Here", "Reading Routes", "Sources of Truth", "Status Vocabulary",
        "Maintenance Rules",
    ),
    "AGENTS.md": (
        "Required Reading", "Authority", "Service Ownership", "Evidence Boundary",
        "Maintenance", "Validation",
    ),
    "spec.md": (
        "Executive Contract", "Evidence and Decision Status", "Problem and Audience",
        "Outcomes and Success Measures", "Scope", "Actors and Permissions",
        "Core Journeys", "Capability and Service Inventory", "Requirements", "Invariants",
        "Quality Requirements", "Dependencies and Constraints", "Assumptions",
        "Open Questions", "Project Acceptance", "Traceability",
    ),
    "project-map.md": (
        "Snapshot", "Reading Routes", "Documentation Map", "Service Ownership Map",
        "Runtime Entry Points", "Change Impact Map", "Known Gaps",
    ),
    "product/overview.md": (
        "Problem", "Audience", "Value Proposition", "Primary Use Cases",
        "Product Boundaries and Measures",
    ),
    "product/glossary.md": ("Naming Rules",),
    "architecture/system.md": (
        "Context", "Service Boundaries", "Cross-Service Flows",
        "Data and Consistency Boundaries", "Shared Infrastructure and Integrations",
        "Security and Trust Boundaries", "Failure Isolation and Recovery",
        "Observability and Operations", "Runtime and Deployment Shape",
        "Architecture Decisions",
    ),
    "services/README.md": ("Ownership Rules", "Dependency Rules"),
    "features/README.md": ("Registry Rules",),
    "interfaces/README.md": ("Shared Conventions", "Interaction Inventory"),
    "data/README.md": ("Ownership Inventory", "Cross-Service Data Rules"),
    "decisions/README.md": ("Decision Inventory", "Open Decision Queue"),
}

SERVICE_HEADINGS: dict[str, tuple[str, ...]] = {
    "README.md": (
        "Status", "Responsibility", "Start Here", "Reading Routes", "Document Map",
        "Maintenance Rules",
    ),
    "spec.md": (
        "Executive Contract", "Evidence and Status", "Responsibility and Ownership",
        "Actors, Systems, and Permissions", "Feature Inventory", "Requirements",
        "Invariants", "State and Lifecycle", "Dependencies and Constraints",
        "Security and Privacy", "Failure, Recovery, and Observability",
        "Quality Requirements", "Assumptions", "Open Questions", "Service Acceptance",
        "Traceability",
    ),
    "scenarios.md": ("Scenario Inventory",),
    "features/README.md": ("Feature Contract Requirements",),
    "design/technical.md": (
        "Context and Status", "Components and Responsibilities", "End-to-End Flows",
        "State Ownership and Consistency", "Dependencies and Integrations",
        "Security Boundaries", "Failure Isolation and Recovery",
        "Observability and Operations", "Performance and Scale",
        "Runtime, Compatibility, and Evolution", "Alternatives", "Traceability",
    ),
    "design/ui-ux.md": (
        "Applicability", "Experience Goals", "Information Architecture", "User Flows",
        "Screen and Interaction Inventory", "Interaction States", "Content and Feedback",
        "Accessibility", "Responsive and Platform Behavior", "Analytics and Success Signals",
        "Open Design Questions", "Traceability",
    ),
    "interfaces/api.md": (
        "Applicability", "Ownership and Consumers", "Shared Conventions",
        "Operation Inventory", "Compatibility and Versioning", "Limits and Performance",
        "Observability", "Traceability",
    ),
    "interfaces/events.md": ("Applicability", "Event Inventory", "Traceability"),
    "data/models.md": (
        "Applicability and Ownership", "Model Inventory", "Traceability",
    ),
    "data/tables.md": (
        "Applicability and Database Status", "Table Inventory", "Cross-Table Rules",
        "Traceability",
    ),
    "decisions.md": ("Decision Inventory", "Open Decision Queue"),
}

FEATURE_HEADINGS = (
    "Status", "Problem and Goal", "Actors and Permissions", "Scope",
    "Requirements and Invariants", "Scenarios and Contract Effects",
    "Failure, Recovery, and Observability", "Acceptance Criteria",
    "Assumptions and Open Questions", "Traceability",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate project and per-service spec structure, headings, links, registries, "
            "reachability, template cleanup, and core identifiers."
        )
    )
    parser.add_argument("docs_root", nargs="?", default="docs", type=Path)
    return parser.parse_args()


def without_fenced_code(text: str) -> str:
    visible: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        marker = line.lstrip()[:3]
        if marker in {"```", "~~~"}:
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is None:
            visible.append(line)
    return "\n".join(visible)


def normalized_headings(text: str) -> set[str]:
    return {
        re.sub(r"\s+#+$", "", heading).strip().casefold()
        for heading in HEADING_PATTERN.findall(without_fenced_code(text))
    }


def clean_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    if " " in target:
        target = target.split(" ", 1)[0]
    return target


def resolve_local_link(source: Path, raw_target: str) -> Path | None:
    target = clean_link_target(raw_target)
    parsed = urlparse(target)
    if not target or target.startswith("#") or target.startswith("/") or parsed.scheme or parsed.netloc:
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


def label(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{path}: cannot read UTF-8 Markdown: {exc}")
        return ""


def direct_links(source: Path, text: str) -> set[Path]:
    return {
        linked
        for match in LINK_PATTERN.finditer(without_fenced_code(text))
        if (linked := resolve_local_link(source, match.group(1))) is not None
    }


def require_documents(
    root: Path,
    required: dict[str, tuple[str, ...]],
    texts: dict[Path, str],
    errors: list[str],
    docs_root: Path,
) -> None:
    for relative, headings in required.items():
        path = (root / relative).resolve()
        if not path.is_file():
            errors.append(f"{label(path, docs_root)}: missing required file")
            continue
        available = normalized_headings(texts.get(path, ""))
        for heading in headings:
            if heading.casefold() not in available:
                errors.append(f"{label(path, docs_root)}: missing heading '## {heading}'")


def validate(docs_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    docs_root = docs_root.resolve()
    if not docs_root.is_dir():
        return [f"{docs_root}: docs root does not exist or is not a directory"], warnings

    markdown_files = sorted(docs_root.rglob("*.md"))
    texts: dict[Path, str] = {}
    inbound: dict[Path, set[Path]] = {path.resolve(): set() for path in markdown_files}

    for path in markdown_files:
        resolved = path.resolve()
        text = read_text(path, errors)
        texts[resolved] = text
        visible = without_fenced_code(text)
        if not visible.strip():
            errors.append(f"{label(path, docs_root)}: document has no prose content")
        if PLACEHOLDER_PATTERN.search(visible):
            errors.append(f"{label(path, docs_root)}: unresolved <!-- TEMPLATE: ... --> marker")
        for match in LINK_PATTERN.finditer(visible):
            raw_target = match.group(1)
            linked = resolve_local_link(path, raw_target)
            if linked is None:
                continue
            if not is_within(linked, docs_root):
                errors.append(f"{label(path, docs_root)}: local link escapes docs root: {raw_target!r}")
                continue
            if not linked.exists():
                errors.append(f"{label(path, docs_root)}: broken link {raw_target!r}")
                continue
            if linked.is_dir():
                linked = (linked / "README.md").resolve()
            if linked in inbound:
                inbound[linked].add(resolved)

    require_documents(docs_root, PROJECT_HEADINGS, texts, errors, docs_root)

    project_spec = (docs_root / "spec.md").resolve()
    if project_spec.is_file() and not re.search(r"\bREQ-\d{3}\b", texts.get(project_spec, "")):
        errors.append("spec.md: missing project requirement ID matching REQ-NNN")

    services_root = docs_root / "services"
    service_roots = sorted(
        path for path in services_root.iterdir() if path.is_dir()
    ) if services_root.is_dir() else []
    if not service_roots:
        errors.append("services/: at least one service specification folder is required")

    service_index = (services_root / "README.md").resolve()
    service_index_links = direct_links(service_index, texts.get(service_index, ""))
    project_feature_index = (docs_root / "features" / "README.md").resolve()
    project_feature_links = direct_links(project_feature_index, texts.get(project_feature_index, ""))

    service_feature_docs: list[Path] = []
    for service_root in service_roots:
        if not SLUG_PATTERN.fullmatch(service_root.name):
            errors.append(f"services/{service_root.name}: service folder must be lowercase kebab-case")
        require_documents(service_root, SERVICE_HEADINGS, texts, errors, docs_root)

        service_readme = (service_root / "README.md").resolve()
        if service_readme not in service_index_links:
            errors.append(f"services/README.md: must link directly to {service_root.name}/README.md")

        service_spec = (service_root / "spec.md").resolve()
        if service_spec.is_file() and not re.search(r"\bREQ-\d{3}\b", texts.get(service_spec, "")):
            errors.append(f"{label(service_spec, docs_root)}: missing service requirement ID matching REQ-NNN")
        scenarios = (service_root / "scenarios.md").resolve()
        if scenarios.is_file() and not re.search(r"^##\s+SCN-\d{3}\s*:", texts.get(scenarios, ""), re.MULTILINE):
            errors.append(f"{label(scenarios, docs_root)}: missing scenario heading matching SCN-NNN")

        readme_links = direct_links(service_readme, texts.get(service_readme, ""))
        for relative in SERVICE_HEADINGS:
            target = (service_root / relative).resolve()
            if relative != "README.md" and target not in readme_links:
                errors.append(
                    f"{label(service_readme, docs_root)}: must link directly to {relative}"
                )

        feature_index = (service_root / "features" / "README.md").resolve()
        feature_index_links = direct_links(feature_index, texts.get(feature_index, ""))
        feature_docs = sorted(
            path.resolve()
            for path in (service_root / "features").glob("*.md")
            if path.name != "README.md"
        ) if (service_root / "features").is_dir() else []
        for feature in feature_docs:
            if not SLUG_PATTERN.fullmatch(feature.stem):
                errors.append(f"{label(feature, docs_root)}: feature file must be lowercase kebab-case")
            headings = normalized_headings(texts.get(feature, ""))
            for heading in FEATURE_HEADINGS:
                if heading.casefold() not in headings:
                    errors.append(f"{label(feature, docs_root)}: missing heading '## {heading}'")
            if not re.search(r"\bREQ-\d{3}\b", texts.get(feature, "")):
                errors.append(f"{label(feature, docs_root)}: missing feature requirement ID matching REQ-NNN")
            if feature not in feature_index_links:
                errors.append(f"{label(feature_index, docs_root)}: must link to {feature.name}")
            if feature not in project_feature_links:
                errors.append(
                    f"features/README.md: must link to owning feature {label(feature, docs_root)}"
                )
            service_feature_docs.append(feature)

    reachability_exempt = {
        (docs_root / "README.md").resolve(),
        (docs_root / "AGENTS.md").resolve(),
        (docs_root / "spec.md").resolve(),
        (docs_root / "project-map.md").resolve(),
    }
    for path in markdown_files:
        resolved = path.resolve()
        if resolved in reachability_exempt:
            continue
        if not inbound[resolved]:
            errors.append(f"{label(path, docs_root)}: orphan document; link it from a README or contract")

    if not service_feature_docs:
        warnings.append("no service feature documents found; registries may describe a baseline only")
    return errors, warnings


def main() -> int:
    errors, warnings = validate(parse_args().docs_root)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"Specification validation failed with {len(errors)} error(s).")
        return 1
    print("Service-oriented project specification validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
