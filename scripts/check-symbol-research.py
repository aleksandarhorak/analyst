#!/usr/bin/env python3
"""Validate symbol-research coverage, probability integrity, and test fixtures."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


REQUIRED_HORIZONS = ("1 trading day", "2 weeks", "1 month", "2 months")
REQUIRED_FIXTURES = {
    "stale_price",
    "missing_news",
    "ambiguous_alias",
    "invalid_probability_sum",
    "narrative_only_psychology",
    "five_x_downside",
}
SYMBOL_PATTERN = re.compile(r"^\|\s*`([A-Z0-9._-]+)`\s*\|")
PROBABILITY_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)$")
NUMBER_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)%?$")
LATEST_MARKER = "<!-- analyst-template: latest-v2 -->"
DECISIONS_MARKER = "<!-- analyst-template: decisions-v2 -->"
REPORT_MARKER = "<!-- analyst-template: report-v2 -->"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


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
        raise ValueError("active universe is empty or contains duplicates")
    return symbols


def section(text: str, heading: str) -> str:
    marker = f"## {heading}\n"
    if marker not in text:
        return ""
    content = text.split(marker, 1)[1]
    return content.split("\n## ", 1)[0]


def section_symbols(text: str, heading: str) -> list[str]:
    return [
        match.group(1)
        for line in section(text, heading).splitlines()
        if (match := SYMBOL_PATTERN.match(line))
    ]


def check_probability_sum(values: list[str], context: str, failures: list[str]) -> None:
    if all(value == "—" for value in values):
        return
    parsed = []
    for value in values:
        match = NUMBER_PATTERN.fullmatch(value)
        if not match:
            fail(f"{context}: probability is neither numeric nor an em dash", failures)
            return
        parsed.append(float(match.group(1)))
    if abs(sum(parsed) - 100.0) > 0.01:
        fail(f"{context}: up/flat/down total is {sum(parsed):g}, expected 100", failures)


def check_latest(path: Path, symbol: str, failures: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for phrase in (
        LATEST_MARKER,
        "Reporting currency: USD",
        "5x gross linear",
        "Insufficient evidence",
        "## Data Lineage",
        "Template version: 2",
    ):
        if phrase not in text:
            fail(f"{symbol}/LATEST.md is missing required phrase: {phrase}", failures)
    probability_section = section(text, "Directional Probabilities")
    rows: dict[str, list[str]] = {}
    for line in probability_section.splitlines():
        if not line.startswith("|") or line.startswith("|---") or "Horizon" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 8:
            rows[cells[0]] = cells
    if tuple(rows) != REQUIRED_HORIZONS:
        fail(f"{symbol}/LATEST.md does not contain the four required horizons in order", failures)
        return
    for horizon, cells in rows.items():
        check_probability_sum(cells[3:6], f"{symbol} {horizon}", failures)


def check_report(repo_root: Path, symbols: list[str], failures: list[str]) -> None:
    report_path = repo_root / "REPORT.md"
    if not report_path.is_file():
        fail("REPORT.md is missing", failures)
        return
    report = report_path.read_text(encoding="utf-8")
    for phrase in (
        REPORT_MARKER,
        "Reporting currency: USD",
        "5x gross linear",
        "1 trading day",
        "2 months",
        "Evidence packets / forecast registrations",
    ):
        if phrase not in report:
            fail(f"REPORT.md is missing required phrase: {phrase}", failures)
    for heading in ("Universe And Current Evidence", "Directional Probabilities", "Downside And 5x Exposure"):
        if section_symbols(report, heading) != symbols:
            fail(f"REPORT.md section has incomplete or misordered coverage: {heading}", failures)

    for line in section(report, "Universe And Current Evidence").splitlines():
        match = SYMBOL_PATTERN.match(line)
        if not match:
            continue
        symbol = match.group(1)
        expected = f"research/symbols/{symbol}/LATEST.md"
        if expected not in line or not (repo_root / expected).is_file():
            fail(f"REPORT.md has a missing or broken detail link for {symbol}", failures)

    for line in section(report, "Directional Probabilities").splitlines():
        match = SYMBOL_PATTERN.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        for horizon, value in zip(REQUIRED_HORIZONS, cells[1:5], strict=True):
            if value == "—":
                continue
            probability = PROBABILITY_PATTERN.fullmatch(value)
            if not probability:
                fail(f"REPORT.md {match.group(1)} {horizon}: invalid U/F/D cell", failures)
                continue
            if abs(sum(map(float, probability.groups())) - 100.0) > 0.01:
                fail(f"REPORT.md {match.group(1)} {horizon}: U/F/D does not total 100", failures)


def check_symbol_tree(repo_root: Path, symbols: list[str], failures: list[str]) -> None:
    root = repo_root / "research" / "symbols"
    for symbol in symbols:
        directory = root / symbol
        latest = directory / "LATEST.md"
        decisions = directory / "DECISIONS.md"
        history = directory / "history"
        if not latest.is_file():
            fail(f"missing {symbol}/LATEST.md", failures)
        else:
            check_latest(latest, symbol, failures)
        if not decisions.is_file() or any(
            phrase not in decisions.read_text(encoding="utf-8")
            for phrase in ("append-only", DECISIONS_MARKER)
        ):
            fail(f"missing or invalid {symbol}/DECISIONS.md", failures)
        if not history.is_dir():
            fail(f"missing {symbol}/history", failures)


def check_fixtures(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / "evaluations" / "symbol-research" / "cases.jsonl"
    if not path.is_file():
        fail("symbol-research adverse fixtures are missing", failures)
        return
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = {case.get("id") for case in cases}
    if ids != REQUIRED_FIXTURES:
        fail(f"fixture IDs differ from required set: {sorted(ids)}", failures)
    for case in cases:
        if not case.get("expected_behaviors") or not case.get("critical_failures"):
            fail(f"fixture lacks behavior or critical-failure assertions: {case.get('id')}", failures)
    leverage = next((case.get("numeric_check") for case in cases if case.get("id") == "five_x_downside"), None)
    if leverage:
        capital = leverage["capital_usd"]
        underlying_return = leverage["underlying_return"]
        multiple = leverage["leverage"]
        if abs(capital * underlying_return - leverage["expected_unlevered_pnl_usd"]) > 0.01:
            fail("five_x_downside has incorrect unlevered fixture arithmetic", failures)
        if abs(capital * multiple * underlying_return - leverage["expected_gross_pnl_usd"]) > 0.01:
            fail("five_x_downside has incorrect leveraged fixture arithmetic", failures)
    else:
        fail("five_x_downside numeric fixture is missing", failures)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    failures: list[str] = []
    try:
        symbols = active_symbols(repo_root / "SYMBOLS.md")
        check_symbol_tree(repo_root, symbols, failures)
        check_report(repo_root, symbols, failures)
        check_fixtures(repo_root, failures)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        fail(str(error), failures)

    if failures:
        for message in failures:
            print(f"FAIL {message}", file=sys.stderr)
        return 1
    print(f"PASS symbol research contract: {len(symbols)} active symbols and {len(REQUIRED_FIXTURES)} adverse fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
