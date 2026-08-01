#!/usr/bin/env python3
"""Validate symbol coverage, full-depth v3 state, history, and report integrity."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = REPO_ROOT / ".codex/skills/research-symbol-watchlist/scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from symbol_research_batch import validate_run  # noqa: E402
from symbol_research_contract import (  # noqa: E402
    ContractError,
    REQUIRED_HORIZONS,
    REQUIRED_LANES,
    json_block,
    markdown_section,
    parse_time,
    validate_latest_v3,
)
from sync_symbol_research import parse_active_universe  # noqa: E402


REQUIRED_FIXTURES = {
    "stale_price",
    "missing_news",
    "ambiguous_alias",
    "invalid_probability_sum",
    "narrative_only_psychology",
    "five_x_downside",
    "shallow_blanket_abstention",
    "partial_batch_resume",
    "blocked_lane_propagation",
    "conditional_workflow_overreach",
    "missing_price_metadata",
    "premature_snapshot",
    "terminal_checkpoint_correction",
    "shallow_asset_depth",
    "incomplete_forecast_registration",
    "fx_conversion_mismatch",
    "partial_completion_ledger",
    "asset_class_spoof",
    "broad_abstention_complete",
}
SYMBOL_PATTERN = re.compile(r"^\|\s*`([A-Z0-9._-]+)`\s*\|")
PROBABILITY_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)$")
NUMBER_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)%?$")
LATEST_V2 = "<!-- analyst-template: latest-v2 -->"
LATEST_V3 = "<!-- analyst-template: latest-v3 -->"
DECISIONS_MARKER = "<!-- analyst-template: decisions-v2 -->"
REPORT_V2 = "<!-- analyst-template: report-v2 -->"
REPORT_V3 = "<!-- analyst-template: report-v3 -->"
COMPLETION_LANES = REQUIRED_LANES


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


def section_symbols(text: str, heading: str) -> list[str]:
    return [
        match.group(1)
        for line in markdown_section(text, heading).splitlines()
        if (match := SYMBOL_PATTERN.match(line))
    ]


def table_rows(text: str, heading: str, width: int) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in markdown_section(text, heading).splitlines():
        match = SYMBOL_PATTERN.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == width:
            rows[match.group(1)] = cells
    return rows


def metadata_value(text: str, label: str) -> str | None:
    match = re.search(rf"(?m)^- {re.escape(label)}: (.+)$", text)
    return match.group(1).strip() if match else None


def probability_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in markdown_section(text, "Directional Probabilities").splitlines():
        if not line.startswith("|") or line.startswith("|---") or "Horizon" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 8:
            rows[cells[0]] = cells
    return rows


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


def display_number(value: float) -> str:
    return f"{value:g}"


def check_latest_probability_display(text: str, symbol: str, state: dict[str, Any], failures: list[str]) -> None:
    rows = probability_rows(text)
    if tuple(rows) != REQUIRED_HORIZONS:
        fail(f"{symbol}/LATEST.md does not contain the four required horizons in order", failures)
        return
    forecasts = {item["horizon"]: item for item in state.get("forecasts", [])}
    for horizon, cells in rows.items():
        check_probability_sum(cells[3:6], f"{symbol} {horizon}", failures)
        forecast = forecasts.get(horizon)
        if not forecast:
            continue
        if forecast["status"] == "registered":
            expected = [display_number(forecast[name]) for name in ("up", "flat", "down")]
            actual = [value.removesuffix("%") for value in cells[3:6]]
            if actual != expected or forecast["forecast_id"] not in cells[6]:
                fail(f"{symbol} {horizon}: Markdown row does not reconcile with registered forecast", failures)
        elif cells[3:6] != ["—", "—", "—"]:
            fail(f"{symbol} {horizon}: abstained/blocked forecast must display em dashes", failures)
        if cells[7] != forecast.get("confidence"):
            fail(f"{symbol} {horizon}: Markdown confidence does not reconcile with forecast state", failures)


def check_latest(
    path: Path, symbol: str, expected_asset_class: str, failures: list[str]
) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if LATEST_V2 in text:
        for phrase in (
            "Reporting currency: USD",
            "5x gross linear",
            "Insufficient evidence",
            "## Data Lineage",
            "Template version: 2",
        ):
            if phrase not in text:
                fail(f"{symbol}/LATEST.md is missing required v2 phrase: {phrase}", failures)
        rows = probability_rows(text)
        if tuple(rows) != REQUIRED_HORIZONS:
            fail(f"{symbol}/LATEST.md does not contain the four required horizons in order", failures)
        else:
            for horizon, cells in rows.items():
                check_probability_sum(cells[3:6], f"{symbol} {horizon}", failures)
        return None
    if LATEST_V3 not in text:
        fail(f"{symbol}/LATEST.md has no recognized template marker", failures)
        return None
    try:
        provisional = validate_latest_v3(
            text, symbol, expected_asset_class=expected_asset_class, require_terminal=False
        )
        terminal = provisional.get("research_status") != "not_started"
        state = validate_latest_v3(
            text, symbol, expected_asset_class=expected_asset_class, require_terminal=terminal
        )
        if terminal:
            check_latest_probability_display(text, symbol, state, failures)
        return state
    except ContractError as error:
        fail(f"{symbol}/LATEST.md violates v3 contract: {error}", failures)
        return None


def check_symbol_tree(
    repo_root: Path,
    symbols: list[str],
    asset_classes: dict[str, str],
    failures: list[str],
) -> dict[str, dict[str, Any] | None]:
    states: dict[str, dict[str, Any] | None] = {}
    root = repo_root / "research" / "symbols"
    for symbol in symbols:
        directory = root / symbol
        latest = directory / "LATEST.md"
        decisions = directory / "DECISIONS.md"
        history = directory / "history"
        if not latest.is_file():
            fail(f"missing {symbol}/LATEST.md", failures)
            states[symbol] = None
        else:
            states[symbol] = check_latest(latest, symbol, asset_classes[symbol], failures)
        if not decisions.is_file() or any(
            phrase not in decisions.read_text(encoding="utf-8")
            for phrase in ("append-only", DECISIONS_MARKER)
        ):
            fail(f"missing or invalid {symbol}/DECISIONS.md", failures)
        if not history.is_dir():
            fail(f"missing {symbol}/history", failures)
    return states


def check_report_coverage(repo_root: Path, report: str, symbols: list[str], failures: list[str]) -> None:
    for heading in ("Universe And Current Evidence", "Directional Probabilities", "Downside And 5x Exposure"):
        if section_symbols(report, heading) != symbols:
            fail(f"REPORT.md section has incomplete or misordered coverage: {heading}", failures)
    for line in markdown_section(report, "Universe And Current Evidence").splitlines():
        match = SYMBOL_PATTERN.match(line)
        if not match:
            continue
        symbol = match.group(1)
        expected = f"research/symbols/{symbol}/LATEST.md"
        if expected not in line or not (repo_root / expected).is_file():
            fail(f"REPORT.md has a missing or broken detail link for {symbol}", failures)


def check_report_probability_cells(report: str, states: dict[str, dict[str, Any] | None], failures: list[str]) -> None:
    rows = table_rows(report, "Directional Probabilities", 6)
    for symbol, cells in rows.items():
        state = states.get(symbol)
        forecasts = state.get("forecasts", []) if state else []
        for horizon, value, forecast in zip(REQUIRED_HORIZONS, cells[1:5], forecasts, strict=True):
            expected = "—"
            if forecast.get("status") == "registered":
                expected = "/".join(display_number(forecast[name]) for name in ("up", "flat", "down"))
            if value != expected:
                fail(f"REPORT.md {symbol} {horizon}: value does not reconcile with LATEST.md", failures)
        expected_confidence = "/".join(forecast.get("confidence", "missing") for forecast in forecasts)
        if cells[5] != expected_confidence:
            fail(f"REPORT.md {symbol}: confidence does not reconcile with LATEST.md", failures)


def parse_plain_number(value: str) -> float | None:
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def check_report_risk_cells(report: str, states: dict[str, dict[str, Any] | None], failures: list[str]) -> None:
    rows = table_rows(report, "Downside And 5x Exposure", 5)
    for symbol, cells in rows.items():
        state = states.get(symbol)
        risk = state.get("risk") if state else None
        if not risk:
            continue
        if risk.get("status") == "complete":
            expected = [
                risk["reference_capital_usd"],
                risk["unlevered_pnl_usd"],
                risk["gross_5x_pnl_usd"],
            ]
            actual = [parse_plain_number(value) for value in cells[1:4]]
            if any(value is None for value in actual) or any(
                abs(left - right) > 0.01 for left, right in zip(actual, expected, strict=True)
            ):
                fail(f"REPORT.md {symbol}: risk values do not reconcile with LATEST.md", failures)
        elif cells[1:4] != ["—", "—", "—"]:
            fail(f"REPORT.md {symbol}: non-complete risk must display em dashes", failures)
        if cells[4] != risk.get("margin_liquidation_summary"):
            fail(f"REPORT.md {symbol}: margin/liquidation status does not reconcile with LATEST.md", failures)


def check_report_summary_cells(report: str, states: dict[str, dict[str, Any] | None], failures: list[str]) -> None:
    rows = table_rows(report, "Universe And Current Evidence", 7)
    for symbol, cells in rows.items():
        state = states.get(symbol)
        if not state:
            continue
        price = state["price_observation"]
        expected_instrument = state["exact_instrument"] if state["identity_status"] == "resolved" else "Unresolved"
        expected_price = display_number(price["usd_value"]) if price["status"] == "verified" else "—"
        expected_time = price["observed_at"] if price["status"] == "verified" else "—"
        expected_news = state["lanes"]["news_catalysts"]["status"]
        thesis = state["analysis_depth"]["investment_thesis"]
        expected_view = thesis.get("decision_status") or state["research_status"]
        if cells[1:6] != [expected_instrument, expected_price, expected_time, expected_news, expected_view]:
            fail(f"REPORT.md {symbol}: summary values do not reconcile with LATEST.md", failures)


def check_current_snapshot(repo_root: Path, symbol: str, state: dict[str, Any], failures: list[str]) -> None:
    manifest_path = repo_root / "research" / "symbols" / symbol / "history" / "MANIFEST.jsonl"
    try:
        records = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as error:
        fail(f"{symbol}: cannot read current history manifest: {error}", failures)
        return
    if not records or records[-1].get("batch_id") != state["batch_id"]:
        fail(f"{symbol}: latest manifest record is not the report batch", failures)
        return
    latest_bytes = (repo_root / "research" / "symbols" / symbol / "LATEST.md").read_bytes()
    if records[-1].get("latest_sha256") != hashlib.sha256(latest_bytes).hexdigest():
        fail(f"{symbol}: current LATEST.md hash does not match manifest", failures)


def check_report_v3(
    repo_root: Path,
    report: str,
    symbols: list[str],
    states: dict[str, dict[str, Any] | None],
    failures: list[str],
) -> None:
    try:
        report_state = json_block(report, "Machine-Readable Batch State")
    except ContractError as error:
        fail(f"REPORT.md v3 state is invalid: {error}", failures)
        return
    if report_state.get("schema_version") != "symbol-research-report-state-v1":
        fail("REPORT.md has an invalid v3 state schema", failures)
    if report_state.get("active_symbols") != symbols:
        fail("REPORT.md v3 active symbol order does not match SYMBOLS.md", failures)
    if report_state.get("reporting_currency") != "USD" or report_state.get("research_depth_contract") != "full-depth-v1":
        fail("REPORT.md v3 currency or research-depth contract is invalid", failures)
    batch_status = report_state.get("batch_status")
    if batch_status == "initialized":
        if any(state and state.get("research_status") != "not_started" for state in states.values()):
            fail("initialized REPORT.md cannot contain terminal v3 symbol state", failures)
        return
    if batch_status not in {"complete", "partial"}:
        fail("REPORT.md v3 batch_status must be initialized, complete, or partial", failures)
        return
    batch_id = report_state.get("batch_id")
    checkpoint = report_state.get("batch_checkpoint")
    expected_checkpoint = f"research/batches/{batch_id}/RUN.json"
    if checkpoint != expected_checkpoint or not (repo_root / expected_checkpoint).is_file():
        fail("REPORT.md v3 batch checkpoint is missing or mismatched", failures)
        return
    try:
        run = json.loads((repo_root / expected_checkpoint).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"REPORT.md batch checkpoint cannot be read: {error}", failures)
        return
    for message in validate_run(repo_root, run, final=True):
        fail(f"REPORT.md batch checkpoint: {message}", failures)
    if run.get("batch_status") != batch_status or run.get("decision_cutoff") != report_state.get("decision_cutoff"):
        fail("REPORT.md state does not reconcile with RUN.json", failures)
    if report_state.get("shared_macro_status") != run.get("shared_stages", {}).get("macro_regime", {}).get("status"):
        fail("REPORT.md shared macro status does not reconcile with RUN.json", failures)
    expected_states: dict[str, str] = {}
    for symbol in symbols:
        state = states.get(symbol)
        if not state or state.get("research_status") == "not_started":
            fail(f"REPORT.md finalized batch lacks terminal v3 state for {symbol}", failures)
            continue
        expected_states[symbol] = state["research_status"]
        if state.get("batch_id") != batch_id or state.get("decision_cutoff") != report_state.get("decision_cutoff"):
            fail(f"REPORT.md batch or cutoff differs from {symbol}/LATEST.md", failures)
        check_current_snapshot(repo_root, symbol, state, failures)
    if report_state.get("symbol_states") != expected_states:
        fail("REPORT.md symbol_states do not reconcile with per-symbol state", failures)
    evidence_count = sum(len(state.get("evidence", [])) for state in states.values() if state)
    forecast_count = sum(
        sum(1 for forecast in state.get("forecasts", []) if forecast.get("status") == "registered")
        for state in states.values() if state
    )
    if report_state.get("evidence_record_count") != evidence_count:
        fail("REPORT.md evidence_record_count does not reconcile with LATEST.md", failures)
    if report_state.get("forecast_registration_count") != forecast_count:
        fail("REPORT.md forecast_registration_count does not reconcile with LATEST.md", failures)
    if metadata_value(report, "Batch ID / decision cutoff") != f"{batch_id} / {report_state.get('decision_cutoff')}":
        fail("REPORT.md batch metadata ID/cutoff does not reconcile", failures)
    if metadata_value(report, "Batch status") != batch_status:
        fail("REPORT.md text batch status does not reconcile", failures)
    if metadata_value(report, "Batch checkpoint") != checkpoint:
        fail("REPORT.md text checkpoint does not reconcile", failures)
    expected_macro = f"research/batches/{batch_id}/MACRO.md"
    if metadata_value(report, "Shared macro artifact") != expected_macro:
        fail("REPORT.md shared macro artifact path does not reconcile", failures)
    if metadata_value(report, "Evidence packets / forecast registrations") != f"{evidence_count} / {forecast_count}":
        fail("REPORT.md text evidence/forecast counts do not reconcile", failures)
    try:
        report_completed = parse_time(report_state.get("access_completed_at"), "report access_completed_at")
        run_updated = parse_time(run.get("updated_at"), "run updated_at")
        latest_completed = max(
            parse_time(state["access_completed_at"], f"{symbol} access_completed_at")
            for symbol, state in states.items() if state
        )
        if report_completed != run_updated or report_completed < latest_completed:
            fail("REPORT.md access completion does not reconcile with RUN.json and LATEST.md", failures)
        if metadata_value(report, "Access completion time") != report_state.get("access_completed_at"):
            fail("REPORT.md text access completion does not reconcile", failures)
    except (RuntimeError, ValueError) as error:
        fail(f"REPORT.md completion timestamp is invalid: {error}", failures)
    completion = table_rows(report, "Batch Completion Ledger", len(COMPLETION_LANES) + 2)
    if list(completion) != symbols:
        fail("REPORT.md completion ledger coverage is incomplete or misordered", failures)
    for symbol, row in completion.items():
        state = states.get(symbol)
        if not state:
            continue
        expected = [state["research_status"]] + [state["lanes"][lane]["status"] for lane in COMPLETION_LANES]
        if row[1:] != expected:
            fail(f"REPORT.md completion ledger does not reconcile for {symbol}", failures)
    check_report_probability_cells(report, states, failures)
    check_report_risk_cells(report, states, failures)
    check_report_summary_cells(report, states, failures)


def check_report(
    repo_root: Path,
    symbols: list[str],
    states: dict[str, dict[str, Any] | None],
    failures: list[str],
) -> None:
    report_path = repo_root / "REPORT.md"
    if not report_path.is_file():
        fail("REPORT.md is missing", failures)
        return
    report = report_path.read_text(encoding="utf-8")
    for phrase in (
        "Reporting currency: USD",
        "5x gross linear",
        "1 trading day",
        "2 months",
        "Evidence packets / forecast registrations",
    ):
        if phrase not in report:
            fail(f"REPORT.md is missing required phrase: {phrase}", failures)
    check_report_coverage(repo_root, report, symbols, failures)
    if REPORT_V2 in report:
        for line in markdown_section(report, "Directional Probabilities").splitlines():
            match = SYMBOL_PATTERN.match(line)
            if not match:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            for horizon, value in zip(REQUIRED_HORIZONS, cells[1:5], strict=True):
                if value == "—":
                    continue
                probability = PROBABILITY_PATTERN.fullmatch(value)
                if not probability or abs(sum(map(float, probability.groups())) - 100.0) > 0.01:
                    fail(f"REPORT.md {match.group(1)} {horizon}: invalid U/F/D cell", failures)
    elif REPORT_V3 in report:
        check_report_v3(repo_root, report, symbols, states, failures)
    else:
        fail("REPORT.md has no recognized template marker", failures)


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    failures: list[str] = []
    symbols: list[str] = []
    try:
        records = parse_active_universe(repo_root / "SYMBOLS.md")
        symbols = [record.symbol for record in records]
        asset_classes = {record.symbol: record.asset_class for record in records}
        states = check_symbol_tree(repo_root, symbols, asset_classes, failures)
        check_report(repo_root, symbols, states, failures)
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
