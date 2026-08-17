#!/usr/bin/env python3
"""Smoke-test initialization and compact feature-plan validation."""

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

    docs_root = plan_root / "docs"
    docs_root.mkdir()
    (docs_root / "README.md").write_text("# Project docs\n", encoding="utf-8")

    destination = plan_root / "feat-search-filters"
    for path in destination.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        path.write_text(PLACEHOLDER_PATTERN.sub("Specified content.", text), encoding="utf-8")

    readme = destination / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8")
        + "\nCurrent contract: [Project docs](../docs/README.md).\n",
        encoding="utf-8",
    )
    return destination


def run_validator(feature_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(feature_root)],
        check=False,
        capture_output=True,
        text=True,
    )


def expect_failure(feature_root: Path, expected: str) -> bool:
    result = run_validator(feature_root)
    if result.returncode != 0 and expected in result.stdout:
        return True
    print(f"Expected validation failure containing {expected!r}.")
    print(result.stdout)
    print(result.stderr)
    return False


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
            print("Expected the materialized compact package to pass validation.")
            print(valid.stdout)
            print(valid.stderr)
            return 1

        readme = valid_root / "README.md"
        original_readme = readme.read_text(encoding="utf-8")
        readme.write_text(
            original_readme.replace("architecture.md", "missing.md"),
            encoding="utf-8",
        )
        if not expect_failure(valid_root, "broken link"):
            return 1

        readme.write_text(original_readme, encoding="utf-8")
        readme.write_text(
            original_readme + "\n<!-- TEMPLATE: unresolved -->\n",
            encoding="utf-8",
        )
        if not expect_failure(valid_root, "unresolved"):
            return 1

        readme.write_text(original_readme, encoding="utf-8")
        implementation = valid_root / "implementation.md"
        original_implementation = implementation.read_text(encoding="utf-8")
        implementation.write_text(
            re.sub(r"^- \[[ xX]\]", "-", original_implementation, flags=re.MULTILINE),
            encoding="utf-8",
        )
        if not expect_failure(valid_root, "checkbox"):
            return 1

        implementation.write_text(original_implementation, encoding="utf-8")
        architecture = valid_root / "architecture.md"
        original_architecture = architecture.read_text(encoding="utf-8")
        architecture.write_text(
            re.sub(
                r"^```.*?^```\s*$",
                "",
                original_architecture,
                flags=re.MULTILINE | re.DOTALL,
            ),
            encoding="utf-8",
        )
        if not expect_failure(valid_root, "fenced architecture or code example"):
            return 1

        architecture.write_text(original_architecture, encoding="utf-8")
        readme.write_text(
            original_readme + "\n[Outside](../../outside.md)\n",
            encoding="utf-8",
        )
        if not expect_failure(valid_root, "escapes package/repository boundaries"):
            return 1

        readme.write_text(original_readme, encoding="utf-8")
        orphan = valid_root / "backend" / "api.md"
        orphan.parent.mkdir()
        orphan.write_text("# Planned API\n", encoding="utf-8")
        if not expect_failure(valid_root, "not reachable from README.md"):
            return 1

        architecture.write_text(
            architecture.read_text(encoding="utf-8")
            + "\nOptional detail: [API plan](backend/api.md).\n",
            encoding="utf-8",
        )
        linked = run_validator(valid_root)
        if linked.returncode != 0:
            print("Expected a linked optional docs-shaped file to pass validation.")
            print(linked.stdout)
            print(linked.stderr)
            return 1

    print("specify-plan script smoke tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
