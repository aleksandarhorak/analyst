#!/usr/bin/env python3
"""Regression tests for immutable forecast registration and calibration math."""

from __future__ import annotations

import json
import hashlib
import math
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / ".codex/skills/calibrate-financial-forecasts/scripts/forecast_ledger.py"


def canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def evidence_packet(field: str, value: float, created_at: str, as_of: str) -> dict:
    packet = {
        "schema_version": "evidence-packet-v1",
        "packet_id": "",
        "created_at": created_at,
        "decision_cutoff": created_at,
        "adapter": {"name": "synthetic-test", "version": "1.0.0"},
        "source": {
            "authority": "Synthetic test source",
            "url": "https://example.test/evidence/synthetic",
            "retrieved_at": created_at,
            "raw_sha256": "c" * 64,
            "rights": "Synthetic fixture; unrestricted test use",
        },
        "request": {"purpose": "forecast ledger regression"},
        "instrument": {
            "id": "sec:cik:0000320193:AAPL",
            "symbol": "AAPL",
            "asset_class": "equity",
            "venue": "XNAS",
            "resolution_status": "resolved",
        },
        "observations": [
            {
                "claim_id": f"synthetic:{field}:{as_of}",
                "field": field,
                "value": value,
                "unit": "decimal_return" if field == "realized_return" else "USD_per_share",
                "currency": "USD",
                "classification": "derived_fact" if field == "realized_return" else "reported_fact",
                "event_time": as_of,
                "published_at": as_of,
                "as_of": as_of,
                "revision": {},
                "source_locator": f"synthetic.{field}",
            }
        ],
        "quality": {"status": "pass", "flags": [], "errors": []},
    }
    packet["packet_id"] = "sha256:" + hashlib.sha256(
        canonical({key: value for key, value in packet.items() if key != "packet_id"})
    ).hexdigest()
    return packet


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


def forecast(
    forecast_id: str, probabilities: dict[str, float], horizon: str, packet_id: str
) -> dict:
    return {
        "forecast_id": forecast_id,
        "created_at": "2025-08-01T12:01:00Z",
        "decision_cutoff": "2025-08-01T12:00:00Z",
        "target_at": "2025-08-08T20:00:00Z",
        "instrument_id": "sec:cik:0000320193:AAPL",
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
        "evidence_packet_ids": [packet_id],
    }


def outcome(forecast_id: str, realized_return: float, packet_id: str) -> dict:
    return {
        "forecast_id": forecast_id,
        "resolved_at": "2025-08-08T20:05:00Z",
        "outcome_as_of": "2025-08-08T20:00:00Z",
        "realized_return": realized_return,
        "outcome_packet_id": packet_id,
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
        forecast_packet_path = root / "forecast-packet.json"
        first_outcome_packet_path = root / "first-outcome-packet.json"
        second_outcome_packet_path = root / "second-outcome-packet.json"

        forecast_packet = evidence_packet(
            "start_value", 200.0, "2025-08-01T12:00:00Z", "2025-08-01T11:59:58Z"
        )
        first_outcome_packet = evidence_packet(
            "realized_return", 0.05, "2025-08-08T20:04:00Z", "2025-08-08T20:00:00Z"
        )
        second_outcome_packet = evidence_packet(
            "realized_return", 0.0, "2025-08-08T20:04:00Z", "2025-08-08T20:00:00Z"
        )
        write(forecast_packet_path, forecast_packet)
        write(first_outcome_packet_path, first_outcome_packet)
        write(second_outcome_packet_path, second_outcome_packet)
        write(
            first,
            forecast(
                "forecast-1", {"up": 0.6, "flat": 0.2, "down": 0.2},
                "1-week", forecast_packet["packet_id"],
            ),
        )
        write(
            second,
            forecast(
                "forecast-2", {"up": 0.1, "flat": 0.2, "down": 0.7},
                "1-week", forecast_packet["packet_id"],
            ),
        )
        register_args = ["--evidence-packet", str(forecast_packet_path)]
        run(["register", "--forecasts", str(forecasts), "--record", str(first), *register_args])
        run(["register", "--forecasts", str(forecasts), "--record", str(second), *register_args])
        duplicate = run(
            ["register", "--forecasts", str(forecasts), "--record", str(first), *register_args],
            expected=1,
        )
        assert "already exists" in duplicate.stderr

        phantom = root / "phantom.json"
        write(
            phantom,
            forecast(
                "forecast-phantom", {"up": 0.4, "flat": 0.3, "down": 0.3},
                "1-week", "sha256:" + "f" * 64,
            ),
        )
        phantom_result = run(
            [
                "register", "--forecasts", str(forecasts), "--record", str(phantom),
                "--evidence-packet", str(forecast_packet_path),
            ],
            expected=1,
        )
        assert "do not match evidence_packet_ids" in phantom_result.stderr

        write(first_outcome, outcome("forecast-1", 0.05, first_outcome_packet["packet_id"]))
        write(second_outcome, outcome("forecast-2", 0.0, second_outcome_packet["packet_id"]))
        mismatched_outcome = root / "mismatched-outcome.json"
        write(
            mismatched_outcome,
            outcome("forecast-1", 0.05, second_outcome_packet["packet_id"]),
        )
        mismatch_result = run(
            [
                "resolve", "--forecasts", str(forecasts), "--outcomes", str(outcomes),
                "--record", str(mismatched_outcome),
                "--outcome-packet", str(second_outcome_packet_path),
            ],
            expected=1,
        )
        assert "lacks the recorded realized_return" in mismatch_result.stderr
        run(
            [
                "resolve", "--forecasts", str(forecasts), "--outcomes", str(outcomes),
                "--record", str(first_outcome), "--outcome-packet", str(first_outcome_packet_path),
            ]
        )
        run(
            [
                "resolve", "--forecasts", str(forecasts), "--outcomes", str(outcomes),
                "--record", str(second_outcome), "--outcome-packet", str(second_outcome_packet_path),
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
        assert score["baseline"]["name"] == "uniform-reference-v1"
        assert score["baseline"]["metrics"]["resolved_count"] == 2
        assert "mean_brier" in score["baseline"]["candidate_minus_baseline"]
        assert score["limitations"]
        assert score["worst_cases"][0]["forecast_id"] == "forecast-2"

        tampered = json.loads(forecasts.read_text(encoding="utf-8").splitlines()[0])
        tampered["start_value"] = 201.0
        forecasts.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
        broken = run(
            ["verify", "--forecasts", str(forecasts), "--outcomes", str(outcomes)], expected=1
        )
        assert "hash mismatch" in broken.stderr

    print(
        "PASS forecast ledgers: evidence-linked appends, independent hashes, outcomes, "
        "baselines, sparse warnings, Brier, log loss, and bins"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
