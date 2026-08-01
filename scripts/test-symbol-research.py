#!/usr/bin/env python3
"""Executable regressions for v3 symbol depth and resumable batch state."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = REPO_ROOT / ".codex/skills/research-symbol-watchlist/scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from symbol_research_contract import (  # noqa: E402
    ContractError,
    LANE_LABELS,
    REQUIRED_HORIZONS,
    REQUIRED_LANES,
    validate_latest_v3,
)


BATCH_SCRIPT = SKILL_SCRIPTS / "symbol_research_batch.py"
SYNC_SCRIPT = SKILL_SCRIPTS / "sync_symbol_research.py"
HISTORY_SCRIPT = SKILL_SCRIPTS / "symbol_research_history.py"
CHECK_SCRIPT = REPO_ROOT / "scripts/check-symbol-research.py"


def evidence(evidence_id: str, scope: str = "symbol") -> dict[str, object]:
    return {
        "id": evidence_id,
        "scope": scope,
        "source_type": "primary",
        "locator": f"https://example.test/{evidence_id}",
        "published_at": "2026-08-01T11:00:00Z",
        "accessed_at": "2026-08-01T12:05:00Z",
        "cutoff_eligible": True,
        "claim": f"Synthetic primary evidence supporting the {evidence_id} analytical lane.",
    }


def complete_state() -> dict[str, object]:
    lanes = {
        lane: {
            "status": "complete",
            "evidence_ids": ["symbol-source" if lane != "macro_transmission" else "macro-source"],
            "summary": f"Completed substantive synthetic work for {lane} with reconciled evidence and assumptions.",
            "reason_code": None,
            "next_action": None,
        }
        for lane in REQUIRED_LANES
    }
    forecasts = [
        {
            "horizon": horizon,
            "status": "registered",
            "start_value": 100.0,
            "flat_band_return": [-0.01, 0.01],
            "up": 40.0,
            "flat": 35.0,
            "down": 25.0,
            "forecast_id": f"forecast-{index + 1}",
            "reason_code": None,
        }
        for index, horizon in enumerate(REQUIRED_HORIZONS)
    ]
    return {
        "schema_version": "symbol-research-state-v1",
        "symbol": "TEST",
        "asset_class": "Stock",
        "batch_id": "2026-08-01T120000Z",
        "decision_cutoff": "2026-08-01T12:00:00Z",
        "access_completed_at": "2026-08-01T12:10:00Z",
        "reporting_currency": "USD",
        "identity_status": "resolved",
        "research_status": "complete",
        "exact_instrument": "TEST common stock on Synthetic Exchange",
        "batch_checkpoint": "research/batches/2026-08-01T120000Z/RUN.json",
        "lanes": lanes,
        "evidence": [evidence("symbol-source"), evidence("macro-source", "shared_macro")],
        "price_observation": {
            "status": "verified",
            "native_value": 100.0,
            "native_currency": "USD",
            "units": "USD per share",
            "observed_at": "2026-08-01T12:00:00Z",
            "market_session": "closed",
            "price_policy": "official_close",
            "usd_value": 100.0,
            "price_evidence_id": "symbol-source",
            "fx_evidence_id": None,
            "reason_code": None,
        },
        "analysis_depth": {
            "fundamentals_product": {
                "reconciliation_ids": ["symbol-source"],
                "drivers": ["Revenue growth driver", "Operating margin driver"],
                "limitations": "Synthetic statements omit real issuer detail and are used only for regression testing.",
            },
            "valuation_scenarios": {
                "methods": ["Discounted cash flow", "Reverse discounted cash flow"],
                "base": "Base scenario links moderate revenue growth and stable margins to cash flow.",
                "bull": "Bull scenario links stronger demand and margin expansion to higher cash flow.",
                "bear": "Bear scenario links demand weakness and margin compression to lower cash flow.",
                "sensitivity": "Value sensitivity covers discount rate, terminal growth, margins, and dilution.",
            },
            "news_catalysts": {
                "window_start": "2026-07-25T00:00:00Z",
                "window_end": "2026-08-01T12:00:00Z",
                "expectation_basis": "Synthetic pre-event expectations are preserved with the event chronology.",
            },
            "macro_transmission": {
                "shared_evidence_ids": ["macro-source"],
                "channels": ["Discount-rate transmission", "End-demand transmission"],
                "instrument_effect": "The synthetic regime affects discount rates and customer demand in opposite directions.",
            },
            "market_behavior": {
                "observations": ["Timestamped synthetic price and volume response"],
                "alternatives": ["Fundamental repricing rather than behavioral overreaction"],
                "falsifier": "A reversal without volume normalization would falsify the proposed response mechanism.",
            },
            "investment_thesis": {
                "decision_status": "observe",
                "variant_view": "The synthetic variant view expects better cash conversion than the market-implied case.",
                "market_implied_view": "The synthetic market-implied case assumes slower growth and persistent margin pressure.",
                "catalysts": ["Synthetic earnings and cash-flow update"],
                "contrary_case": "The strongest contrary case is sustained demand weakness and negative operating leverage.",
                "disconfirmers": ["Revenue growth remains below the bear-case trigger"],
                "invalidation": "The thesis is invalidated if demand and cash conversion remain below the bear case.",
            },
            "monitoring": {
                "signals": ["Quarterly revenue growth", "Free-cash-flow conversion"],
                "next_review": "2026-08-02T12:00:00Z",
            },
        },
        "forecasts": forecasts,
        "risk": {
            "status": "complete",
            "reference_capital_usd": 1000.0,
            "underlying_downside_return": -0.12,
            "unlevered_pnl_usd": -120.0,
            "gross_5x_pnl_usd": -600.0,
            "reason_code": None,
        },
        "unblockers": [],
    }


def render_document(state: dict[str, object]) -> str:
    ledger = "\n".join(
        f"| {LANE_LABELS[lane]} | Complete | Completed synthetic evidence and reconciled analytical work. | Continue monitoring the stated evidence. |"
        for lane in REQUIRED_LANES
    )
    probability_rows = "\n".join(
        f"| {horizon} | 100 | -1% to 1% | 40 | 35 | 25 | forecast-{index + 1} | Medium |"
        for index, horizon in enumerate(REQUIRED_HORIZONS)
    )
    sections = {
        "Instrument And Batch": "Exact synthetic common stock, USD, cutoff preserved under full-depth-v1.",
        "Machine-Readable Research State": f"```json\n{json.dumps(state, indent=2)}\n```",
        "Research Depth Ledger": (
            "| Lane | Status | Evidence/work completed | Blocker or next action |\n"
            "|---|---|---|---|\n" + ledger
        ),
        "Price And Evidence": "Synthetic point-in-time price and a complete evidence ledger are reconciled.",
        "Fundamentals Or Product Analysis": "Synthetic statements and business drivers are reconciled across periods.",
        "Valuation And Scenarios": "Base, bull, and bear cases use DCF and reverse-valuation sensitivities.",
        "News And Catalysts": "The searched window, expectations, chronology, and response are documented.",
        "Macro Transmission": "The shared regime is mapped to cash flow, discount rate, and demand.",
        "Market Behavior": "Observable volume evidence is tested against alternatives and a falsifier.",
        "Investment Thesis": "Variant view, scenarios, catalysts, contrary case, and invalidation are complete.",
        "Directional Probabilities": (
            "| Horizon | Start | Flat band | Up | Flat | Down | Calibration / forecast ID | Confidence |\n"
            "|---|---:|---:|---:|---:|---:|---|---|\n" + probability_rows
        ),
        "Downside And 5x Exposure": "Reference capital 1000; unlevered -120; approximate 5x gross -600 before costs and liquidation.",
        "Monitoring": "Review disconfirmers, catalysts, registered outcomes, and source updates at the stated date.",
        "Decision": "- Immutable snapshot: —\n- Status: Observe\n- Invalidation and next review: Synthetic trigger and date.",
        "Data Lineage": "Evidence IDs and forecast IDs are recorded; template version is 3.",
    }
    body = "\n\n".join(f"## {heading}\n\n{content}" for heading, content in sections.items())
    return f"# TEST — Latest Research\n\n<!-- analyst-template: latest-v3 -->\n\n{body}\n"


def expect_rejected(state: dict[str, object], expected: str) -> None:
    try:
        validate_latest_v3(render_document(state), "TEST", require_terminal=True)
    except ContractError as error:
        if expected not in str(error):
            raise AssertionError(f"expected rejection containing {expected!r}, got {error!r}") from error
        return
    raise AssertionError(f"expected v3 artifact to be rejected: {expected}")


def run_script(script: Path, arguments: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(script), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != expected:
        raise AssertionError(
            f"expected batch exit {expected}, got {completed.returncode}\n"
            f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
        )
    return completed


def run_batch(root: Path, arguments: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    return run_script(BATCH_SCRIPT, arguments, expected)


def complete_batch_artifacts(root: Path, run: dict[str, object]) -> None:
    batch_id = run["batch_id"]
    cutoff = run["decision_cutoff"]
    for stage, relative in run["shared_workspaces"].items():
        evidence_id = f"shared-{stage}-evidence"
        path = root / relative
        if stage == "macro_regime":
            content = (
                "# Shared Macro Regime\n\n<!-- analyst-template: symbol-batch-macro-v1 -->\n\n"
                f"- Batch ID: {batch_id}\n- Status: Complete\n"
                f"- Evidence ID: {evidence_id}\n\n"
                "## Evidence Ledger\n\nSynthetic primary evidence reviewed and reconciled.\n\n"
                "## Regime Scenarios\n\nBase, upside, and downside regimes completed.\n\n"
                "## Per-Symbol Transmission Inputs\n\nSynthetic transmission inputs completed.\n\n"
                "## Limitations\n\nSynthetic fixture only.\n"
            )
        else:
            content = (
                f"# Completed {stage}\n\n<!-- analyst-template: symbol-batch-shared-v1 -->\n\n"
                f"- Batch ID: {batch_id}\n- Decision cutoff: {cutoff}\n- Status: Complete\n"
                f"- Evidence ID: {evidence_id}\n\n## Evidence And Work\n\n"
                "Synthetic shared work is complete and centrally reconciled.\n"
            )
        path.write_text(content, encoding="utf-8")
    for symbol, paths in run["symbol_workspaces"].items():
        (root / paths["evidence"]).write_text(
            f"# {symbol} — Completed Evidence Ledger\n\n"
            "<!-- analyst-template: symbol-batch-evidence-v1 -->\n\n"
            f"- Batch ID: {batch_id}\n- Decision cutoff: {cutoff}\n"
            "- Evidence IDs: symbol-source, macro-source\n\n"
            "Synthetic eligible evidence and analytical attempts are fully recorded.\n",
            encoding="utf-8",
        )


def test_contract() -> None:
    valid = complete_state()
    validate_latest_v3(render_document(valid), "TEST", require_terminal=True)

    nonterminal = copy.deepcopy(valid)
    nonterminal["lanes"]["valuation_scenarios"]["status"] = "in_progress"
    expect_rejected(nonterminal, "invalid status")

    after_cutoff = copy.deepcopy(valid)
    after_cutoff["evidence"][0]["published_at"] = "2026-08-01T12:00:01Z"
    expect_rejected(after_cutoff, "published after")

    preserved_late = copy.deepcopy(valid)
    late = evidence("after-cutoff-source")
    late["published_at"] = "2026-08-01T12:00:01Z"
    late["cutoff_eligible"] = False
    preserved_late["evidence"].append(late)
    validate_latest_v3(render_document(preserved_late), "TEST", require_terminal=True)
    relied_on_late = copy.deepcopy(preserved_late)
    relied_on_late["lanes"]["news_catalysts"]["evidence_ids"] = ["after-cutoff-source"]
    expect_rejected(relied_on_late, "cutoff-ineligible")

    unknown_availability = copy.deepcopy(valid)
    unknown_availability["evidence"][0]["published_at"] = None
    expect_rejected(unknown_availability, "availability_basis")

    no_forecast_id = copy.deepcopy(valid)
    no_forecast_id["forecasts"][0]["forecast_id"] = None
    expect_rejected(no_forecast_id, "forecast_id")

    bad_risk = copy.deepcopy(valid)
    bad_risk["risk"]["gross_5x_pnl_usd"] = -500.0
    expect_rejected(bad_risk, "5x risk arithmetic")

    bad_price = copy.deepcopy(valid)
    bad_price["price_observation"]["market_session"] = None
    expect_rejected(bad_price, "market_session")

    shallow_valuation = copy.deepcopy(valid)
    shallow_valuation["analysis_depth"]["valuation_scenarios"]["methods"] = ["Discounted cash flow"]
    expect_rejected(shallow_valuation, "at least 2")

    evidence_free_abstention = copy.deepcopy(valid)
    lane = evidence_free_abstention["lanes"]["market_behavior"]
    lane.update(
        {
            "status": "abstained",
            "evidence_ids": [],
            "reason_code": "no_observable_behavior_evidence",
            "next_action": "Acquire participant-specific flow and positioning observations.",
        }
    )
    expect_rejected(evidence_free_abstention, "must reference evidence or an attempt record")

    propagated = copy.deepcopy(valid)
    lane = propagated["lanes"]["fundamentals_product"]
    lane.update(
        {
            "status": "blocked",
            "reason_code": "unavailable_current_price",
            "next_action": "Acquire a cutoff-eligible current price before continuing this lane.",
        }
    )
    propagated["research_status"] = "partial"
    expect_rejected(propagated, "price unavailability cannot block independent lane")

    generic = copy.deepcopy(valid)
    for lane in generic["lanes"].values():
        lane.update(
            {
                "status": "abstained",
                "summary": "The same generic insufficient evidence response was copied without analytical work.",
                "reason_code": "missing_primary_evidence",
                "next_action": "Find additional primary evidence before making any analytical conclusion.",
            }
        )
    generic["research_status"] = "complete"
    for forecast in generic["forecasts"]:
        forecast.update(
            {
                "status": "abstained",
                "start_value": None,
                "flat_band_return": None,
                "up": None,
                "flat": None,
                "down": None,
                "forecast_id": None,
                "reason_code": "missing_primary_evidence",
            }
        )
    generic["risk"] = {
        "status": "abstained",
        "reference_capital_usd": None,
        "underlying_downside_return": None,
        "unlevered_pnl_usd": None,
        "gross_5x_pnl_usd": None,
        "reason_code": "missing_primary_evidence",
    }
    expect_rejected(generic, "at least one completed lane")


def test_batch_checkpoint() -> None:
    with tempfile.TemporaryDirectory(prefix="analyst-symbol-batch-") as directory:
        root = Path(directory)
        (root / "SYMBOLS.md").write_text(
            "# Symbols\n\n## Active Universe\n\n"
            "| Symbol | Instrument | Asset class | Description | Status |\n"
            "|---|---|---|---|---|\n"
            "| `TEST` | Test Corp | Stock | Synthetic test. | Observe |\n",
            encoding="utf-8",
        )
        common = ["--repo-root", str(root), "--batch-id", "2026-08-01T120000Z"]
        run_batch(
            root,
            [
                "init", *common,
                "--decision-cutoff", "2026-08-01T12:00:00Z",
                "--created-at", "2026-08-01T12:01:00Z",
            ],
        )
        run_batch(root, ["verify", *common])
        run_path = root / "research/batches/2026-08-01T120000Z/RUN.json"
        run = json.loads(run_path.read_text(encoding="utf-8"))
        complete_batch_artifacts(root, run)
        for stage, record in run["shared_stages"].items():
            record.update(
                {
                    "status": "complete",
                    "note": "Completed shared batch stage with reconciled synthetic evidence.",
                    "artifact_path": run["shared_workspaces"][stage],
                    "evidence_ids": [f"shared-{stage}-evidence"],
                    "updated_at": "2026-08-01T12:20:00Z",
                }
            )
        for lane, record in run["symbol_lanes"]["TEST"].items():
            record.update(
                {
                    "status": "complete",
                    "note": "Completed symbol lane with reconciled synthetic evidence and checks.",
                    "artifact_path": run["symbol_workspaces"]["TEST"]["evidence"],
                    "evidence_ids": ["macro-source" if lane == "macro_transmission" else "symbol-source"],
                    "updated_at": "2026-08-01T12:20:00Z",
                }
            )
        run["batch_status"] = "complete"
        run["updated_at"] = "2026-08-01T12:20:00Z"
        run_path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
        run_batch(root, ["verify", *common, "--final"])
        artifact = run["symbol_workspaces"]["TEST"]["evidence"]
        terminal_update = run_batch(
            root,
            [
                "set-lane", *common,
                "--symbol", "TEST",
                "--lane", "monitoring",
                "--status", "complete",
                "--note", "Attempt to overwrite an already terminal checkpoint record.",
                "--artifact-path", artifact,
                "--evidence-id", "symbol-source",
                "--updated-at", "2026-08-01T12:21:00Z",
            ],
            expected=1,
        )
        assert "without a correction" in terminal_update.stderr
        run_batch(
            root,
            [
                "correct-lane", *common,
                "--symbol", "TEST",
                "--lane", "monitoring",
                "--status", "complete",
                "--note", "Corrected monitoring details after central review found a material omission.",
                "--artifact-path", artifact,
                "--evidence-id", "symbol-source",
                "--correction-reason", "Central review found that the original terminal note omitted a monitoring trigger.",
                "--updated-at", "2026-08-01T12:21:00Z",
            ],
        )
        run_batch(root, ["verify", *common, "--final"])
        corrections = root / "research/batches/2026-08-01T120000Z/CORRECTIONS.jsonl"
        assert len([line for line in corrections.read_text(encoding="utf-8").splitlines() if line]) == 1
        run = json.loads(run_path.read_text(encoding="utf-8"))
        run["symbol_lanes"]["TEST"]["valuation_scenarios"]["status"] = "in_progress"
        run_path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
        rejected = run_batch(root, ["verify", *common, "--final"], expected=1)
        assert "nonterminal TEST lane: valuation_scenarios" in rejected.stderr


def test_final_report_reconciliation() -> None:
    with tempfile.TemporaryDirectory(prefix="analyst-symbol-report-") as directory:
        root = Path(directory)
        (root / "SYMBOLS.md").write_text(
            "# Symbols\n\n## Active Universe\n\n"
            "| Symbol | Instrument | Asset class | Description | Status |\n"
            "|---|---|---|---|---|\n"
            "| `TEST` | Test Corp | Stock | Synthetic test. | Observe |\n",
            encoding="utf-8",
        )
        fixture_root = root / "evaluations/symbol-research"
        fixture_root.mkdir(parents=True)
        shutil.copy2(REPO_ROOT / "evaluations/symbol-research/cases.jsonl", fixture_root / "cases.jsonl")
        run_script(SYNC_SCRIPT, ["--sync", "--repo-root", str(root)])
        common = ["--repo-root", str(root), "--batch-id", "2026-08-01T120000Z"]
        run_batch(
            root,
            [
                "init", *common,
                "--decision-cutoff", "2026-08-01T12:00:00Z",
                "--created-at", "2026-08-01T12:01:00Z",
            ],
        )
        checkpoint_path = root / "research/batches/2026-08-01T120000Z/RUN.json"
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        complete_batch_artifacts(root, checkpoint)
        for stage, record in checkpoint["shared_stages"].items():
            record.update(
                {
                    "status": "complete",
                    "note": "Completed shared stage with reconciled synthetic primary evidence.",
                    "artifact_path": checkpoint["shared_workspaces"][stage],
                    "evidence_ids": [f"shared-{stage}-evidence"],
                    "updated_at": "2026-08-01T12:20:00Z",
                }
            )
        for lane, record in checkpoint["symbol_lanes"]["TEST"].items():
            record.update(
                {
                    "status": "complete",
                    "note": "Completed terminal symbol lane with reconciled synthetic evidence.",
                    "artifact_path": checkpoint["symbol_workspaces"]["TEST"]["evidence"],
                    "evidence_ids": ["macro-source" if lane == "macro_transmission" else "symbol-source"],
                    "updated_at": "2026-08-01T12:20:00Z",
                }
            )
        checkpoint["updated_at"] = "2026-08-01T12:20:00Z"
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")
        state = complete_state()
        draft = root / checkpoint["symbol_workspaces"]["TEST"]["latest_draft"]
        draft.write_text(render_document(state), encoding="utf-8")
        decision = root / checkpoint["symbol_workspaces"]["TEST"]["decision_draft"]
        decision.write_text(
            json.dumps(
                {
                    "price_status": "100 USD synthetic close",
                    "horizon_view": "Four registered synthetic distributions",
                    "decision": "Observe",
                    "confidence": "Medium",
                    "next_review": "2026-08-02",
                }
            ),
            encoding="utf-8",
        )
        run_script(
            HISTORY_SCRIPT,
            [
                "snapshot", *common,
                "--symbol", "TEST",
                "--decision-cutoff", "2026-08-01T12:00:00Z",
                "--recorded-at", "2026-08-01T12:20:00Z",
                "--draft", str(draft),
                "--decision-record", str(decision),
            ],
        )
        snapshotted_correction = run_batch(
            root,
            [
                "correct-lane", *common,
                "--symbol", "TEST",
                "--lane", "monitoring",
                "--status", "complete",
                "--note", "Attempted correction after the immutable snapshot was created.",
                "--artifact-path", checkpoint["symbol_workspaces"]["TEST"]["evidence"],
                "--evidence-id", "symbol-source",
                "--correction-reason", "A post-snapshot change must use a new corrective batch instead.",
                "--updated-at", "2026-08-01T12:20:30Z",
            ],
            expected=1,
        )
        assert "create a new corrective batch" in snapshotted_correction.stderr
        run_batch(root, ["finalize", *common, "--updated-at", "2026-08-01T12:21:00Z"])
        report_state = {
            "schema_version": "symbol-research-report-state-v1",
            "batch_id": "2026-08-01T120000Z",
            "batch_status": "complete",
            "decision_cutoff": "2026-08-01T12:00:00Z",
            "access_completed_at": "2026-08-01T12:21:00Z",
            "reporting_currency": "USD",
            "research_depth_contract": "full-depth-v1",
            "batch_checkpoint": "research/batches/2026-08-01T120000Z/RUN.json",
            "shared_macro_status": "complete",
            "evidence_record_count": 2,
            "forecast_registration_count": 4,
            "active_symbols": ["TEST"],
            "symbol_states": {"TEST": "complete"},
        }
        report = (
            "# Symbol Research Report\n\n<!-- analyst-template: report-v3 -->\n\n"
            "## Batch Metadata\n\n"
            "- Batch ID / decision cutoff: 2026-08-01T120000Z / 2026-08-01T12:00:00Z\n"
            "- Access completion time: 2026-08-01T12:21:00Z\n"
            "- Batch status: complete\n"
            "- Batch checkpoint: research/batches/2026-08-01T120000Z/RUN.json\n"
            "- Shared macro artifact: research/batches/2026-08-01T120000Z/MACRO.md\n"
            "- Reporting currency: USD\n"
            "- Leverage: unlevered plus 5x gross linear before costs\n"
            "- Evidence packets / forecast registrations: 2 / 4\n\n"
            "## Machine-Readable Batch State\n\n```json\n"
            f"{json.dumps(report_state, indent=2)}\n```\n\n"
            "## Batch Completion Ledger\n\n"
            "| Symbol | Research state | Identity | Fundamentals/product | Valuation/scenarios | Thesis | Forecast | Downside/5x |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| `TEST` | complete | complete | complete | complete | complete | complete | complete |\n\n"
            "## Shared Macro Regime\n\nThe shared synthetic regime and transmission are complete.\n\n"
            "## Universe And Current Evidence\n\n"
            "| Symbol | Instrument | USD price/value | Price as of | News/evidence | Current view | Detail |\n"
            "|---|---|---:|---|---|---|---|\n"
            "| `TEST` | TEST common stock on Synthetic Exchange | 100 | 2026-08-01T12:00:00Z | complete | observe | [Latest](research/symbols/TEST/LATEST.md) |\n\n"
            "## Directional Probabilities\n\nThe four horizons are 1 trading day, 2 weeks, 1 month, and 2 months.\n\n"
            "| Symbol | 1 trading day | 2 weeks | 1 month | 2 months | Confidence |\n"
            "|---|---:|---:|---:|---:|---|\n"
            "| `TEST` | 40/35/25 | 40/35/25 | 40/35/25 | 40/35/25 | Medium |\n\n"
            "## Downside And 5x Exposure\n\n"
            "| Symbol | Reference capital USD | Unlevered downside | Approx. 5x gross downside | Margin/liquidation status |\n"
            "|---|---:|---:|---:|---|\n"
            "| `TEST` | 1000 | -120 | -600 | Costs and liquidation disclosed |\n\n"
            "## Batch Limitations\n\nSynthetic executable fixture only.\n"
        )
        report_path = root / "REPORT.md"
        report_path.write_text(report, encoding="utf-8")
        run_script(CHECK_SCRIPT, ["--repo-root", str(root)])
        report_path.write_text(report.replace("40/35/25 | 40/35/25", "50/30/20 | 40/35/25", 1), encoding="utf-8")
        rejected = run_script(CHECK_SCRIPT, ["--repo-root", str(root)], expected=1)
        assert "does not reconcile with LATEST.md" in rejected.stderr
        report_path.write_text(
            report.replace("| `TEST` | TEST common stock on Synthetic Exchange | 100 |", "| `TEST` | TEST common stock on Synthetic Exchange | 101 |", 1),
            encoding="utf-8",
        )
        summary_rejected = run_script(CHECK_SCRIPT, ["--repo-root", str(root)], expected=1)
        assert "summary values do not reconcile" in summary_rejected.stderr
        report_path.write_text(report.replace('"evidence_record_count": 2', '"evidence_record_count": 3', 1), encoding="utf-8")
        count_rejected = run_script(CHECK_SCRIPT, ["--repo-root", str(root)], expected=1)
        assert "evidence_record_count does not reconcile" in count_rejected.stderr


def main() -> int:
    test_contract()
    test_batch_checkpoint()
    test_final_report_reconciliation()
    print(
        "PASS symbol research v3: terminal depth, cutoff integrity, forecast/risk "
        "reconciliation, dependency isolation, and resumable batch state"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
