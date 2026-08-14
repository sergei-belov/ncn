#!/usr/bin/env python3
"""Smoke-test project/service/feature initialization and spec validation."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
INIT_PROJECT = SCRIPT_DIR / "init_project.py"
INIT_SERVICE = SCRIPT_DIR / "init_service.py"
INIT_FEATURE = SCRIPT_DIR / "init_feature.py"
VALIDATOR = SCRIPT_DIR / "validate_spec.py"
PLACEHOLDER = re.compile(r"<!--\s*TEMPLATE:.*?-->", re.IGNORECASE)


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], check=False, capture_output=True, text=True
    )


def assert_success(result: subprocess.CompletedProcess[str], action: str) -> None:
    if result.returncode != 0:
        raise RuntimeError(f"{action} failed:\n{result.stdout}\n{result.stderr}")


def materialize(docs_root: Path) -> None:
    for path in docs_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        path.write_text(PLACEHOLDER.sub("Specified content.", text), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="specify-project-test-") as temporary:
        root = Path(temporary)
        docs_root = root / "docs"

        assert_success(run(str(INIT_PROJECT), str(docs_root)), "project initialization")
        assert_success(
            run(str(INIT_SERVICE), "Agent Service", "--docs-root", str(docs_root)),
            "agent service initialization",
        )
        assert_success(
            run(str(INIT_SERVICE), "Management Service", "--docs-root", str(docs_root)),
            "management service initialization",
        )
        assert_success(
            run(
                str(INIT_FEATURE), "Agent Core", "--service", "agent-service",
                "--docs-root", str(docs_root),
            ),
            "feature initialization",
        )

        duplicate = run(
            str(INIT_SERVICE), "Agent Service", "--docs-root", str(docs_root)
        )
        if duplicate.returncode == 0 or "already exists" not in duplicate.stderr:
            print("Expected duplicate service initialization to fail safely.")
            print(duplicate.stdout, duplicate.stderr)
            return 1

        materialize(docs_root)
        valid = run(str(VALIDATOR), str(docs_root))
        if valid.returncode != 0:
            print("Expected the materialized service-oriented spec to pass.")
            print(valid.stdout, valid.stderr)
            return 1

        table_contract = docs_root / "services" / "agent-service" / "data" / "tables.md"
        table_contract.unlink()
        missing_table = run(str(VALIDATOR), str(docs_root))
        if missing_table.returncode == 0 or "data/tables.md: missing required file" not in missing_table.stdout:
            print("Expected a missing table contract to fail validation.")
            print(missing_table.stdout, missing_table.stderr)
            return 1

    print("specify-project initialization and validation smoke tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
