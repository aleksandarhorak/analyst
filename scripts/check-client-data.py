#!/usr/bin/env python3
"""Check operational repository artifacts for high-confidence client-data leaks."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


SSN_PATTERN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
SENSITIVE_KEY_PATTERN = re.compile(
    r'(?i)["\'](?:client_name|account_number|date_of_birth|tax_id|ssn|passport_number)["\']\s*:'
)
PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
SCANNED_ROOTS = ("evaluations", "forecasts", "research/symbols")
SCANNED_FILES = ("REPORT.md", "SYMBOLS.md", "MEMORY.md", "TODO.md")


def findings(text: str) -> list[str]:
    result: list[str] = []
    for label, pattern in (
        ("government identifier pattern", SSN_PATTERN),
        ("sensitive JSON/YAML-style key", SENSITIVE_KEY_PATTERN),
        ("private key material", PRIVATE_KEY_PATTERN),
    ):
        if pattern.search(text):
            result.append(label)
    return result


def candidate_files(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for root_name in SCANNED_ROOTS:
        root = repo_root / root_name
        if root.is_dir():
            paths.extend(path for path in root.rglob("*") if path.is_file() and path.name != ".gitkeep")
    paths.extend(repo_root / name for name in SCANNED_FILES if (repo_root / name).is_file())
    return sorted(set(paths))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        synthetic_identifier = "111" + "-22-" + "3333"
        if not findings(f'{{"client_name":"Synthetic", "id":"{synthetic_identifier}"}}'):
            print("FAIL client-data detector self-test", file=sys.stderr)
            return 1

    repo_root = args.repo_root.resolve()
    failures: list[str] = []
    for path in candidate_files(repo_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"non-text operational artifact: {path.relative_to(repo_root)}")
            continue
        for finding in findings(text):
            failures.append(f"{path.relative_to(repo_root)}: {finding}")

    policy = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    governance = (
        repo_root / ".codex/skills/govern-client-data/SKILL.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "Never store real client identity",
        "Use an approved secure client system",
        "synthetic repository tests",
    ):
        if phrase not in policy:
            failures.append(f"AGENTS.md missing client-data guardrail: {phrase}")
    for phrase in ("Never store real client data", "Use synthetic data", "Stop collection"):
        if phrase not in governance:
            failures.append(f"govern-client-data missing guardrail: {phrase}")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print(f"PASS client-data policy and {len(candidate_files(repo_root))} operational artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
