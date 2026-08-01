#!/usr/bin/env python3
"""Regression tests for immutable forecast registration and calibration math."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / ".codex/skills/calibrate-financial-forecasts/scripts/forecast_ledger.py"
PACKET_ID = "sha256:" + "a" * 64
OUTCOME_PACKET_ID = "sha256:" + "b" * 64


def run(arguments: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(LEDGER), *arguments],
        cwd=REPO_ROOT,
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


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def forecast(forecast_id: str, probabilities: dict[str, float], horizon: str) -> dict:
    return {
        "forecast_id": forecast_id,
        "created_at": "2025-08-01T12:01:00Z",
        "decision_cutoff": "2025-08-01T12:00:00Z",
        "target_at": "2025-08-08T20:00:00Z",
        "instrument_id": "figi:BBG000B9XRY4",
        "symbol": "AAPL",
        "asset_class": "equity",
        "horizon": horizon,
        "regime": "synthetic-test",
        "start_value": 200.0,
        "unit": "USD_per_share_total_return_basis",
        "currency": "USD",
        "flat_band": {"lower_return": -0.01, "upper_return": 0.01},
        "probabilities": probabilities,
        "method_version": "fixture-v1",
        "evidence_packet_ids": [PACKET_ID],
    }


def outcome(forecast_id: str, realized_return: float) -> dict:
    return {
        "forecast_id": forecast_id,
        "resolved_at": "2025-08-08T20:05:00Z",
        "outcome_as_of": "2025-08-08T20:00:00Z",
        "realized_return": realized_return,
        "outcome_packet_id": OUTCOME_PACKET_ID,
        "corporate_action_treatment": "Synthetic total-return series; no action",
        "fx_treatment": "Native USD; no conversion",
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="analyst-forecast-test-") as directory:
        root = Path(directory)
        forecasts = root / "forecasts.jsonl"
        outcomes = root / "outcomes.jsonl"
        first = root / "first.json"
        second = root / "second.json"
        first_outcome = root / "first-outcome.json"
        second_outcome = root / "second-outcome.json"
        score_path = root / "score.json"

        write(first, forecast("forecast-1", {"up": 0.6, "flat": 0.2, "down": 0.2}, "1-week"))
        write(second, forecast("forecast-2", {"up": 0.1, "flat": 0.2, "down": 0.7}, "1-week"))
        run(["register", "--forecasts", str(forecasts), "--record", str(first)])
        run(["register", "--forecasts", str(forecasts), "--record", str(second)])
        duplicate = run(
            ["register", "--forecasts", str(forecasts), "--record", str(first)], expected=1
        )
        assert "already exists" in duplicate.stderr

        write(first_outcome, outcome("forecast-1", 0.05))
        write(second_outcome, outcome("forecast-2", 0.0))
        run(
            [
                "resolve", "--forecasts", str(forecasts), "--outcomes", str(outcomes),
                "--record", str(first_outcome),
            ]
        )
        run(
            [
                "resolve", "--forecasts", str(forecasts), "--outcomes", str(outcomes),
                "--record", str(second_outcome),
            ]
        )
        run(["verify", "--forecasts", str(forecasts), "--outcomes", str(outcomes)])
        run(
            [
                "score", "--forecasts", str(forecasts), "--outcomes", str(outcomes),
                "--output", str(score_path),
            ]
        )
        score = json.loads(score_path.read_text(encoding="utf-8"))
        all_metrics = score["groups"]["all"]
        assert score["coverage"] == 1.0
        assert math.isclose(all_metrics["mean_brier"], 0.69, abs_tol=1e-12)
        assert math.isclose(
            all_metrics["mean_log_loss"], (-math.log(0.6) - math.log(0.2)) / 2, abs_tol=1e-12
        )
        assert all_metrics["accuracy"] == 0.5
        assert sum(bucket["count"] for bucket in all_metrics["reliability"]["up"]) == 2

        tampered = json.loads(forecasts.read_text(encoding="utf-8").splitlines()[0])
        tampered["start_value"] = 201.0
        forecasts.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
        broken = run(
            ["verify", "--forecasts", str(forecasts), "--outcomes", str(outcomes)], expected=1
        )
        assert "hash mismatch" in broken.stderr

    print("PASS forecast ledgers: append-only IDs, hashes, outcomes, Brier, log loss, and bins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
