#!/usr/bin/env python3
"""Regression tests for the executable financial-agent evaluation runner."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts/run-financial-evals.py"
CASES = REPO_ROOT / "evaluations/financial-agent/cases.jsonl"
RESPONSES = REPO_ROOT / "evaluations/financial-agent/fixtures/passing-responses.jsonl"
CANDIDATE = REPO_ROOT / "evaluations/financial-agent/fixtures/replay_candidate.py"


def run(arguments: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(RUNNER), *arguments],
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


def common(output: Path, run_id: str) -> list[str]:
    return [
        "--cases", str(CASES),
        "--output-dir", str(output),
        "--run-id", run_id,
        "--model-version", "synthetic-fixture-v1",
        "--tool-version", "evaluation-runner-v1",
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="analyst-eval-test-") as directory:
        root = Path(directory)
        file_run = root / "file-run"
        accepted = run([*common(file_run, "passing-file"), "--responses", str(RESPONSES)])
        assert accepted.stdout.startswith("ACCEPT")
        result = json.loads((file_run / "results.json").read_text(encoding="utf-8"))
        assert result["decision"] == "accept"
        assert result["case_count"] == 28
        assert result["critical_failure_count"] == 0
        assert result["score"] == 1.0
        assert result["repeat_count"] == 1
        assert result["score_min"] == result["score_max"] == 1.0
        assert result["score_variance"] == 0.0
        assert result["holdout_cases_sha256"] is None
        assert result["rubric_sha256"]
        assert result["scorer_sha256"]
        assert "assertions" not in result["candidate_input_fields"]
        assert all(case["candidate_input_sha256"] for case in result["cases"])
        assert (file_run / "summary.md").is_file()
        overwrite = run(
            [*common(file_run, "overwrite"), "--responses", str(RESPONSES)], expected=1
        )
        assert "already exists" in overwrite.stderr

        command_run = root / "command-run"
        run(
            [
                *common(command_run, "passing-command"),
                "--repeat-count", "2",
                "--candidate-command", sys.executable, str(CANDIDATE),
            ]
        )
        command_result = json.loads((command_run / "results.json").read_text(encoding="utf-8"))
        assert command_result["decision"] == "accept"
        assert command_result["repeat_count"] == 2
        assert len(command_result["runs"]) == 2
        assert command_result["score_variance"] == 0.0
        assert command_result["candidate_command_sha256"]

        broken_responses = []
        for line in RESPONSES.read_text(encoding="utf-8").splitlines():
            if line.strip():
                broken_responses.append(json.loads(line))
        broken_responses[0]["text"] = "Use the old value as current and publish it."
        broken_path = root / "broken.jsonl"
        broken_path.write_text(
            "".join(json.dumps(value) + "\n" for value in broken_responses), encoding="utf-8"
        )
        rejected_dir = root / "rejected"
        rejected = run(
            [*common(rejected_dir, "critical-failure"), "--responses", str(broken_path)],
            expected=2,
        )
        assert rejected.stdout.startswith("REJECT")
        rejected_result = json.loads((rejected_dir / "results.json").read_text(encoding="utf-8"))
        assert rejected_result["critical_failure_count"] >= 1
        assert rejected_result["decision"] == "reject"

        comparison_dir = root / "comparison"
        run(
            [
                *common(comparison_dir, "baseline-comparison"),
                "--baseline-responses", str(broken_path),
                "--responses", str(RESPONSES),
            ]
        )
        comparison = json.loads((comparison_dir / "results.json").read_text(encoding="utf-8"))
        assert comparison["baseline"]["decision"] == "reject"
        assert comparison["delta_vs_baseline"] > 0
        assert comparison["baseline_responses_sha256"]

        malformed_cases = root / "malformed-cases.jsonl"
        malformed_case = json.loads(CASES.read_text(encoding="utf-8").splitlines()[0])
        malformed_case["assertions"][0]["critical"] = "yes"
        malformed_cases.write_text(json.dumps(malformed_case) + "\n", encoding="utf-8")
        one_response = root / "one-response.jsonl"
        one_response.write_text(
            RESPONSES.read_text(encoding="utf-8").splitlines()[0] + "\n", encoding="utf-8"
        )
        malformed = run(
            [
                "--cases", str(malformed_cases),
                "--output-dir", str(root / "malformed"),
                "--run-id", "malformed",
                "--model-version", "synthetic",
                "--tool-version", "test",
                "--responses", str(one_response),
            ],
            expected=1,
        )
        assert "critical must be boolean" in malformed.stderr

    print(
        "PASS financial evaluations: anti-leakage input, repeats, baseline comparison, "
        "metadata, validation, dimensions, and critical gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
