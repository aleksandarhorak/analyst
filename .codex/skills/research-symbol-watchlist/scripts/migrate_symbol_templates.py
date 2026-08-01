#!/usr/bin/env python3
"""Apply or check non-destructive symbol-research template migrations."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys


LATEST_MARKER = "<!-- analyst-template: latest-v2 -->"
DECISIONS_MARKER = "<!-- analyst-template: decisions-v2 -->"
REPORT_MARKER = "<!-- analyst-template: report-v2 -->"
ANY_MARKER = re.compile(r"<!-- analyst-template: (latest|decisions|report)-v(\d+) -->")
SYMBOL_PATTERN = re.compile(r"^\|\s*`([A-Z0-9._-]+)`\s*\|")


class MigrationError(RuntimeError):
    """A template cannot be migrated without risking existing content."""


def atomic_replace(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.migration.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def insert_after_title(text: str, marker: str) -> str:
    first_newline = text.find("\n")
    if first_newline < 0 or not text.startswith("# "):
        raise MigrationError("document lacks a Markdown title")
    return text[: first_newline + 1] + "\n" + marker + text[first_newline + 1 :]


def reject_unknown_marker(text: str, expected_kind: str) -> None:
    match = ANY_MARKER.search(text)
    if match and (match.group(1) != expected_kind or int(match.group(2)) != 2):
        raise MigrationError(f"unknown or mismatched template marker: {match.group(0)}")


def migrate_latest(text: str) -> str:
    reject_unknown_marker(text, "latest")
    result = text if LATEST_MARKER in text else insert_after_title(text, LATEST_MARKER)
    if "## Data Lineage" not in result:
        suffix = "" if result.endswith("\n") else "\n"
        result += (
            suffix
            + "\n## Data Lineage\n\n"
            + "- Evidence packet IDs: —\n"
            + "- Registered forecast IDs: —\n"
            + "- Template version: 2\n"
        )
    return result


def migrate_decisions(text: str) -> str:
    reject_unknown_marker(text, "decisions")
    return text if DECISIONS_MARKER in text else insert_after_title(text, DECISIONS_MARKER)


def migrate_report(text: str) -> str:
    reject_unknown_marker(text, "report")
    result = text if REPORT_MARKER in text else insert_after_title(text, REPORT_MARKER)
    lineage = "- Evidence packets / forecast registrations: Not researched"
    if not re.search(r"(?m)^- Evidence packets / forecast registrations: .+$", result):
        anchor = "- Capacity: Impersonal research; no order authority"
        if anchor not in result:
            raise MigrationError("report lacks capacity metadata anchor")
        result = result.replace(anchor, anchor + "\n" + lineage, 1)
    return result


def active_symbols(path: Path) -> list[str]:
    symbols: list[str] = []
    in_universe = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "## Active Universe":
            in_universe = True
            continue
        if in_universe and line.startswith("## "):
            break
        match = SYMBOL_PATTERN.match(line) if in_universe else None
        if match:
            symbols.append(match.group(1))
    if not symbols or len(symbols) != len(set(symbols)):
        raise MigrationError("active symbol universe is empty or duplicated")
    return symbols


def process(path: Path, migrate, apply: bool) -> bool:
    original = path.read_text(encoding="utf-8")
    migrated = migrate(original)
    changed = migrated != original
    if changed and apply:
        atomic_replace(path, migrated)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    try:
        changes: list[str] = []
        for symbol in active_symbols(repo_root / "SYMBOLS.md"):
            symbol_root = repo_root / "research" / "symbols" / symbol
            for filename, migration in (("LATEST.md", migrate_latest), ("DECISIONS.md", migrate_decisions)):
                path = symbol_root / filename
                if process(path, migration, args.apply):
                    changes.append(str(path.relative_to(repo_root)))
        report = repo_root / "REPORT.md"
        if process(report, migrate_report, args.apply):
            changes.append(str(report.relative_to(repo_root)))
    except (MigrationError, OSError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1

    if args.check and changes:
        for path in changes:
            print(f"FAIL migration required: {path}", file=sys.stderr)
        return 1
    action = "migrated" if args.apply else "verified"
    print(f"PASS {action} symbol templates; {len(changes)} file(s) changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
