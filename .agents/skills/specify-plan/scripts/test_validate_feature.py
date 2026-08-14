#!/usr/bin/env python3
"""Smoke-test validate_feature.py with valid and deliberately invalid packages."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
INITIALIZER = SCRIPT_DIR / "init_feature.py"
VALIDATOR = SCRIPT_DIR / "validate_feature.py"
PLACEHOLDER_PATTERN = re.compile(r"<!--\s*TEMPLATE:.*?-->", re.IGNORECASE)


def materialize_feature(plan_root: Path) -> Path:
    initialized = subprocess.run(
        [sys.executable, str(INITIALIZER), "Search Filters", "--path", str(plan_root)],
        check=False,
        capture_output=True,
        text=True,
    )
    if initialized.returncode != 0:
        raise RuntimeError(initialized.stderr or initialized.stdout)

    destination = plan_root / "feat-search-filters"
    for path in destination.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        path.write_text(PLACEHOLDER_PATTERN.sub("Specified content.", text), encoding="utf-8")
    return destination


def run_validator(feature_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(feature_root)],
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="specify-plan-test-") as temporary:
        temporary_root = Path(temporary)
        valid_root = materialize_feature(temporary_root)

        duplicate = subprocess.run(
            [
                sys.executable,
                str(INITIALIZER),
                "Search Filters",
                "--path",
                str(temporary_root),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if duplicate.returncode == 0 or "already exists" not in duplicate.stderr:
            print("Expected the initializer to refuse an existing feature package.")
            print(duplicate.stdout)
            print(duplicate.stderr)
            return 1

        valid = run_validator(valid_root)
        if valid.returncode != 0:
            print("Expected the materialized feature package to pass validation.")
            print(valid.stdout)
            print(valid.stderr)
            return 1

        readme = valid_root / "README.md"
        original_readme = readme.read_text(encoding="utf-8")
        readme.write_text(
            original_readme.replace("design/technical.md", "design/missing.md"),
            encoding="utf-8",
        )
        broken = run_validator(valid_root)
        if broken.returncode == 0 or "broken link" not in broken.stdout:
            print("Expected a broken README link to fail validation.")
            print(broken.stdout)
            print(broken.stderr)
            return 1

        readme.write_text(original_readme, encoding="utf-8")
        unresolved = valid_root / "feature.md"
        unresolved.write_text(
            unresolved.read_text(encoding="utf-8") + "\n<!-- TEMPLATE: unresolved -->\n",
            encoding="utf-8",
        )
        placeholder = run_validator(valid_root)
        if placeholder.returncode == 0 or "unresolved" not in placeholder.stdout:
            print("Expected an unresolved template marker to fail validation.")
            print(placeholder.stdout)
            print(placeholder.stderr)
            return 1

    print("validate_feature.py smoke tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
