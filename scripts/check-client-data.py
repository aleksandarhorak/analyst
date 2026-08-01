#!/usr/bin/env python3
"""Check operational repository artifacts for high-confidence client-data leaks."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


SSN_PATTERN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
EMAIL_PATTERN = re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.I)
E164_PHONE_PATTERN = re.compile(r"(?<![\w+])\+[1-9]\d{7,14}(?!\d)")
IBAN_PATTERN = re.compile(r"(?<![A-Z0-9])[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}(?![A-Z0-9])")
UK_NI_PATTERN = re.compile(r"(?<![A-Z0-9])[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D](?![A-Z0-9])", re.I)
PAYMENT_CARD_CANDIDATE = re.compile(
    r"(?<![\d/])(?:\d{13,19}|\d{4}(?:[ -]\d{4}){2,3})(?!\d)"
)
SENSITIVE_KEY_PATTERN = re.compile(
    r"(?ix)(?:[\"']?)(?:"
    r"client_name|full_name|account_number|bank_account|routing_number|sort_code|"
    r"date_of_birth|tax_id|ssn|passport_number|national_id|email|email_address|"
    r"phone|phone_number|postal_address|street_address|iban|swift_bic|card_number|"
    r"annual_income|net_worth|portfolio_value|client_secret|access_token|api_key|password"
    r")(?:[\"']?)\s*(?::|=)"
)
PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
AWS_ACCESS_KEY_PATTERN = re.compile(r"(?<![A-Z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])")
SCANNED_ROOTS = ("evaluations", "forecasts", "research")
SCANNED_FILES = ("REPORT.md", "SYMBOLS.md", "MEMORY.md", "TODO.md")


def passes_luhn(value: str) -> bool:
    digits = [int(character) for character in value if character.isdigit()]
    if len(digits) < 13 or len(digits) > 19 or len(set(digits)) == 1:
        return False
    total = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def findings(text: str) -> list[str]:
    result: list[str] = []
    for label, pattern in (
        ("government identifier pattern", SSN_PATTERN),
        ("email address pattern", EMAIL_PATTERN),
        ("international phone pattern", E164_PHONE_PATTERN),
        ("IBAN pattern", IBAN_PATTERN),
        ("national insurance identifier pattern", UK_NI_PATTERN),
        ("sensitive JSON/YAML-style key", SENSITIVE_KEY_PATTERN),
        ("private key material", PRIVATE_KEY_PATTERN),
        ("cloud access key pattern", AWS_ACCESS_KEY_PATTERN),
    ):
        if pattern.search(text):
            result.append(label)
    if any(passes_luhn(match.group(0)) for match in PAYMENT_CARD_CANDIDATE.finditer(text)):
        result.append("payment card number pattern")
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
        synthetic_cases = {
            "government identifier pattern": "111" + "-22-" + "3333",
            "email address pattern": "synthetic.person" + "@example.test",
            "international phone pattern": "+" + "447700900123",
            "IBAN pattern": "GB82 WEST 1234 5698 7654 32",
            "national insurance identifier pattern": "AB123456C",
            "sensitive JSON/YAML-style key": '"bank_account"' + ':"synthetic"',
            "private key material": "-----BEGIN " + "PRIVATE KEY-----",
            "cloud access key pattern": "AKIA" + "SYNTHETICKEY1234",
            "payment card number pattern": "4111" + " 1111 1111 1111",
        }
        for expected, sample in synthetic_cases.items():
            if expected not in findings(sample):
                print(f"FAIL client-data detector self-test: {expected}", file=sys.stderr)
                return 1
        if findings("SEC accession 0000320193-25-000001; ordinary research text"):
            print("FAIL client-data detector self-test: false positive", file=sys.stderr)
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
