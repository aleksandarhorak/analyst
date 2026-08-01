#!/usr/bin/env python3
"""Regression tests for symbol template migration and immutable snapshots."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = REPO_ROOT / ".codex/skills/research-symbol-watchlist/scripts"
MIGRATE = SKILL_SCRIPTS / "migrate_symbol_templates.py"
HISTORY = SKILL_SCRIPTS / "symbol_research_history.py"


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

        draft = root / "draft.md"
        draft.write_text(latest.read_text(encoding="utf-8"), encoding="utf-8")
        decision_record = root / "decision.json"
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

    print("PASS symbol history: preserving migration, exclusive snapshots, chain, rows, and tamper detection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
