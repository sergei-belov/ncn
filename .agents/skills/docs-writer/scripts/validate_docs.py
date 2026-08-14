#!/usr/bin/env python3
"""Validate Markdown fences and relative local links without dependencies."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


MARKDOWN_SUFFIXES = {".md", ".mdx"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
HTML_ID_RE = re.compile(r'''\bid=["']([^"']+)["']''')
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Markdown fences and relative local links."
    )
    parser.add_argument("paths", nargs="+", help="Markdown files or directories")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used for display paths (default: current directory)",
    )
    return parser.parse_args()


def collect_files(paths: list[str]) -> tuple[list[Path], list[str]]:
    files: set[Path] = set()
    errors: list[str] = []
    for raw_path in paths:
        path = Path(raw_path).resolve()
        if not path.exists():
            errors.append(f"{raw_path}: input does not exist")
        elif path.is_dir():
            files.update(
                child.resolve()
                for child in path.rglob("*")
                if child.is_file() and child.suffix.lower() in MARKDOWN_SUFFIXES
            )
        elif path.suffix.lower() in MARKDOWN_SUFFIXES:
            files.add(path)
        else:
            errors.append(f"{raw_path}: input is not a Markdown file or directory")
    if not files and not errors:
        errors.append("no Markdown files found")
    return sorted(files), errors


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def slugify(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[`*_~]", "", value).strip().lower()
    value = re.sub(r"[^\w\- ]", "", value)
    return re.sub(r"\s+", "-", value)


def anchors_for(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            base = slugify(heading.group(1))
            number = counts.get(base, 0)
            counts[base] = number + 1
            anchors.add(base if number == 0 else f"{base}-{number}")
        anchors.update(HTML_ID_RE.findall(line))
    return anchors


def link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split(maxsplit=1)[0] if target else ""


def validate_file(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    fence: tuple[str, int] | None = None

    for line_number, line in enumerate(lines, start=1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = (marker[0], line_number)
            elif marker[0] == fence[0]:
                fence = None
            continue
        if fence is not None:
            continue

        for match in LINK_RE.finditer(line):
            target = link_target(match.group(1))
            if not target or target.startswith("#"):
                if target.startswith("#") and target[1:] not in anchors_for(path):
                    errors.append(
                        f"{display_path(path, root)}:{line_number}: "
                        f"missing anchor {target}"
                    )
                continue

            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith("/"):
                continue

            target_path = (path.parent / unquote(parsed.path)).resolve()
            if not target_path.exists():
                errors.append(
                    f"{display_path(path, root)}:{line_number}: "
                    f"missing local link target {target}"
                )
                continue

            if parsed.fragment and target_path.suffix.lower() in MARKDOWN_SUFFIXES:
                anchor = unquote(parsed.fragment)
                if anchor not in anchors_for(target_path):
                    errors.append(
                        f"{display_path(path, root)}:{line_number}: "
                        f"missing anchor #{anchor} in {display_path(target_path, root)}"
                    )

    if fence is not None:
        errors.append(
            f"{display_path(path, root)}:{fence[1]}: unclosed {fence[0] * 3} fence"
        )
    return errors


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    files, errors = collect_files(args.paths)
    for path in files:
        try:
            errors.extend(validate_file(path, root))
        except UnicodeDecodeError:
            errors.append(f"{display_path(path, root)}: file is not valid UTF-8")

    if errors:
        print("Documentation validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} Markdown file(s): fences and local links are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
