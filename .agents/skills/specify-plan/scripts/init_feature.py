#!/usr/bin/env python3
"""Initialize a feat-* planning package from the bundled template."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import unicodedata
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR.parent / "assets" / "feature-template"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a non-overwriting feat-{name} feature planning package."
    )
    parser.add_argument("feature_name", help="Feature name or lowercase kebab-case slug")
    parser.add_argument(
        "--path",
        default=Path.cwd(),
        type=Path,
        help="Existing parent directory for the new feat-* folder (default: current directory)",
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        raise ValueError("feature name must contain at least one ASCII letter or digit")
    return slug


def initialize(feature_name: str, plan_root: Path) -> Path:
    plan_root = plan_root.resolve()
    if not plan_root.is_dir():
        raise ValueError(f"plan root does not exist or is not a directory: {plan_root}")
    if not TEMPLATE_DIR.is_dir():
        raise ValueError(f"bundled feature template is missing: {TEMPLATE_DIR}")

    destination = plan_root / f"feat-{slugify(feature_name)}"
    if destination.exists():
        raise FileExistsError(
            f"target already exists; reconcile it manually instead of overwriting: {destination}"
        )

    shutil.copytree(TEMPLATE_DIR, destination)
    return destination


def main() -> int:
    args = parse_args()
    try:
        destination = initialize(args.feature_name, args.path)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Created feature planning package: {destination}")
    print("Replace every <!-- TEMPLATE: ... --> marker, then run validate_feature.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
