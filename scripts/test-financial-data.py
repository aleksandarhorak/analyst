#!/usr/bin/env python3
"""Deterministic regression tests for point-in-time financial-data adapters."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER = (
    REPO_ROOT
    / ".codex/skills/acquire-point-in-time-financial-data/scripts/acquire_financial_data.py"
)
FIXTURES = REPO_ROOT / "evaluations/financial-data/fixtures"
COMMON = [
    "--decision-cutoff",
    "2025-08-01T23:59:59Z",
    "--retrieved-at",
    "2025-08-01T12:01:00Z",
]


def run(arguments: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(ADAPTER), *arguments],
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


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="analyst-data-test-") as directory:
        output = Path(directory)

        sec_path = output / "sec.json"
        run(
            [
                "sec-companyfacts",
                "--instrument-id", "sec:cik:0000320193",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *COMMON,
                "--input-file", str(FIXTURES / "sec_companyfacts.json"),
                "--output", str(sec_path),
                "--cik", "320193",
                "--taxonomy", "us-gaap",
                "--concept", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "--unit", "USD",
            ]
        )
        sec = read(sec_path)
        assert len(sec["observations"]) == 1
        assert sec["observations"][0]["unit"] == "USD"
        assert sec["request"]["cik"] == "0000320193"
        run(["validate", str(sec_path)])

        mismatch = run(
            [
                "sec-companyfacts",
                "--instrument-id", "sec:cik:0000320193",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                *COMMON,
                "--input-file", str(FIXTURES / "sec_companyfacts.json"),
                "--cik", "320193",
                "--taxonomy", "us-gaap",
                "--concept", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "--unit", "EUR",
            ],
            expected=2,
        )
        assert "no observations" in mismatch.stderr

        fred_path = output / "fred.json"
        run(
            [
                "fred-observations",
                "--instrument-id", "fred:CPIAUCSL",
                "--symbol", "CPIAUCSL",
                "--asset-class", "macro-series",
                *COMMON,
                "--input-file", str(FIXTURES / "fred_observations.json"),
                "--output", str(fred_path),
                "--series-id", "CPIAUCSL",
                "--realtime-start", "2025-01-01",
                "--realtime-end", "2025-06-30",
                "--unit", "index",
                "--frequency", "monthly",
            ]
        )
        fred = read(fred_path)
        assert [item["value"] for item in fred["observations"]] == [2.4, 2.1]
        assert fred["observations"][0]["revision"]["realtime_end"] == "2025-02-09"
        assert any("missing-value" in flag for flag in fred["quality"]["flags"])

        future = run(
            [
                "fred-observations",
                "--instrument-id", "fred:CPIAUCSL",
                "--symbol", "CPIAUCSL",
                "--asset-class", "macro-series",
                "--decision-cutoff", "2025-02-01T00:00:00Z",
                "--retrieved-at", "2025-08-01T12:01:00Z",
                "--input-file", str(FIXTURES / "fred_observations.json"),
                "--series-id", "CPIAUCSL",
                "--realtime-start", "2025-01-01",
                "--realtime-end", "2025-06-30",
                "--unit", "index",
                "--frequency", "monthly",
            ],
            expected=2,
        )
        assert "after-cutoff evidence" in future.stderr

        cftc_path = output / "cftc.json"
        run(
            [
                "cftc-cot",
                "--instrument-id", "cftc:083731",
                "--symbol", "ARABICA",
                "--asset-class", "commodity-future",
                "--venue", "IFUS",
                *COMMON,
                "--input-file", str(FIXTURES / "cftc_cot.json"),
                "--output", str(cftc_path),
                "--contract-market-code", "083731",
                "--published-at", "2025-08-01T19:30:00Z",
                "--field", "open_interest_all",
                "--field", "m_money_positions_long_all",
            ]
        )
        cftc = read(cftc_path)
        assert len(cftc["observations"]) == 2
        assert cftc["observations"][0]["as_of"] == "2025-07-29"
        assert cftc["observations"][0]["published_at"] == "2025-08-01T19:30:00Z"

        provider_path = output / "provider.json"
        run(
            [
                "provider",
                "--instrument-id", "figi:BBG000B9XRY4",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *COMMON,
                "--input-file", str(FIXTURES / "provider_price.json"),
                "--output", str(provider_path),
                "--request-id", "price-aapl-20250801",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "60",
            ]
        )
        provider = read(provider_path)
        assert provider["observations"][0]["metadata"]["latency"] == "real_time"
        assert "api_key" not in json.dumps(provider).lower()

        wrong_identity = run(
            [
                "provider",
                "--instrument-id", "figi:WRONG",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                *COMMON,
                "--input-file", str(FIXTURES / "provider_price.json"),
                "--request-id", "price-aapl-20250801",
            ],
            expected=1,
        )
        assert "identity mismatch" in wrong_identity.stderr

    print("PASS financial data adapters: official fixtures, cutoff, units, identity, and secrets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
