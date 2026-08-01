#!/usr/bin/env python3
"""Execute deterministic assertions against financial-agent candidate outputs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


MAX_CANDIDATE_BYTES = 2 * 1024 * 1024
CANDIDATE_INPUT_FIELDS = ("id", "lane", "prompt", "decision_cutoff", "context")
CASE_FIELDS = set(CANDIDATE_INPUT_FIELDS) | {"assertions"}


class EvaluationError(RuntimeError):
    """A malformed case, response, or candidate execution."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path, kind: str) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise EvaluationError(f"{path}:{line_number}: invalid {kind} JSON") from error
        if not isinstance(value, dict):
            raise EvaluationError(f"{path}:{line_number}: {kind} must be an object")
        values.append(value)
    if not values:
        raise EvaluationError(f"{path}: no {kind} records")
    return values


def validate_cases(cases: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for case in cases:
        required = {"id", "lane", "prompt", "decision_cutoff", "assertions"}
        if missing := required - case.keys():
            raise EvaluationError(f"case missing fields: {sorted(missing)}")
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id:
            raise EvaluationError("case id must be a nonempty string")
        if case_id in seen:
            raise EvaluationError(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if unexpected := case.keys() - CASE_FIELDS:
            raise EvaluationError(f"case {case_id} has unsupported fields: {sorted(unexpected)}")
        for field in ("lane", "prompt", "decision_cutoff"):
            if not isinstance(case[field], str) or not case[field].strip():
                raise EvaluationError(f"case {case_id} {field} must be a nonempty string")
        try:
            cutoff = datetime.fromisoformat(case["decision_cutoff"].replace("Z", "+00:00"))
        except ValueError as error:
            raise EvaluationError(f"case {case_id} decision_cutoff must be ISO 8601") from error
        if cutoff.tzinfo is None:
            raise EvaluationError(f"case {case_id} decision_cutoff must include a timezone")
        if "context" in case and not isinstance(case["context"], dict):
            raise EvaluationError(f"case {case_id} context must be an object")
        assertions = case["assertions"]
        if not isinstance(assertions, list) or not assertions:
            raise EvaluationError(f"case {case_id} has no assertions")
        for assertion in assertions:
            if not isinstance(assertion, dict):
                raise EvaluationError(f"case {case_id} assertion is not an object")
            required_assertion = {"type", "dimension", "critical", "label"}
            if missing := required_assertion - assertion.keys():
                raise EvaluationError(f"case {case_id} assertion missing: {sorted(missing)}")
            if assertion["type"] not in {
                "contains", "not_contains", "regex", "not_regex", "equals", "probability_sum"
            }:
                raise EvaluationError(f"case {case_id} has unsupported assertion type")
            if not isinstance(assertion["dimension"], str) or not assertion["dimension"].strip():
                raise EvaluationError(f"case {case_id} assertion dimension must be nonempty")
            if not isinstance(assertion["label"], str) or not assertion["label"].strip():
                raise EvaluationError(f"case {case_id} assertion label must be nonempty")
            if not isinstance(assertion["critical"], bool):
                raise EvaluationError(f"case {case_id} assertion critical must be boolean")
            weight = assertion.get("weight", 1.0)
            if (
                isinstance(weight, bool)
                or not isinstance(weight, (int, float))
                or not math.isfinite(float(weight))
                or weight <= 0
            ):
                raise EvaluationError(f"case {case_id} assertion weight must be positive")
            assertion_type = assertion["type"]
            if assertion_type in {"contains", "not_contains"}:
                if not isinstance(assertion.get("value"), str) or not assertion["value"]:
                    raise EvaluationError(f"case {case_id} text assertion requires a value")
            elif assertion_type in {"regex", "not_regex"}:
                if not isinstance(assertion.get("pattern"), str) or not assertion["pattern"]:
                    raise EvaluationError(f"case {case_id} regex assertion requires a pattern")
                try:
                    re.compile(assertion["pattern"])
                except re.error as error:
                    raise EvaluationError(f"case {case_id} has invalid regex: {error}") from error
            else:
                if not isinstance(assertion.get("path"), str) or not assertion["path"]:
                    raise EvaluationError(f"case {case_id} structured assertion requires a path")
                tolerance = assertion.get("tolerance", 0.0 if assertion_type == "equals" else 1e-12)
                if (
                    isinstance(tolerance, bool)
                    or not isinstance(tolerance, (int, float))
                    or not math.isfinite(float(tolerance))
                    or tolerance < 0
                ):
                    raise EvaluationError(f"case {case_id} assertion tolerance must be nonnegative")


def candidate_payload(case: dict[str, Any]) -> dict[str, Any]:
    """Return only decision inputs; never expose assertions or expected answers."""
    return {field: case[field] for field in CANDIDATE_INPUT_FIELDS if field in case}


def response_index(responses: list[dict[str, Any]], case_ids: set[str]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for response in responses:
        case_id = response.get("id")
        if not isinstance(case_id, str) or case_id not in case_ids:
            raise EvaluationError(f"unknown or missing response id: {case_id}")
        if case_id in indexed:
            raise EvaluationError(f"duplicate response id: {case_id}")
        if not isinstance(response.get("text"), str):
            raise EvaluationError(f"response {case_id} must contain text")
        if "values" in response and not isinstance(response["values"], dict):
            raise EvaluationError(f"response {case_id} values must be an object")
        indexed[case_id] = response
    missing = case_ids - indexed.keys()
    if missing:
        raise EvaluationError(f"missing responses: {sorted(missing)}")
    return indexed


def run_candidate(command: list[str], case: dict[str, Any], timeout: float) -> dict[str, Any]:
    if not command:
        raise EvaluationError("candidate command is empty")
    try:
        completed = subprocess.run(
            command,
            input=canonical(candidate_payload(case)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise EvaluationError(f"candidate failed for {case['id']}: {error}") from error
    if completed.returncode != 0:
        raise EvaluationError(
            f"candidate exited {completed.returncode} for {case['id']}; "
            f"stderr_sha256={hashlib.sha256(completed.stderr).hexdigest()}"
        )
    if len(completed.stdout) > MAX_CANDIDATE_BYTES:
        raise EvaluationError(f"candidate output too large for {case['id']}")
    try:
        response = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvaluationError(f"candidate returned invalid JSON for {case['id']}") from error
    if not isinstance(response, dict) or response.get("id") != case["id"]:
        raise EvaluationError(f"candidate response id mismatch for {case['id']}")
    if not isinstance(response.get("text"), str):
        raise EvaluationError(f"candidate response lacks text for {case['id']}")
    return response


def resolve_path(value: Any, path: str) -> Any:
    current = value
    for component in path.split("."):
        if not isinstance(current, dict) or component not in current:
            raise KeyError(path)
        current = current[component]
    return current


def equal(actual: Any, expected: Any, tolerance: float) -> bool:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual is expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return math.isfinite(float(actual)) and abs(float(actual) - float(expected)) <= tolerance
    return actual == expected


def evaluate_assertion(assertion: dict[str, Any], response: dict[str, Any]) -> tuple[bool, str]:
    assertion_type = assertion["type"]
    text = response["text"]
    try:
        if assertion_type == "contains":
            expected = str(assertion["value"])
            passed = expected.casefold() in text.casefold()
            return passed, f"expected text to contain {expected!r}"
        if assertion_type == "not_contains":
            expected = str(assertion["value"])
            passed = expected.casefold() not in text.casefold()
            return passed, f"expected text not to contain {expected!r}"
        if assertion_type == "regex":
            pattern = str(assertion["pattern"])
            passed = re.search(pattern, text, flags=re.IGNORECASE) is not None
            return passed, f"expected text to match /{pattern}/"
        if assertion_type == "not_regex":
            pattern = str(assertion["pattern"])
            passed = re.search(pattern, text, flags=re.IGNORECASE) is None
            return passed, f"expected text not to match /{pattern}/"
        if assertion_type == "equals":
            actual = resolve_path(response, str(assertion["path"]))
            expected = assertion["expected"]
            tolerance = float(assertion.get("tolerance", 0.0))
            return equal(actual, expected, tolerance), f"expected {assertion['path']}={expected!r}, got {actual!r}"
        if assertion_type == "probability_sum":
            actual = resolve_path(response, str(assertion["path"]))
            values = list(actual.values()) if isinstance(actual, dict) else actual
            if not isinstance(values, list) or not values:
                return False, f"expected {assertion['path']} to be a nonempty list or object"
            if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in values):
                return False, f"expected numeric probabilities at {assertion['path']}"
            expected = float(assertion.get("expected", 1.0))
            tolerance = float(assertion.get("tolerance", 1e-12))
            actual_sum = sum(float(item) for item in values)
            return abs(actual_sum - expected) <= tolerance, f"expected probability sum {expected}, got {actual_sum}"
    except (KeyError, TypeError, ValueError) as error:
        return False, f"assertion could not read response: {error}"
    raise EvaluationError(f"unsupported assertion type: {assertion_type}")


def score_responses(
    cases: list[dict[str, Any]], responses: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    case_results: list[dict[str, Any]] = []
    total_weight = 0.0
    passed_weight = 0.0
    critical_failures = 0
    dimensions: dict[str, dict[str, float]] = {}
    for case in cases:
        response = responses[case["id"]]
        assertions: list[dict[str, Any]] = []
        case_weight = 0.0
        case_passed = 0.0
        case_critical = False
        for assertion in case["assertions"]:
            passed, detail = evaluate_assertion(assertion, response)
            weight = float(assertion.get("weight", 1.0))
            case_weight += weight
            total_weight += weight
            dimension = assertion["dimension"]
            dimension_result = dimensions.setdefault(
                dimension, {"passed_weight": 0.0, "total_weight": 0.0}
            )
            dimension_result["total_weight"] += weight
            if passed:
                case_passed += weight
                passed_weight += weight
                dimension_result["passed_weight"] += weight
            if not passed and assertion["critical"]:
                case_critical = True
                critical_failures += 1
            assertions.append(
                {
                    "label": assertion["label"],
                    "dimension": dimension,
                    "critical": assertion["critical"],
                    "passed": passed,
                    "detail": detail,
                }
            )
        case_results.append(
            {
                "id": case["id"],
                "lane": case["lane"],
                "case_sha256": digest(case),
                "candidate_input_sha256": digest(candidate_payload(case)),
                "response_sha256": digest(response),
                "score": case_passed / case_weight,
                "critical_failure": case_critical,
                "assertions": assertions,
            }
        )
    return {
        "score": passed_weight / total_weight,
        "critical_failure_count": critical_failures,
        "dimensions": {
            name: values | {"score": values["passed_weight"] / values["total_weight"]}
            for name, values in sorted(dimensions.items())
        },
        "cases": case_results,
    }


def aggregate_dimensions(run_results: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    aggregated: dict[str, dict[str, float]] = {}
    for run in run_results:
        for name, values in run["dimensions"].items():
            result = aggregated.setdefault(name, {"passed_weight": 0.0, "total_weight": 0.0})
            result["passed_weight"] += values["passed_weight"]
            result["total_weight"] += values["total_weight"]
    return {
        name: values | {"score": values["passed_weight"] / values["total_weight"]}
        for name, values in sorted(aggregated.items())
    }


def aggregate_cases(run_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregated: list[dict[str, Any]] = []
    for index, first in enumerate(run_results[0]["cases"]):
        cases = [run["cases"][index] for run in run_results]
        scores = [case["score"] for case in cases]
        aggregated.append(
            first
            | {
                "score": sum(scores) / len(scores),
                "score_min": min(scores),
                "score_max": max(scores),
                "critical_failure": any(case["critical_failure"] for case in cases),
                "response_sha256s": [case["response_sha256"] for case in cases],
            }
        )
    return aggregated


def render_summary(result: dict[str, Any]) -> str:
    lines = [
        f"# Financial Agent Evaluation: {result['run_id']}",
        "",
        f"- Decision: **{result['decision'].upper()}**",
        f"- Score: {result['score']:.3f}",
        f"- Critical failures: {result['critical_failure_count']}",
        f"- Cases: {result['case_count']}",
        f"- Repeat count: {result['repeat_count']}",
        f"- Score range: {result['score_min']:.3f} to {result['score_max']:.3f}",
        f"- Score variance: {result['score_variance']:.6f}",
        f"- Model version: `{result['model_version']}`",
        f"- Tool version: `{result['tool_version']}`",
    ]
    baseline = result.get("baseline")
    if baseline:
        lines.extend(
            [
                f"- Baseline score: {baseline['score']:.3f}",
                f"- Delta versus baseline: {result['delta_vs_baseline']:+.3f}",
            ]
        )
    lines.extend(["", "| Case | Lane | Score | Critical failure |", "|---|---|---:|---|"])
    for case in result["cases"]:
        lines.append(
            f"| `{case['id']}` | {case['lane']} | {case['score']:.3f} | "
            f"{'yes' if case['critical_failure'] else 'no'} |"
        )
    lines.extend(["", "Any critical assertion failure rejects the candidate regardless of average score."])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--holdout-cases", type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--responses", type=Path)
    source.add_argument("--candidate-command", nargs=argparse.REMAINDER)
    parser.add_argument("--baseline-responses", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model-version", required=True)
    parser.add_argument("--tool-version", required=True)
    parser.add_argument("--minimum-score", type=float, default=0.9)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--repeat-count", type=int, default=1)
    args = parser.parse_args()

    try:
        if not 0 <= args.minimum_score <= 1 or args.timeout <= 0 or args.repeat_count <= 0:
            raise EvaluationError(
                "minimum-score must be in [0,1], timeout positive, and repeat-count positive"
            )
        if args.responses and args.repeat_count != 1:
            raise EvaluationError("frozen responses support repeat-count 1 only")
        if args.output_dir.exists():
            raise EvaluationError(f"output directory already exists: {args.output_dir}")
        args.output_dir.parent.mkdir(parents=True, exist_ok=True)
        args.output_dir.mkdir()
        public_cases = load_jsonl(args.cases, "case")
        holdout_cases = load_jsonl(args.holdout_cases, "holdout case") if args.holdout_cases else []
        cases = [*public_cases, *holdout_cases]
        validate_cases(cases)
        case_ids = {case["id"] for case in cases}
        response_runs: list[dict[str, dict[str, Any]]]
        if args.responses:
            response_runs = [response_index(load_jsonl(args.responses, "response"), case_ids)]
        else:
            response_runs = [
                {
                    case["id"]: run_candidate(args.candidate_command or [], case, args.timeout)
                    for case in cases
                }
                for _ in range(args.repeat_count)
            ]
        run_results = [score_responses(cases, responses) for responses in response_runs]
        scores = [run["score"] for run in run_results]
        score = sum(scores) / len(scores)
        score_variance = sum((value - score) ** 2 for value in scores) / len(scores)
        critical_failures = sum(run["critical_failure_count"] for run in run_results)
        decision = "reject" if critical_failures or score < args.minimum_score else "accept"
        baseline = None
        if args.baseline_responses:
            baseline_responses = response_index(
                load_jsonl(args.baseline_responses, "baseline response"), case_ids
            )
            baseline = score_responses(cases, baseline_responses)
            baseline["decision"] = (
                "reject"
                if baseline["critical_failure_count"] or baseline["score"] < args.minimum_score
                else "accept"
            )
        result = {
            "schema_version": "financial-agent-evaluation-v1",
            "run_id": args.run_id,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "model_version": args.model_version,
            "tool_version": args.tool_version,
            "public_cases_sha256": digest(public_cases),
            "holdout_cases_sha256": digest(holdout_cases) if holdout_cases else None,
            "holdout_used": bool(holdout_cases),
            "rubric_sha256": digest(
                [{"id": case["id"], "assertions": case["assertions"]} for case in cases]
            ),
            "scorer_sha256": file_digest(Path(__file__)),
            "candidate_command_sha256": (
                digest(args.candidate_command) if args.candidate_command else None
            ),
            "frozen_responses_sha256": file_digest(args.responses) if args.responses else None,
            "baseline_responses_sha256": (
                file_digest(args.baseline_responses) if args.baseline_responses else None
            ),
            "candidate_input_fields": list(CANDIDATE_INPUT_FIELDS),
            "case_count": len(cases),
            "repeat_count": len(run_results),
            "minimum_score": args.minimum_score,
            "score": score,
            "score_min": min(scores),
            "score_max": max(scores),
            "score_variance": score_variance,
            "critical_failure_count": critical_failures,
            "decision": decision,
            "dimensions": aggregate_dimensions(run_results),
            "cases": aggregate_cases(run_results),
            "runs": run_results,
            "baseline": baseline,
            "delta_vs_baseline": score - baseline["score"] if baseline else None,
        }
        (args.output_dir / "results.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (args.output_dir / "summary.md").write_text(render_summary(result), encoding="utf-8")
        print(f"{decision.upper()} score={score:.3f} critical_failures={critical_failures}")
        return 0 if decision == "accept" else 2
    except (EvaluationError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
