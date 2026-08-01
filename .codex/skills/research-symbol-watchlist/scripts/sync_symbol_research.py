#!/usr/bin/env python3
"""Create or verify durable research files for the active SYMBOLS.md universe."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class SymbolRecord:
    symbol: str
    instrument: str
    asset_class: str
    description: str


ROW_PATTERN = re.compile(r"^\|\s*`([A-Z0-9._-]+)`\s*\|")
REQUIRED_FILES = ("LATEST.md", "DECISIONS.md")
LATEST_MARKERS = (
    "<!-- analyst-template: latest-v2 -->",
    "<!-- analyst-template: latest-v3 -->",
)
DECISIONS_MARKER = "<!-- analyst-template: decisions-v2 -->"


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def parse_active_universe(path: Path) -> list[SymbolRecord]:
    records: list[SymbolRecord] = []
    in_universe = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line == "## Active Universe":
            in_universe = True
            continue
        if in_universe and raw_line.startswith("## "):
            break
        if not in_universe or not ROW_PATTERN.match(raw_line):
            continue
        cells = [cell.strip() for cell in raw_line.strip().strip("|").split("|")]
        if len(cells) != 5:
            raise ValueError(f"malformed active-universe row: {raw_line}")
        symbol = cells[0].strip("`")
        records.append(SymbolRecord(symbol, cells[1], cells[2], cells[3]))

    if not in_universe:
        raise ValueError(f"missing Active Universe section in {path}")
    if not records:
        raise ValueError(f"no active symbols found in {path}")
    symbols = [record.symbol for record in records]
    if len(symbols) != len(set(symbols)):
        raise ValueError("duplicate symbols found in Active Universe")
    return records


def render(template: str, record: SymbolRecord) -> str:
    return (
        template.replace("{{SYMBOL}}", record.symbol)
        .replace("{{INSTRUMENT}}", record.instrument)
        .replace("{{ASSET_CLASS}}", record.asset_class)
        .replace("{{DESCRIPTION}}", record.description)
    )


def write_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def initialize_report(repo_root: Path, records: list[SymbolRecord], template: str) -> bool:
    report_path = repo_root / "REPORT.md"
    if report_path.exists():
        return False
    summary_rows = []
    probability_rows = []
    risk_rows = []
    completion_rows = []
    for record in records:
        link = f"research/symbols/{record.symbol}/LATEST.md"
        summary_rows.append(
            f"| `{record.symbol}` | {record.instrument} | — | — | Not researched | "
            f"Observe | [Latest]({link}) |"
        )
        probability_rows.append(f"| `{record.symbol}` | — | — | — | — | Insufficient |")
        risk_rows.append(f"| `{record.symbol}` | — | — | — | Not researched |")
        completion_rows.append(
            f"| `{record.symbol}` | not_started | not_started | not_started | "
            "not_started | not_started | not_started | not_started |"
        )
    state = {
        "schema_version": "symbol-research-report-state-v1",
        "batch_id": None,
        "batch_status": "initialized",
        "decision_cutoff": None,
        "access_completed_at": None,
        "reporting_currency": "USD",
        "research_depth_contract": "full-depth-v1",
        "batch_checkpoint": None,
        "shared_macro_status": "not_started",
        "evidence_record_count": 0,
        "forecast_registration_count": 0,
        "active_symbols": [record.symbol for record in records],
        "symbol_states": {record.symbol: "not_started" for record in records},
    }
    content = (
        template.replace("{{SUMMARY_ROWS}}", "\n".join(summary_rows))
        .replace("{{PROBABILITY_ROWS}}", "\n".join(probability_rows))
        .replace("{{RISK_ROWS}}", "\n".join(risk_rows))
        .replace("{{COMPLETION_ROWS}}", "\n".join(completion_rows))
        .replace("{{REPORT_STATE_JSON}}", json.dumps(state, indent=2))
    )
    report_path.write_text(content, encoding="utf-8")
    return True


def sync(repo_root: Path, records: list[SymbolRecord]) -> int:
    skill_root = Path(__file__).resolve().parents[1]
    asset_root = skill_root / "assets"
    latest_template = (asset_root / "LATEST.template.md").read_text(encoding="utf-8")
    decisions_template = (asset_root / "DECISIONS.template.md").read_text(encoding="utf-8")
    report_template = (asset_root / "REPORT.template.md").read_text(encoding="utf-8")
    symbol_root = repo_root / "research" / "symbols"
    symbol_root.mkdir(parents=True, exist_ok=True)
    created = 0
    for record in records:
        directory = symbol_root / record.symbol
        history = directory / "history"
        history.mkdir(parents=True, exist_ok=True)
        created += write_missing(directory / "LATEST.md", render(latest_template, record))
        created += write_missing(directory / "DECISIONS.md", render(decisions_template, record))
        created += write_missing(history / ".gitkeep", "")
    created += initialize_report(repo_root, records, report_template)
    return created


def check(repo_root: Path, records: list[SymbolRecord]) -> list[str]:
    failures: list[str] = []
    report_path = repo_root / "REPORT.md"
    report = report_path.read_text(encoding="utf-8") if report_path.is_file() else ""
    if not report:
        failures.append("REPORT.md is missing or empty")
    for record in records:
        directory = repo_root / "research" / "symbols" / record.symbol
        if not directory.is_dir():
            failures.append(f"missing symbol directory: {record.symbol}")
            continue
        for filename in REQUIRED_FILES:
            if not (directory / filename).is_file():
                failures.append(f"missing {record.symbol}/{filename}")
        latest_path = directory / "LATEST.md"
        if latest_path.is_file() and not any(
            marker in latest_path.read_text(encoding="utf-8") for marker in LATEST_MARKERS
        ):
            failures.append(f"unmigrated {record.symbol}/LATEST.md")
        decisions_path = directory / "DECISIONS.md"
        if decisions_path.is_file() and DECISIONS_MARKER not in decisions_path.read_text(encoding="utf-8"):
            failures.append(f"unmigrated {record.symbol}/DECISIONS.md")
        if not (directory / "history").is_dir():
            failures.append(f"missing {record.symbol}/history directory")
        expected_link = f"research/symbols/{record.symbol}/LATEST.md"
        if expected_link not in report:
            failures.append(f"REPORT.md does not link {record.symbol}/LATEST.md")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--sync", action="store_true", help="create missing files without overwriting")
    action.add_argument("--check", action="store_true", help="verify active-universe coverage")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    try:
        records = parse_active_universe(repo_root / "SYMBOLS.md")
        created = sync(repo_root, records) if args.sync else 0
        failures = check(repo_root, records)
    except (OSError, ValueError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print(f"PASS {len(records)} active symbols verified; {created} missing files created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
