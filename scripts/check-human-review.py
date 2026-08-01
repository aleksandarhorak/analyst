#!/usr/bin/env python3
"""Initialize or validate blinded human review records for an evaluation run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


DIMENSIONS = (
    "evidence_and_citations",
    "factual_and_numerical_accuracy",
    "temporal_integrity",
    "uncertainty_and_calibration",
    "risk_cost_and_client_coverage",
    "compliance_and_market_integrity",
    "usefulness_and_reproducibility",
)
REVIEW_FIELDS = {
    "schema_version", "evaluation_results_sha256", "run_id", "case_id",
    "case_result_sha256", "reviewer_id", "blinded", "independent", "scores",
    "critical_failure", "verdict", "reason",
}
ADJUDICATION_FIELDS = {
    "schema_version", "evaluation_results_sha256", "run_id", "case_id",
    "case_result_sha256", "adjudicator_id", "decision", "reason",
}


class ReviewError(RuntimeError):
    """Malformed, incomplete, or unbound human review evidence."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return digest_bytes(canonical(value))


def load_results(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReviewError("evaluation results are not valid UTF-8 JSON") from error
    if not isinstance(value, dict) or value.get("schema_version") != "financial-agent-evaluation-v1":
        raise ReviewError("evaluation results schema mismatch")
    if not isinstance(value.get("run_id"), str) or not value["run_id"]:
        raise ReviewError("evaluation results lack run_id")
    cases = value.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ReviewError("evaluation results contain no cases")
    case_ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(case_ids) != len(cases) or any(not isinstance(case_id, str) for case_id in case_ids):
        raise ReviewError("evaluation results contain malformed cases")
    if len(set(case_ids)) != len(case_ids):
        raise ReviewError("evaluation results contain duplicate case IDs")
    bundle_hash = value.get("review_bundle_sha256")
    if not isinstance(bundle_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", bundle_hash):
        raise ReviewError("evaluation results lack a valid review_bundle_sha256")
    return value, digest_bytes(raw)


def load_jsonl(paths: list[Path], kind: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ReviewError(f"{path}:{line_number}: invalid {kind} JSON") from error
            if not isinstance(record, dict):
                raise ReviewError(f"{path}:{line_number}: {kind} must be an object")
            records.append(record)
    if not records:
        raise ReviewError(f"no {kind} records")
    return records


def identifier(value: Any, field: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{2,80}", value):
        raise ReviewError(f"{field} must be a pseudonymous identifier")
    return value


def case_index(results: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {case["id"]: case for case in results["cases"]}


def validate_review_bundle(path: Path, results: dict[str, Any]) -> None:
    raw = path.read_bytes()
    if digest_bytes(raw) != results["review_bundle_sha256"]:
        raise ReviewError("review bundle hash does not match evaluation results")
    try:
        items = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReviewError("review bundle is not valid UTF-8 JSONL") from error
    expected_count = results["case_count"] * results["repeat_count"]
    if len(items) != expected_count:
        raise ReviewError(
            f"review bundle has {len(items)} items; expected {expected_count}"
        )
    cases = case_index(results)
    seen: set[tuple[int, str]] = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {
            "schema_version", "repeat_index", "case", "response"
        }:
            raise ReviewError("review bundle item schema mismatch")
        if item["schema_version"] != "financial-agent-review-item-v1":
            raise ReviewError("review bundle item version mismatch")
        repeat_index = item["repeat_index"]
        case = item["case"]
        response = item["response"]
        if not isinstance(repeat_index, int) or not 1 <= repeat_index <= results["repeat_count"]:
            raise ReviewError("review bundle repeat_index is invalid")
        if not isinstance(case, dict) or "assertions" in case or "expected" in case:
            raise ReviewError("review bundle exposes a scoring key")
        case_id = case.get("id")
        if case_id not in cases or not isinstance(response, dict) or response.get("id") != case_id:
            raise ReviewError("review bundle case/response identity mismatch")
        key = (repeat_index, case_id)
        if key in seen:
            raise ReviewError(f"duplicate review bundle item: {key}")
        seen.add(key)
        result_case = cases[case_id]
        if digest(case) != result_case["candidate_input_sha256"]:
            raise ReviewError(f"review bundle candidate input hash mismatch: {case_id}")
        if digest(response) != result_case["response_sha256s"][repeat_index - 1]:
            raise ReviewError(f"review bundle response hash mismatch: {case_id}")


def binding_errors(
    record: dict[str, Any], results: dict[str, Any], results_hash: str, case: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if record.get("evaluation_results_sha256") != results_hash:
        errors.append("evaluation_results_sha256 mismatch")
    if record.get("run_id") != results["run_id"]:
        errors.append("run_id mismatch")
    if record.get("case_result_sha256") != digest(case):
        errors.append("case_result_sha256 mismatch")
    return errors


def initialize(args: argparse.Namespace) -> int:
    results, results_hash = load_results(args.results)
    validate_review_bundle(args.review_bundle, results)
    reviewer_id = identifier(args.reviewer_id, "reviewer_id")
    if args.output.exists():
        raise ReviewError(f"output already exists: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for case in results["cases"]:
        record = {
            "schema_version": "human-review-v1",
            "evaluation_results_sha256": results_hash,
            "run_id": results["run_id"],
            "case_id": case["id"],
            "case_result_sha256": digest(case),
            "reviewer_id": reviewer_id,
            "blinded": True,
            "independent": True,
            "scores": {dimension: None for dimension in DIMENSIONS},
            "critical_failure": False,
            "verdict": "pending",
            "reason": "",
        }
        lines.append(json.dumps(record, sort_keys=True))
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"PASS initialized {len(lines)} blinded review records for {reviewer_id}")
    return 0


def validate_review(
    record: dict[str, Any], results: dict[str, Any], results_hash: str, cases: dict[str, dict]
) -> tuple[str, str, bool]:
    if set(record) != REVIEW_FIELDS:
        raise ReviewError(f"review has incorrect fields: {sorted(set(record) ^ REVIEW_FIELDS)}")
    if record["schema_version"] != "human-review-v1":
        raise ReviewError("review schema mismatch")
    case_id = record.get("case_id")
    if case_id not in cases:
        raise ReviewError(f"review references unknown case: {case_id}")
    errors = binding_errors(record, results, results_hash, cases[case_id])
    if errors:
        raise ReviewError(f"review {case_id} binding failed: {', '.join(errors)}")
    reviewer_id = identifier(record.get("reviewer_id"), "reviewer_id")
    if record.get("blinded") is not True or record.get("independent") is not True:
        raise ReviewError(f"review {case_id}/{reviewer_id} is not blinded and independent")
    scores = record.get("scores")
    if not isinstance(scores, dict) or set(scores) != set(DIMENSIONS):
        raise ReviewError(f"review {case_id}/{reviewer_id} has incorrect score dimensions")
    scored = 0
    for dimension, score in scores.items():
        if score is None:
            continue
        if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
            raise ReviewError(f"review {case_id}/{reviewer_id} has invalid {dimension} score")
        scored += 1
    if scored < 3:
        raise ReviewError(f"review {case_id}/{reviewer_id} must score at least three dimensions")
    critical = record.get("critical_failure")
    verdict = record.get("verdict")
    if not isinstance(critical, bool) or verdict not in {"pass", "fail"}:
        raise ReviewError(f"review {case_id}/{reviewer_id} lacks a final verdict")
    if critical and verdict != "fail":
        raise ReviewError(f"review {case_id}/{reviewer_id} critical failure must fail")
    reason = record.get("reason")
    if not isinstance(reason, str) or len(reason.strip()) < 20:
        raise ReviewError(f"review {case_id}/{reviewer_id} reason is too short")
    return case_id, reviewer_id, critical


def validate_adjudication(
    record: dict[str, Any], results: dict[str, Any], results_hash: str, cases: dict[str, dict]
) -> tuple[str, str]:
    if set(record) != ADJUDICATION_FIELDS:
        raise ReviewError(
            f"adjudication has incorrect fields: {sorted(set(record) ^ ADJUDICATION_FIELDS)}"
        )
    if record["schema_version"] != "human-adjudication-v1":
        raise ReviewError("adjudication schema mismatch")
    case_id = record.get("case_id")
    if case_id not in cases:
        raise ReviewError(f"adjudication references unknown case: {case_id}")
    errors = binding_errors(record, results, results_hash, cases[case_id])
    if errors:
        raise ReviewError(f"adjudication {case_id} binding failed: {', '.join(errors)}")
    adjudicator_id = identifier(record.get("adjudicator_id"), "adjudicator_id")
    if record.get("decision") not in {"pass", "fail"}:
        raise ReviewError(f"adjudication {case_id} lacks a final decision")
    reason = record.get("reason")
    if not isinstance(reason, str) or len(reason.strip()) < 20:
        raise ReviewError(f"adjudication {case_id} reason is too short")
    return case_id, adjudicator_id


def check(args: argparse.Namespace) -> int:
    results, results_hash = load_results(args.results)
    validate_review_bundle(args.review_bundle, results)
    cases = case_index(results)
    records = load_jsonl(args.reviews, "review")
    grouped: dict[str, list[dict[str, Any]]] = {case_id: [] for case_id in cases}
    seen: set[tuple[str, str]] = set()
    for record in records:
        case_id, reviewer_id, _ = validate_review(record, results, results_hash, cases)
        key = (case_id, reviewer_id)
        if key in seen:
            raise ReviewError(f"duplicate review: {case_id}/{reviewer_id}")
        seen.add(key)
        grouped[case_id].append(record)

    adjudications: dict[str, dict[str, Any]] = {}
    if args.adjudications:
        for record in load_jsonl([args.adjudications], "adjudication"):
            case_id, adjudicator_id = validate_adjudication(
                record, results, results_hash, cases
            )
            if case_id in adjudications:
                raise ReviewError(f"duplicate adjudication: {case_id}")
            if adjudicator_id in {item["reviewer_id"] for item in grouped[case_id]}:
                raise ReviewError(f"adjudicator for {case_id} must be independent of reviewers")
            adjudications[case_id] = record

    accepted_cases = 0
    agreements = 0
    required_adjudications: set[str] = set()
    for case_id, case_reviews in grouped.items():
        if len(case_reviews) < args.minimum_reviewers:
            raise ReviewError(
                f"case {case_id} has {len(case_reviews)} reviewers; "
                f"requires {args.minimum_reviewers}"
            )
        verdicts = {record["verdict"] for record in case_reviews}
        critical = any(record["critical_failure"] for record in case_reviews)
        if len(verdicts) == 1 and not critical:
            agreements += 1
            decision = next(iter(verdicts))
        elif len(verdicts) == 1 and verdicts == {"fail"}:
            agreements += 1
            decision = "fail"
        else:
            required_adjudications.add(case_id)
            if case_id not in adjudications:
                raise ReviewError(f"case {case_id} requires independent adjudication")
            decision = adjudications[case_id]["decision"]
        if decision == "pass":
            accepted_cases += 1

    extra_adjudications = set(adjudications) - required_adjudications
    if extra_adjudications:
        raise ReviewError(f"adjudications supplied without a conflict: {sorted(extra_adjudications)}")

    deterministic_accept = results.get("decision") == "accept"
    human_accept = accepted_cases == len(cases)
    decision = "accept" if deterministic_accept and human_accept else "reject"
    print(
        f"{decision.upper()} human_review_cases={len(cases)} reviewers={len(records)} "
        f"agreements={agreements} adjudications={len(adjudications)} "
        f"deterministic_decision={results.get('decision')}"
    )
    return 0 if decision == "accept" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize_parser = commands.add_parser("init", help="create a bound reviewer worksheet")
    initialize_parser.add_argument("--results", type=Path, required=True)
    initialize_parser.add_argument("--review-bundle", type=Path, required=True)
    initialize_parser.add_argument("--reviewer-id", required=True)
    initialize_parser.add_argument("--output", type=Path, required=True)
    initialize_parser.set_defaults(handler=initialize)
    check_parser = commands.add_parser("check", help="validate completed reviews")
    check_parser.add_argument("--results", type=Path, required=True)
    check_parser.add_argument("--review-bundle", type=Path, required=True)
    check_parser.add_argument("--reviews", type=Path, action="append", required=True)
    check_parser.add_argument("--adjudications", type=Path)
    check_parser.add_argument("--minimum-reviewers", type=int, default=2)
    check_parser.set_defaults(handler=check)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if getattr(args, "minimum_reviewers", 2) < 2:
            raise ReviewError("minimum_reviewers must be at least 2")
        return args.handler(args)
    except (ReviewError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
