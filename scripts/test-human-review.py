#!/usr/bin/env python3
"""Deterministic regressions for blinded financial-agent human review records."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts/run-financial-evals.py"
REVIEWER = REPO_ROOT / "scripts/check-human-review.py"
CASES = REPO_ROOT / "evaluations/financial-agent/cases.jsonl"
RESPONSES = REPO_ROOT / "evaluations/financial-agent/fixtures/passing-responses.jsonl"


def run(command: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
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


def complete(path: Path, *, fail_first: bool = False) -> None:
    values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    for index, value in enumerate(values):
        value["scores"] = {dimension: 4 for dimension in value["scores"]}
        value["verdict"] = "fail" if fail_first and index == 0 else "pass"
        value["critical_failure"] = fail_first and index == 0
        value["reason"] = (
            "Material factual concern requires qualified adjudication."
            if fail_first and index == 0
            else "Evidence, calculations, uncertainty, safety, and usefulness meet the rubric."
        )
    path.write_text("".join(json.dumps(value) + "\n" for value in values), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="analyst-human-review-test-") as temporary:
        root = Path(temporary)
        run_dir = root / "run"
        run(
            [
                str(Path(sys.executable).resolve()),
                str(RUNNER),
                "--cases", str(CASES),
                "--responses", str(RESPONSES),
                "--output-dir", str(run_dir),
                "--run-id", "human-review-fixture",
                "--model-version", "synthetic-fixture",
                "--tool-version", "test",
            ]
        )
        results = run_dir / "results.json"
        review_bundle = run_dir / "review-bundle.jsonl"
        review_paths: list[Path] = []
        for reviewer_id in ("blind-r1", "blind-r2"):
            path = root / f"{reviewer_id}.jsonl"
            run(
                [
                    str(Path(sys.executable).resolve()),
                    str(REVIEWER),
                    "init",
                    "--results", str(results),
                    "--review-bundle", str(review_bundle),
                    "--reviewer-id", reviewer_id,
                    "--output", str(path),
                ]
            )
            review_paths.append(path)

        pending = run(
            [
                str(Path(sys.executable).resolve()),
                str(REVIEWER),
                "check",
                "--results", str(results),
                "--review-bundle", str(review_bundle),
                "--reviews", str(review_paths[0]),
                "--reviews", str(review_paths[1]),
            ],
            expected=1,
        )
        assert "must score at least three dimensions" in pending.stderr

        for path in review_paths:
            complete(path)
        accepted = run(
            [
                str(Path(sys.executable).resolve()),
                str(REVIEWER),
                "check",
                "--results", str(results),
                "--review-bundle", str(review_bundle),
                "--reviews", str(review_paths[0]),
                "--reviews", str(review_paths[1]),
            ]
        )
        assert accepted.stdout.startswith("ACCEPT")
        assert "human_review_cases=28" in accepted.stdout

        one_reviewer = run(
            [
                str(Path(sys.executable).resolve()),
                str(REVIEWER),
                "check",
                "--results", str(results),
                "--review-bundle", str(review_bundle),
                "--reviews", str(review_paths[0]),
            ],
            expected=1,
        )
        assert "requires 2" in one_reviewer.stderr

        complete(review_paths[1], fail_first=True)
        conflict = run(
            [
                str(Path(sys.executable).resolve()),
                str(REVIEWER),
                "check",
                "--results", str(results),
                "--review-bundle", str(review_bundle),
                "--reviews", str(review_paths[0]),
                "--reviews", str(review_paths[1]),
            ],
            expected=1,
        )
        assert "requires independent adjudication" in conflict.stderr

        first_review = json.loads(review_paths[0].read_text(encoding="utf-8").splitlines()[0])
        adjudication_path = root / "adjudications.jsonl"
        adjudication = {
            "schema_version": "human-adjudication-v1",
            "evaluation_results_sha256": first_review["evaluation_results_sha256"],
            "run_id": first_review["run_id"],
            "case_id": first_review["case_id"],
            "case_result_sha256": first_review["case_result_sha256"],
            "adjudicator_id": "blind-a1",
            "decision": "pass",
            "reason": "Independent source review resolves the reported concern as a false positive.",
        }
        adjudication_path.write_text(json.dumps(adjudication) + "\n", encoding="utf-8")
        adjudicated = run(
            [
                str(Path(sys.executable).resolve()),
                str(REVIEWER),
                "check",
                "--results", str(results),
                "--review-bundle", str(review_bundle),
                "--reviews", str(review_paths[0]),
                "--reviews", str(review_paths[1]),
                "--adjudications", str(adjudication_path),
            ]
        )
        assert "adjudications=1" in adjudicated.stdout

        tampered_values = [
            json.loads(line) for line in review_paths[0].read_text(encoding="utf-8").splitlines()
        ]
        tampered_values[0]["case_result_sha256"] = "0" * 64
        tampered_path = root / "tampered.jsonl"
        tampered_path.write_text(
            "".join(json.dumps(value) + "\n" for value in tampered_values), encoding="utf-8"
        )
        tampered = run(
            [
                str(Path(sys.executable).resolve()),
                str(REVIEWER),
                "check",
                "--results", str(results),
                "--review-bundle", str(review_bundle),
                "--reviews", str(tampered_path),
                "--reviews", str(review_paths[1]),
            ],
            expected=1,
        )
        assert "binding failed" in tampered.stderr

    print(
        "PASS human reviews: result/case binding, two blinded reviewers, rubric scores, "
        "conflict adjudication, deterministic gate, and tamper rejection"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
