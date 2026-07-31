#!/usr/bin/env python3
"""Append, verify, and score immutable directional forecast ledgers."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Callable


FORECAST_SCHEMA = "forecast-record-v1"
OUTCOME_SCHEMA = "forecast-outcome-v1"
CLASSES = ("up", "flat", "down")
HASH_PREFIX = "sha256:"


class LedgerError(RuntimeError):
    """A malformed or unsafe ledger operation."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def record_hash(record: dict[str, Any]) -> str:
    body = {key: value for key, value in record.items() if key != "record_sha256"}
    return hashlib.sha256(canonical(body)).hexdigest()


def parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise LedgerError(f"{field} must be a timezone-aware ISO 8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise LedgerError(f"{field} must be a timezone-aware ISO 8601 string") from error
    if parsed.tzinfo is None:
        raise LedgerError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LedgerError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise LedgerError(f"{field} must be finite")
    return result


def validate_packet_id(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.startswith(HASH_PREFIX) or len(value) != 71:
        raise LedgerError(f"{field} must be sha256:<64 lowercase hex>")
    try:
        int(value[len(HASH_PREFIX) :], 16)
    except ValueError as error:
        raise LedgerError(f"{field} must be sha256:<64 lowercase hex>") from error
    if value != value.lower():
        raise LedgerError(f"{field} must use lowercase hex")


def validate_forecast(record: dict[str, Any], require_hash: bool = True) -> None:
    required = {
        "schema_version", "forecast_id", "created_at", "decision_cutoff", "target_at",
        "instrument_id", "symbol", "asset_class", "horizon", "regime", "start_value",
        "unit", "currency", "flat_band", "probabilities", "method_version",
        "evidence_packet_ids",
    }
    if missing := required - record.keys():
        raise LedgerError(f"forecast missing fields: {sorted(missing)}")
    if record["schema_version"] != FORECAST_SCHEMA:
        raise LedgerError("invalid forecast schema_version")
    for field in ("forecast_id", "instrument_id", "symbol", "asset_class", "horizon", "regime", "unit", "currency", "method_version"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise LedgerError(f"{field} must be a nonempty string")
    cutoff = parse_time(record["decision_cutoff"], "decision_cutoff")
    created = parse_time(record["created_at"], "created_at")
    target = parse_time(record["target_at"], "target_at")
    if created < cutoff:
        raise LedgerError("created_at cannot precede decision_cutoff")
    if target <= cutoff or created > target:
        raise LedgerError("target_at must follow cutoff and creation")
    finite_number(record["start_value"], "start_value")
    band = record["flat_band"]
    if not isinstance(band, dict) or set(band) != {"lower_return", "upper_return"}:
        raise LedgerError("flat_band must contain only lower_return and upper_return")
    lower = finite_number(band["lower_return"], "flat_band.lower_return")
    upper = finite_number(band["upper_return"], "flat_band.upper_return")
    if not lower <= 0 <= upper or lower >= upper:
        raise LedgerError("flat band must be ordered and contain zero")
    probabilities = record["probabilities"]
    if not isinstance(probabilities, dict) or set(probabilities) != set(CLASSES):
        raise LedgerError("probabilities must contain exactly up, flat, and down")
    values = [finite_number(probabilities[label], f"probabilities.{label}") for label in CLASSES]
    if any(value < 0 or value > 1 for value in values) or abs(sum(values) - 1.0) > 1e-12:
        raise LedgerError("probabilities must be in [0,1] and total 1.0")
    packet_ids = record["evidence_packet_ids"]
    if not isinstance(packet_ids, list) or not packet_ids:
        raise LedgerError("evidence_packet_ids must be a nonempty array")
    for index, value in enumerate(packet_ids):
        validate_packet_id(value, f"evidence_packet_ids[{index}]")
    if require_hash and record.get("record_sha256") != record_hash(record):
        raise LedgerError(f"forecast hash mismatch: {record['forecast_id']}")


def classify(realized_return: float, forecast: dict[str, Any]) -> str:
    band = forecast["flat_band"]
    if realized_return < float(band["lower_return"]):
        return "down"
    if realized_return > float(band["upper_return"]):
        return "up"
    return "flat"


def validate_outcome(
    record: dict[str, Any], forecasts: dict[str, dict[str, Any]], require_hash: bool = True
) -> None:
    required = {
        "schema_version", "forecast_id", "resolved_at", "outcome_as_of",
        "realized_return", "outcome_category", "outcome_packet_id",
        "corporate_action_treatment", "fx_treatment",
    }
    if missing := required - record.keys():
        raise LedgerError(f"outcome missing fields: {sorted(missing)}")
    if record["schema_version"] != OUTCOME_SCHEMA:
        raise LedgerError("invalid outcome schema_version")
    forecast_id = record["forecast_id"]
    if forecast_id not in forecasts:
        raise LedgerError(f"orphan outcome: {forecast_id}")
    forecast = forecasts[forecast_id]
    outcome_as_of = parse_time(record["outcome_as_of"], "outcome_as_of")
    resolved_at = parse_time(record["resolved_at"], "resolved_at")
    target = parse_time(forecast["target_at"], "target_at")
    if outcome_as_of < target:
        raise LedgerError("outcome_as_of cannot precede target_at")
    if resolved_at < outcome_as_of:
        raise LedgerError("resolved_at cannot precede outcome_as_of")
    realized = finite_number(record["realized_return"], "realized_return")
    if record["outcome_category"] != classify(realized, forecast):
        raise LedgerError(f"outcome category mismatch: {forecast_id}")
    validate_packet_id(record["outcome_packet_id"], "outcome_packet_id")
    for field in ("corporate_action_treatment", "fx_treatment"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise LedgerError(f"{field} must be a nonempty string")
    if require_hash and record.get("record_sha256") != record_hash(record):
        raise LedgerError(f"outcome hash mismatch: {forecast_id}")


def load_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise LedgerError(f"{path}:{line_number}: invalid JSON") from error
        if not isinstance(value, dict):
            raise LedgerError(f"{path}:{line_number}: record must be an object")
        records.append(value)
    return records


def index_forecasts(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        validate_forecast(record)
        forecast_id = record["forecast_id"]
        if forecast_id in indexed:
            raise LedgerError(f"duplicate forecast_id: {forecast_id}")
        indexed[forecast_id] = record
    return indexed


def index_outcomes(
    records: list[dict[str, Any]], forecasts: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        validate_outcome(record, forecasts)
        forecast_id = record["forecast_id"]
        if forecast_id in indexed:
            raise LedgerError(f"duplicate outcome: {forecast_id}")
        indexed[forecast_id] = record
    return indexed


def append_locked(
    path: Path,
    record: dict[str, Any],
    existing_validator: Callable[[list[dict[str, Any]]], None],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_RDWR | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        with os.fdopen(descriptor, "r+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            handle.seek(0)
            existing: list[dict[str, Any]] = []
            for line_number, line in enumerate(handle.read().splitlines(), start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as error:
                    raise LedgerError(f"{path}:{line_number}: invalid JSON") from error
                if not isinstance(value, dict):
                    raise LedgerError(f"{path}:{line_number}: record must be an object")
                existing.append(value)
            existing_validator(existing)
            handle.seek(0, os.SEEK_END)
            handle.write(canonical(record).decode("utf-8") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        if not getattr(descriptor, "closed", True):
            os.close(descriptor)
        raise


def load_input(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LedgerError("input record must be an object")
    return value


def register(args: argparse.Namespace) -> int:
    record = load_input(args.record)
    record["schema_version"] = FORECAST_SCHEMA
    record.pop("record_sha256", None)
    validate_forecast(record, require_hash=False)
    record["record_sha256"] = record_hash(record)

    def validate_existing(existing: list[dict[str, Any]]) -> None:
        indexed = index_forecasts(existing)
        if record["forecast_id"] in indexed:
            raise LedgerError(f"forecast_id already exists: {record['forecast_id']}")

    append_locked(args.forecasts, record, validate_existing)
    print(f"PASS registered {record['forecast_id']} {record['record_sha256']}")
    return 0


def resolve(args: argparse.Namespace) -> int:
    input_record = load_input(args.record)
    forecasts = index_forecasts(load_records(args.forecasts))
    forecast_id = input_record.get("forecast_id")
    if forecast_id not in forecasts:
        raise LedgerError(f"unknown forecast_id: {forecast_id}")
    record = dict(input_record)
    record["schema_version"] = OUTCOME_SCHEMA
    record["outcome_category"] = classify(
        finite_number(record.get("realized_return"), "realized_return"), forecasts[forecast_id]
    )
    record.pop("record_sha256", None)
    validate_outcome(record, forecasts, require_hash=False)
    record["record_sha256"] = record_hash(record)

    def validate_existing(existing: list[dict[str, Any]]) -> None:
        indexed = index_outcomes(existing, forecasts)
        if forecast_id in indexed:
            raise LedgerError(f"outcome already exists: {forecast_id}")

    append_locked(args.outcomes, record, validate_existing)
    print(f"PASS resolved {forecast_id} as {record['outcome_category']} {record['record_sha256']}")
    return 0


def verify(args: argparse.Namespace) -> int:
    forecasts = index_forecasts(load_records(args.forecasts))
    outcomes = index_outcomes(load_records(args.outcomes), forecasts)
    print(f"PASS verified {len(forecasts)} forecast(s) and {len(outcomes)} outcome(s)")
    return 0


def metric_group(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]], bin_width: float, epsilon: float
) -> dict[str, Any]:
    brier = 0.0
    log_loss = 0.0
    correct = 0
    bins: dict[str, dict[int, list[tuple[float, int]]]] = {
        label: defaultdict(list) for label in CLASSES
    }
    for forecast, outcome in pairs:
        probabilities = {label: float(forecast["probabilities"][label]) for label in CLASSES}
        actual = outcome["outcome_category"]
        brier += sum((probabilities[label] - (1.0 if label == actual else 0.0)) ** 2 for label in CLASSES)
        log_loss += -math.log(max(epsilon, min(1.0, probabilities[actual])))
        prediction = max(CLASSES, key=lambda label: probabilities[label])
        correct += int(prediction == actual)
        for label in CLASSES:
            bucket = min(int(probabilities[label] / bin_width), int(1.0 / bin_width) - 1)
            bins[label][bucket].append((probabilities[label], int(actual == label)))
    count = len(pairs)
    reliability: dict[str, list[dict[str, Any]]] = {}
    for label in CLASSES:
        reliability[label] = []
        for bucket, values in sorted(bins[label].items()):
            reliability[label].append(
                {
                    "lower": round(bucket * bin_width, 12),
                    "upper": round((bucket + 1) * bin_width, 12),
                    "count": len(values),
                    "mean_probability": sum(value[0] for value in values) / len(values),
                    "observed_frequency": sum(value[1] for value in values) / len(values),
                }
            )
    return {
        "resolved_count": count,
        "mean_brier": brier / count,
        "mean_log_loss": log_loss / count,
        "accuracy": correct / count,
        "reliability": reliability,
    }


def score(args: argparse.Namespace) -> int:
    if not 0 < args.bin_width <= 1 or abs(round(1 / args.bin_width) * args.bin_width - 1) > 1e-12:
        raise LedgerError("bin_width must divide 1.0 exactly")
    if not 0 < args.epsilon < 0.5:
        raise LedgerError("epsilon must be between 0 and 0.5")
    forecasts = index_forecasts(load_records(args.forecasts))
    outcomes = index_outcomes(load_records(args.outcomes), forecasts)
    pairs = [(forecast, outcomes[forecast_id]) for forecast_id, forecast in forecasts.items() if forecast_id in outcomes]
    result: dict[str, Any] = {
        "schema_version": "forecast-score-v1",
        "registered_count": len(forecasts),
        "resolved_count": len(pairs),
        "coverage": len(pairs) / len(forecasts) if forecasts else 0.0,
        "unresolved_count": len(forecasts) - len(pairs),
        "bin_width": args.bin_width,
        "log_loss_epsilon": args.epsilon,
        "groups": {},
    }
    if pairs:
        grouped: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {"all": pairs}
        for field in ("horizon", "asset_class", "regime", "method_version"):
            for value in sorted({forecast[field] for forecast, _ in pairs}):
                grouped[f"{field}:{value}"] = [pair for pair in pairs if pair[0][field] == value]
        result["groups"] = {
            name: metric_group(group, args.bin_width, args.epsilon) for name, group in grouped.items()
        }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    for name, handler in (("register", register), ("resolve", resolve)):
        command = commands.add_parser(name)
        command.add_argument("--forecasts", type=Path, required=True)
        command.add_argument("--outcomes", type=Path)
        command.add_argument("--record", type=Path, required=True)
        command.set_defaults(handler=handler)

    verify_command = commands.add_parser("verify")
    verify_command.add_argument("--forecasts", type=Path, required=True)
    verify_command.add_argument("--outcomes", type=Path, required=True)
    verify_command.set_defaults(handler=verify)

    score_command = commands.add_parser("score")
    score_command.add_argument("--forecasts", type=Path, required=True)
    score_command.add_argument("--outcomes", type=Path, required=True)
    score_command.add_argument("--bin-width", type=float, default=0.1)
    score_command.add_argument("--epsilon", type=float, default=1e-15)
    score_command.add_argument("--output", type=Path)
    score_command.set_defaults(handler=score)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "register" and args.outcomes is not None:
        raise SystemExit("register does not accept --outcomes")
    if args.command == "resolve" and args.outcomes is None:
        raise SystemExit("resolve requires --outcomes")
    try:
        return args.handler(args)
    except (LedgerError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
