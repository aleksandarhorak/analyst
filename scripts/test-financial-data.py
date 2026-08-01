#!/usr/bin/env python3
"""Deterministic regression tests for point-in-time financial-data adapters."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER = (
    REPO_ROOT
    / ".codex/skills/acquire-point-in-time-financial-data/scripts/acquire_financial_data.py"
)
PREFLIGHT = REPO_ROOT / "scripts/preflight-provider.py"
FIXTURES = REPO_ROOT / "evaluations/financial-data/fixtures"
COMMON = [
    "--decision-cutoff",
    "2025-08-01T23:59:59Z",
    "--retrieved-at",
    "2025-08-01T12:01:00Z",
]
PROVIDER_COMMON = [
    "--decision-cutoff",
    "2025-08-01T12:00:30Z",
    "--retrieved-at",
    "2025-08-01T12:01:00Z",
]


def run(
    arguments: list[str], expected: int = 0, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(ADAPTER), *arguments],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
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
                "--instrument-id", "sec:cik:0000320193:AAPL",
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
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
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

        wrong_sec_fixture = json.loads((FIXTURES / "sec_companyfacts.json").read_text(encoding="utf-8"))
        wrong_sec_fixture["entityName"] = "Different Issuer"
        wrong_sec_path = output / "wrong-sec.json"
        wrong_sec_path.write_text(json.dumps(wrong_sec_fixture), encoding="utf-8")
        wrong_sec = run(
            [
                "sec-companyfacts",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *COMMON,
                "--input-file", str(wrong_sec_path),
                "--cik", "320193",
                "--taxonomy", "us-gaap",
                "--concept", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "--unit", "USD",
            ],
            expected=1,
        )
        assert "issuer name" in wrong_sec.stderr

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
                "--registry-key", "ARABICA-ICE-KC",
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
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--input-file", str(FIXTURES / "provider_price.json"),
                "--output", str(provider_path),
                "--request-id", "price-aapl-20250801",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "60",
            ]
        )
        provider = read(provider_path)
        assert provider["observations"][0]["metadata"]["latency"] == "real_time"
        assert "resolution_status" not in provider["request"]["instrument"]
        assert "api_key" not in json.dumps(provider).lower()

        leaky_packet = json.loads(json.dumps(provider))
        leaky_packet["request"]["api_key"] = "synthetic-must-not-persist"
        leaky_path = output / "leaky.json"
        leaky_path.write_text(json.dumps(leaky_packet), encoding="utf-8")
        leaky = run(["validate", str(leaky_path)], expected=1)
        assert "sensitive credential key" in leaky.stderr

        news_path = output / "news.json"
        run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *COMMON,
                "--input-file", str(FIXTURES / "provider_news.json"),
                "--output", str(news_path),
                "--request-id", "news-aapl-20250801",
                "--kind", "news",
                "--maximum-age-seconds", "86400",
            ]
        )
        news = read(news_path)
        assert news["observations"][0]["metadata"]["publisher"] == "Synthetic Wire"
        assert news["observations"][0]["metadata"]["correction_status"] == "original"
        assert news["observations"][0]["metadata"]["document_id"] == "synthetic-document-1"

        price_fixture = json.loads((FIXTURES / "provider_price.json").read_text(encoding="utf-8"))
        wrong_identity_fixture = json.loads(json.dumps(price_fixture))
        wrong_identity_fixture["instrument"]["symbol"] = "MSFT"
        wrong_identity_path = output / "wrong-provider-identity.json"
        wrong_identity_path.write_text(json.dumps(wrong_identity_fixture), encoding="utf-8")
        rejected_output_path = output / "must-not-write-rejected-packet.json"
        wrong_identity = run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--input-file", str(wrong_identity_path),
                "--output", str(rejected_output_path),
                "--request-id", "price-aapl-20250801",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "60",
            ],
            expected=1,
        )
        assert "identity mismatch" in wrong_identity.stderr
        assert not rejected_output_path.exists()

        for field, value, expected_text in (
            ("currency", "EUR", "currency mismatch"),
            ("session", "extended", "session mismatch"),
        ):
            variant = json.loads(json.dumps(price_fixture))
            variant["observations"][0][field] = value
            variant_path = output / f"wrong-{field}.json"
            variant_path.write_text(json.dumps(variant), encoding="utf-8")
            result = run(
                [
                    "provider",
                    "--instrument-id", "sec:cik:0000320193:AAPL",
                    "--symbol", "AAPL",
                    "--asset-class", "equity",
                    "--venue", "XNAS",
                    *PROVIDER_COMMON,
                    "--input-file", str(variant_path),
                    "--request-id", "price-aapl-20250801",
                    "--kind", "price",
                    "--currency", "USD",
                    "--session", "regular",
                    "--maximum-age-seconds", "60",
                ],
                expected=1,
            )
            assert expected_text in result.stderr

        stale = run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--input-file", str(FIXTURES / "provider_price.json"),
                "--request-id", "price-aapl-20250801",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "1",
            ],
            expected=1,
        )
        assert "is stale" in stale.stderr

        boundary_path = output / "freshness-boundary.json"
        run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--input-file", str(FIXTURES / "provider_price.json"),
                "--output", str(boundary_path),
                "--request-id", "price-aapl-20250801",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "32",
            ]
        )

        provider_process = FIXTURES / "provider_process.py"
        process_command = [str(Path(sys.executable).resolve()), str(provider_process)]
        process_env = os.environ.copy()
        process_env["SYNTHETIC_UNRELATED_SECRET"] = "must-not-reach-child"
        process_path = output / "process-provider.json"
        run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--output", str(process_path),
                "--request-id", "process-price",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "0",
                "--command", *process_command,
            ],
            env=process_env,
        )
        assert read(process_path)["source"]["authority"] == "synthetic-process-provider"

        preflight = subprocess.run(
            [
                str(Path(sys.executable).resolve()),
                str(PREFLIGHT),
                "--registry-key", "AAPL",
                "--price-maximum-age-seconds", "0",
                "--news-maximum-age-seconds", "0",
                "--command", *process_command,
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=process_env,
        )
        assert preflight.returncode == 0, preflight.stderr
        assert "PASS price" in preflight.stdout
        assert "PASS news" in preflight.stdout
        assert "temporary packets removed" in preflight.stdout

        allowed_env = os.environ.copy()
        allowed_env["SYNTHETIC_PROVIDER_KEY"] = "synthetic-provider-value"
        allowed_path = output / "allowed-env-provider.json"
        run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--output", str(allowed_path),
                "--request-id", "allowed-env-price",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "0",
                "--provider-env", "SYNTHETIC_PROVIDER_KEY",
                "--command", *process_command,
            ],
            env=allowed_env,
        )

        relative_command = run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--request-id", "relative-command",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "0",
                "--command", "python3", str(provider_process),
            ],
            expected=1,
        )
        assert "absolute executable path" in relative_command.stderr

        timeout = run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--timeout", "0.05",
                "--request-id", "timeout-price",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "0",
                "--command", *process_command,
            ],
            expected=1,
        )
        assert "exceeded timeout" in timeout.stderr

        nonzero = run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--request-id", "nonzero-price",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "0",
                "--command", *process_command,
            ],
            expected=1,
        )
        assert "stderr_sha256=" in nonzero.stderr
        assert "confidential diagnostic" not in nonzero.stderr

        invalid_json = run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--request-id", "invalid-json-price",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "0",
                "--command", *process_command,
            ],
            expected=1,
        )
        assert "valid UTF-8 JSON" in invalid_json.stderr

        for field in ("event_time", "published_at", "as_of"):
            future_fixture = json.loads(json.dumps(price_fixture))
            future_fixture["observations"][0][field] = "2025-08-01T12:00:31Z"
            future_path = output / f"future-{field}.json"
            future_path.write_text(json.dumps(future_fixture), encoding="utf-8")
            future_result = run(
                [
                    "provider",
                    "--instrument-id", "sec:cik:0000320193:AAPL",
                    "--symbol", "AAPL",
                    "--asset-class", "equity",
                    "--venue", "XNAS",
                    *PROVIDER_COMMON,
                    "--input-file", str(future_path),
                    "--request-id", "price-aapl-20250801",
                    "--kind", "price",
                    "--currency", "USD",
                    "--session", "regular",
                    "--maximum-age-seconds", "60",
                ],
                expected=1,
            )
            assert f"{field} is after" in future_result.stderr

        extra_provider = json.loads(json.dumps(price_fixture))
        extra_provider["unexpected"] = True
        extra_provider_path = output / "extra-provider-response.json"
        extra_provider_path.write_text(json.dumps(extra_provider), encoding="utf-8")
        extra_provider_result = run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--input-file", str(extra_provider_path),
                "--request-id", "price-aapl-20250801",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "60",
            ],
            expected=1,
        )
        assert "provider response has unsupported fields" in extra_provider_result.stderr

        extra_observation = json.loads(json.dumps(price_fixture))
        extra_observation["observations"][0]["unexpected"] = True
        extra_observation_path = output / "extra-provider-observation.json"
        extra_observation_path.write_text(json.dumps(extra_observation), encoding="utf-8")
        extra_observation_result = run(
            [
                "provider",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                *PROVIDER_COMMON,
                "--input-file", str(extra_observation_path),
                "--request-id", "price-aapl-20250801",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "60",
            ],
            expected=1,
        )
        assert "provider observation 0 has unsupported fields" in extra_observation_result.stderr

        same_day = run(
            [
                "sec-companyfacts",
                "--instrument-id", "sec:cik:0000320193:AAPL",
                "--symbol", "AAPL",
                "--asset-class", "equity",
                "--venue", "XNAS",
                "--decision-cutoff", "2025-04-25T23:59:59Z",
                "--retrieved-at", "2025-08-01T12:01:00Z",
                "--input-file", str(FIXTURES / "sec_companyfacts.json"),
                "--cik", "320193",
                "--taxonomy", "us-gaap",
                "--concept", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "--unit", "USD",
            ],
            expected=2,
        )
        assert "cutoff-day date-granularity" in same_day.stderr

        malformed = json.loads(json.dumps(provider))
        malformed["unexpected"] = True
        malformed_path = output / "malformed.json"
        malformed_path.write_text(json.dumps(malformed), encoding="utf-8")
        malformed_result = run(["validate", str(malformed_path)], expected=1)
        assert "unsupported fields" in malformed_result.stderr

        nested_malformed = json.loads(json.dumps(provider))
        nested_malformed["observations"][0]["uncontracted"] = "reject"
        nested_path = output / "nested-malformed.json"
        nested_path.write_text(json.dumps(nested_malformed), encoding="utf-8")
        nested_result = run(["validate", str(nested_path)], expected=1)
        assert "observation 0 has unsupported fields" in nested_result.stderr

        unresolved = run(
            [
                "provider",
                "--instrument-id", "alias:GOLD",
                "--symbol", "GOLD",
                "--asset-class", "commodity",
                *PROVIDER_COMMON,
                "--input-file", str(FIXTURES / "provider_price.json"),
                "--request-id", "price-aapl-20250801",
                "--kind", "price",
                "--currency", "USD",
                "--session", "regular",
                "--maximum-age-seconds", "60",
            ],
            expected=1,
        )
        assert "is unresolved" in unresolved.stderr

    print(
        "PASS financial data adapters: registry, exact schemas, complete timestamps, "
        "freshness, process isolation, bounded diagnostics, validate-before-write, and secrets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
