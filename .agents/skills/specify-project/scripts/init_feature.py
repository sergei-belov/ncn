#!/usr/bin/env python3
"""Initialize and register a feature within its owning service specification."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import unicodedata
from pathlib import Path


TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "feature-template.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an owned service feature contract.")
    parser.add_argument("feature_name", help="Feature name or lowercase kebab-case slug")
    parser.add_argument("--service", required=True, help="Owning service slug")
    parser.add_argument("--docs-root", required=True, type=Path)
    return parser.parse_args()


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        raise ValueError("name must contain an ASCII letter or digit")
    return slug


def add_registry_row(registry: Path, marker: str, heading: str, row: str) -> str:
    original = registry.read_text(encoding="utf-8")
    lines = original.splitlines()
    marker_index = next(
        (index for index, line in enumerate(lines) if line.startswith(marker)), None
    )
    if marker_index is not None:
        lines[marker_index] = row
    else:
        heading_index = next(
            (index for index, line in enumerate(lines) if line == heading), len(lines)
        )
        lines.insert(heading_index, row)
        lines.insert(heading_index + 1, "")
    registry.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return original


def initialize(feature_name: str, service_name: str, docs_root: Path) -> Path:
    docs_root = docs_root.resolve()
    service_slug = slugify(service_name)
    feature_slug = slugify(feature_name)
    service_root = docs_root / "services" / service_slug
    service_registry = service_root / "features" / "README.md"
    project_registry = docs_root / "features" / "README.md"
    if not service_registry.is_file() or not project_registry.is_file():
        raise ValueError("owning service or required feature registries are missing")
    if not TEMPLATE.is_file():
        raise ValueError(f"feature template is missing: {TEMPLATE}")
    destination = service_root / "features" / f"{feature_slug}.md"
    if destination.exists():
        raise FileExistsError(
            f"target already exists; reconcile it manually instead of overwriting: {destination}"
        )

    shutil.copyfile(TEMPLATE, destination)
    display_name = feature_name.strip() or feature_slug
    service_original = project_original = None
    try:
        service_original = add_registry_row(
            service_registry,
            "| <!-- TEMPLATE: feature -->",
            "## Feature Contract Requirements",
            f"| {display_name} | draft | Open | Open | [Feature]({feature_slug}.md) | Open |",
        )
        project_original = add_registry_row(
            project_registry,
            "| FEAT-001 | <!-- TEMPLATE: feature -->",
            "## Registry Rules",
            (
                f"| Open | {display_name} | `{service_slug}` | Open | Open | draft | "
                f"[Feature](../services/{service_slug}/features/{feature_slug}.md) | Open |"
            ),
        )
    except OSError:
        destination.unlink(missing_ok=True)
        if service_original is not None:
            service_registry.write_text(service_original, encoding="utf-8")
        if project_original is not None:
            project_registry.write_text(project_original, encoding="utf-8")
        raise
    return destination


def main() -> int:
    args = parse_args()
    try:
        destination = initialize(args.feature_name, args.service, args.docs_root)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Created and registered owned feature contract: {destination}")
    print("Replace every TEMPLATE marker and propagate effects through affected service docs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
