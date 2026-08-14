#!/usr/bin/env python3
"""Initialize and register a non-overwriting service specification."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import unicodedata
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "assets" / "service-template"
REGISTRY_PLACEHOLDER = "| <!-- TEMPLATE: service-slug -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create docs/services/<service-slug>.")
    parser.add_argument("service_name", help="Service name or lowercase kebab-case slug")
    parser.add_argument("--docs-root", required=True, type=Path)
    return parser.parse_args()


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        raise ValueError("service name must contain an ASCII letter or digit")
    return slug


def register_service(registry: Path, slug: str) -> None:
    text = registry.read_text(encoding="utf-8")
    row = (
        f"| `{slug}` | Open | Open | Open | Open | Open | planned | "
        f"[Service spec]({slug}/README.md) |"
    )
    lines = text.splitlines()
    placeholder_index = next(
        (index for index, line in enumerate(lines) if line.startswith(REGISTRY_PLACEHOLDER)),
        None,
    )
    if placeholder_index is not None:
        lines[placeholder_index] = row
    else:
        heading_index = next(
            (index for index, line in enumerate(lines) if line == "## Ownership Rules"),
            len(lines),
        )
        lines.insert(heading_index, row)
        lines.insert(heading_index + 1, "")
    registry.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def initialize(service_name: str, docs_root: Path) -> Path:
    docs_root = docs_root.resolve()
    registry = docs_root / "services" / "README.md"
    if not registry.is_file():
        raise ValueError(f"project service registry is missing: {registry}")
    if not TEMPLATE_DIR.is_dir():
        raise ValueError(f"service template is missing: {TEMPLATE_DIR}")
    slug = slugify(service_name)
    destination = docs_root / "services" / slug
    if destination.exists():
        raise FileExistsError(
            f"target already exists; reconcile it manually instead of overwriting: {destination}"
        )
    shutil.copytree(TEMPLATE_DIR, destination)
    try:
        register_service(registry, slug)
    except OSError:
        shutil.rmtree(destination)
        raise
    return destination


def main() -> int:
    args = parse_args()
    try:
        destination = initialize(args.service_name, args.docs_root)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Created and registered service specification: {destination}")
    print("Replace every TEMPLATE marker and update project ownership maps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
