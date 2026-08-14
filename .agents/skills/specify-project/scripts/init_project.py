#!/usr/bin/env python3
"""Initialize a non-overwriting service-oriented project specification."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "assets" / "spec-template"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a project docs baseline.")
    parser.add_argument("docs_root", type=Path, help="Destination docs directory")
    return parser.parse_args()


def initialize(docs_root: Path) -> Path:
    destination = docs_root.resolve()
    if destination.exists():
        raise FileExistsError(
            f"target already exists; reconcile it manually instead of overwriting: {destination}"
        )
    if not destination.parent.is_dir():
        raise ValueError(f"parent directory does not exist: {destination.parent}")
    if not TEMPLATE_DIR.is_dir():
        raise ValueError(f"project template is missing: {TEMPLATE_DIR}")
    shutil.copytree(TEMPLATE_DIR, destination)
    return destination


def main() -> int:
    try:
        destination = initialize(parse_args().docs_root)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Created project specification: {destination}")
    print("Add at least one service, replace all TEMPLATE markers, then validate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
