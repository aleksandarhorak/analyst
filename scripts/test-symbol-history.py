#!/usr/bin/env python3
"""Regression tests for symbol template migration and immutable snapshots."""

from __future__ import annotations

import copy
import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = REPO_ROOT / ".codex/skills/research-symbol-watchlist/scripts"
MIGRATE = SKILL_SCRIPTS / "migrate_symbol_templates.py"
HISTORY = SKILL_SCRIPTS / "symbol_research_history.py"
BATCH = SKILL_SCRIPTS / "symbol_research_batch.py"
DEPTH_TEST = REPO_ROOT / "scripts/test-symbol-research.py"


def load_depth_helpers():
    spec = importlib.util.spec_from_file_location("symbol_depth_test_helpers", DEPTH_TEST)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load symbol depth test helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(script: Path, arguments: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(script), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != expected:
        raise AssertionError(
            f"expected exit {expected}, got {completed.returncode}\n"
            f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
        )
    return completed


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="analyst-symbol-history-") as directory:
        root = Path(directory)
        symbol_root = root / "research/symbols/TEST"
        history_root = symbol_root / "history"
        history_root.mkdir(parents=True)
        (root / "SYMBOLS.md").write_text(
            "# Symbols\n\n## Active Universe\n\n"
            "| Symbol | Instrument | Asset class | Description | Status |\n"
            "|---|---|---|---|---|\n"
            "| `TEST` | Test Corp | Stock | Synthetic test. | Observe |\n",
            encoding="utf-8",
        )
        (root / "REPORT.md").write_text(
            "# Symbol Research Report\n\n"
            "- Capacity: Impersonal research; no order authority\n\n"
            "UNIQUE REPORT CONTENT\n",
            encoding="utf-8",
        )
        latest = symbol_root / "LATEST.md"
        latest.write_text(
            "# TEST — Latest Research\n\n"
            "UNIQUE POPULATED RESEARCH MUST SURVIVE\n\n"
            "## Decision\n\n"
            "- Immutable snapshot: —\n",
            encoding="utf-8",
        )
        decisions = symbol_root / "DECISIONS.md"
        decisions.write_text(
            "# TEST — Decision History\n\n"
            "Existing explanation must survive.\n\n"
            "| Decision cutoff | Batch ID | Price/status | Horizon view | Decision | Confidence | Snapshot | Next review |\n"
            "|---|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )

        applied = run(MIGRATE, ["--apply", "--repo-root", str(root)])
        assert "3 file(s) changed" in applied.stdout
        assert "UNIQUE POPULATED RESEARCH MUST SURVIVE" in latest.read_text(encoding="utf-8")
        assert "Existing explanation must survive" in decisions.read_text(encoding="utf-8")
        assert "UNIQUE REPORT CONTENT" in (root / "REPORT.md").read_text(encoding="utf-8")
        run(MIGRATE, ["--check", "--repo-root", str(root)])
        reapplied = run(MIGRATE, ["--apply", "--repo-root", str(root)])
        assert "0 file(s) changed" in reapplied.stdout
        report_path = root / "REPORT.md"
        report_path.write_text(
            report_path.read_text(encoding="utf-8").replace(
                "- Evidence packets / forecast registrations: Not researched",
                "- Evidence packets / forecast registrations: 0 / 0",
            ),
            encoding="utf-8",
        )
        run(MIGRATE, ["--check", "--repo-root", str(root)])

        run(
            BATCH,
            [
                "init",
                "--repo-root", str(root),
                "--batch-id", "2025-08-01T120000Z",
                "--decision-cutoff", "2025-08-01T12:00:00Z",
                "--created-at", "2025-08-01T12:00:30Z",
            ],
        )
        checkpoint_path = root / "research/batches/2025-08-01T120000Z/RUN.json"
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        helpers = load_depth_helpers()
        helpers.complete_batch_artifacts(root, checkpoint)
        for stage, record in checkpoint["shared_stages"].items():
            record.update(
                {
                    "status": "complete",
                    "note": "Completed shared stage before the immutable synthetic snapshot.",
                    "artifact_path": checkpoint["shared_workspaces"][stage],
                    "evidence_ids": [f"shared-{stage}-evidence"],
                    "updated_at": "2025-08-01T12:00:45Z",
                }
            )
        for lane, record in checkpoint["symbol_lanes"]["TEST"].items():
            record.update(
                {
                    "status": "complete",
                    "note": "Completed synthetic terminal lane for immutable history testing.",
                    "artifact_path": checkpoint["symbol_workspaces"]["TEST"]["evidence"],
                    "evidence_ids": ["macro-source" if lane == "macro_transmission" else "symbol-source"],
                    "updated_at": "2025-08-01T12:00:45Z",
                }
            )
        checkpoint["updated_at"] = "2025-08-01T12:00:45Z"
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")

        state = helpers.complete_state()
        state.update(
            {
                "batch_id": "2025-08-01T120000Z",
                "decision_cutoff": "2025-08-01T12:00:00Z",
                "access_completed_at": "2025-08-01T12:01:00Z",
                "batch_checkpoint": "research/batches/2025-08-01T120000Z/RUN.json",
            }
        )
        for item in state["evidence"]:
            item["published_at"] = "2025-08-01T11:00:00Z"
            item["accessed_at"] = "2025-08-01T12:00:50Z"
        state["price_observation"]["observed_at"] = "2025-08-01T12:00:00Z"
        state["analysis_depth"]["news_catalysts"].update(
            {
                "window_start": "2025-07-25T00:00:00Z",
                "window_end": "2025-08-01T12:00:00Z",
            }
        )
        state["analysis_depth"]["monitoring"]["next_review"] = "2025-08-02T12:00:00Z"
        draft = root / checkpoint["symbol_workspaces"]["TEST"]["latest_draft"]
        draft.write_text(helpers.render_document(state), encoding="utf-8")
        decision_record = root / checkpoint["symbol_workspaces"]["TEST"]["decision_draft"]
        decision_record.write_text(
            json.dumps(
                {
                    "price_status": "100 USD at synthetic close",
                    "horizon_view": "1 week: 50/30/20",
                    "decision": "Observe",
                    "confidence": "Low",
                    "next_review": "2025-08-09",
                }
            ),
            encoding="utf-8",
        )
        snapshot_args = [
            "snapshot",
            "--repo-root", str(root),
            "--symbol", "TEST",
            "--batch-id", "2025-08-01T120000Z",
            "--decision-cutoff", "2025-08-01T12:00:00Z",
            "--recorded-at", "2025-08-01T12:01:00Z",
            "--draft", str(draft),
            "--decision-record", str(decision_record),
        ]
        spoofed_state = copy.deepcopy(state)
        spoofed_state["asset_class"] = "Other Product"
        draft.write_text(helpers.render_document(spoofed_state), encoding="utf-8")
        spoofed = run(HISTORY, snapshot_args, expected=1)
        assert "frozen active universe" in spoofed.stderr
        draft.write_text(helpers.render_document(state), encoding="utf-8")
        checkpoint["shared_stages"]["central_reconciliation"]["status"] = "in_progress"
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")
        premature = run(HISTORY, snapshot_args, expected=1)
        assert "central_reconciliation must be complete" in premature.stderr
        checkpoint["shared_stages"]["central_reconciliation"]["status"] = "complete"
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")
        run(HISTORY, snapshot_args)
        run(HISTORY, ["verify", "--repo-root", str(root), "--symbol", "TEST"])
        assert (history_root / "2025-08-01T120000Z.md").is_file()
        assert (history_root / "MANIFEST.jsonl").is_file()
        assert "history/2025-08-01T120000Z.md" in latest.read_text(encoding="utf-8")
        assert decisions.read_text(encoding="utf-8").count("| 2025-08-01T120000Z |") == 1

        duplicate = run(HISTORY, snapshot_args, expected=1)
        assert "batch already exists" in duplicate.stderr

        snapshot_path = history_root / "2025-08-01T120000Z.md"
        snapshot_path.write_text(snapshot_path.read_text(encoding="utf-8") + "tamper\n", encoding="utf-8")
        tampered = run(
            HISTORY,
            ["verify", "--repo-root", str(root), "--symbol", "TEST"],
            expected=1,
        )
        assert "snapshot hash mismatch" in tampered.stderr

    print(
        "PASS symbol history: preserving migration and populated metadata, exclusive "
        "snapshots, chain, rows, and tamper detection"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
