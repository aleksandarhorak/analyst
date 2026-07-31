#!/usr/bin/env python3
"""Create and verify write-once symbol snapshots with a hash-chained manifest."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


SYMBOL_PATTERN = re.compile(r"^[A-Z0-9._-]+$")
BATCH_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{6}Z$")
LATEST_MARKER = "<!-- analyst-template: latest-v2 -->"
DECISIONS_MARKER = "<!-- analyst-template: decisions-v2 -->"
MANIFEST_SCHEMA = "symbol-history-manifest-v1"
DECISION_FIELDS = ("price_status", "horizon_view", "decision", "confidence", "next_review")


class HistoryError(RuntimeError):
    """An immutable-history validation or write error."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def record_hash(record: dict[str, Any]) -> str:
    return sha256_bytes(canonical({key: value for key, value in record.items() if key != "record_sha256"}))


def parse_time(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise HistoryError(f"{field} must be an ISO 8601 date-time") from error
    if parsed.tzinfo is None:
        raise HistoryError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate_symbol(symbol: str) -> None:
    if not SYMBOL_PATTERN.fullmatch(symbol):
        raise HistoryError(f"invalid symbol: {symbol}")


def load_manifest_lines(lines: list[str], context: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    previous: str | None = None
    batches: set[str] = set()
    paths: set[str] = set()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise HistoryError(f"{context}:{line_number}: invalid JSON") from error
        if not isinstance(record, dict) or record.get("schema_version") != MANIFEST_SCHEMA:
            raise HistoryError(f"{context}:{line_number}: invalid schema")
        if record.get("record_sha256") != record_hash(record):
            raise HistoryError(f"{context}:{line_number}: record hash mismatch")
        if record.get("previous_record_sha256") != previous:
            raise HistoryError(f"{context}:{line_number}: broken manifest hash chain")
        batch_id = record.get("batch_id")
        path = record.get("snapshot_path")
        if batch_id in batches or path in paths:
            raise HistoryError(f"{context}:{line_number}: duplicate batch or path")
        batches.add(batch_id)
        paths.add(path)
        previous = record["record_sha256"]
        records.append(record)
    return records


def load_manifest(path: Path) -> list[dict[str, Any]]:
    return load_manifest_lines(path.read_text(encoding="utf-8").splitlines(), str(path)) if path.exists() else []


def render_decision_row(record: dict[str, Any], cutoff: str, batch_id: str, snapshot_name: str) -> str:
    for field in DECISION_FIELDS:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            raise HistoryError(f"decision record field must be nonempty: {field}")
        if "|" in value or "\n" in value or "\r" in value:
            raise HistoryError(f"decision record field contains table control characters: {field}")
    return (
        f"| {cutoff} | {batch_id} | {record['price_status']} | {record['horizon_view']} | "
        f"{record['decision']} | {record['confidence']} | "
        f"[Snapshot](history/{snapshot_name}) | {record['next_review']} |"
    )


def write_exclusive(path: Path, content: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def atomic_replace(path: Path, content: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def snapshot(args: argparse.Namespace) -> int:
    validate_symbol(args.symbol)
    if not BATCH_PATTERN.fullmatch(args.batch_id):
        raise HistoryError("batch_id must use YYYY-MM-DDTHHMMSSZ")
    parse_time(datetime.strptime(args.batch_id, "%Y-%m-%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat(), "batch_id")
    cutoff_time = parse_time(args.decision_cutoff, "decision_cutoff")
    recorded_time = parse_time(args.recorded_at, "recorded_at")
    if recorded_time < cutoff_time:
        raise HistoryError("recorded_at cannot precede decision_cutoff")
    draft = args.draft.read_text(encoding="utf-8")
    if LATEST_MARKER not in draft or not draft.startswith(f"# {args.symbol} — Latest Research\n"):
        raise HistoryError("draft must be the matching latest-v2 symbol document")
    placeholder = "- Immutable snapshot: —"
    if placeholder not in draft:
        raise HistoryError("draft must contain the immutable snapshot placeholder")
    decision = json.loads(args.decision_record.read_text(encoding="utf-8"))
    if not isinstance(decision, dict):
        raise HistoryError("decision record must be a JSON object")

    symbol_root = args.repo_root.resolve() / "research" / "symbols" / args.symbol
    history_root = symbol_root / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    decisions_path = symbol_root / "DECISIONS.md"
    latest_path = symbol_root / "LATEST.md"
    manifest_path = history_root / "MANIFEST.jsonl"
    if not decisions_path.is_file() or DECISIONS_MARKER not in decisions_path.read_text(encoding="utf-8"):
        raise HistoryError("DECISIONS.md must be migrated to decisions-v2")

    snapshot_name = f"{args.batch_id}.md"
    snapshot_path = history_root / snapshot_name
    relative_snapshot = f"research/symbols/{args.symbol}/history/{snapshot_name}"
    snapshot_content = draft.replace(
        placeholder, f"- Immutable snapshot: Self (`{args.batch_id}`)", 1
    ).encode("utf-8")
    latest_content = draft.replace(
        placeholder, f"- Immutable snapshot: [Snapshot](history/{snapshot_name})", 1
    ).encode("utf-8")
    decision_row = render_decision_row(decision, args.decision_cutoff, args.batch_id, snapshot_name)

    manifest_path.touch(mode=0o644, exist_ok=True)
    with manifest_path.open("r+", encoding="utf-8") as manifest:
        fcntl.flock(manifest.fileno(), fcntl.LOCK_EX)
        manifest.seek(0)
        existing = load_manifest_lines(manifest.read().splitlines(), str(manifest_path))
        if any(record["batch_id"] == args.batch_id for record in existing):
            raise HistoryError(f"batch already exists: {args.batch_id}")
        if snapshot_path.exists():
            raise HistoryError(f"snapshot already exists: {snapshot_path}")
        decisions_text = decisions_path.read_text(encoding="utf-8")
        if decision_row in decisions_text:
            raise HistoryError("decision row already exists")

        write_exclusive(snapshot_path, snapshot_content)
        atomic_replace(latest_path, latest_content)
        with decisions_path.open("a", encoding="utf-8") as decisions_file:
            if decisions_text and not decisions_text.endswith("\n"):
                decisions_file.write("\n")
            decisions_file.write(decision_row + "\n")
            decisions_file.flush()
            os.fsync(decisions_file.fileno())

        record: dict[str, Any] = {
            "schema_version": MANIFEST_SCHEMA,
            "symbol": args.symbol,
            "batch_id": args.batch_id,
            "decision_cutoff": args.decision_cutoff,
            "recorded_at": args.recorded_at,
            "snapshot_path": relative_snapshot,
            "snapshot_sha256": sha256_bytes(snapshot_content),
            "latest_sha256": sha256_bytes(latest_content),
            "decision_row": decision_row,
            "decision_row_sha256": sha256_bytes(decision_row.encode("utf-8")),
            "previous_record_sha256": existing[-1]["record_sha256"] if existing else None,
        }
        record["record_sha256"] = record_hash(record)
        manifest.seek(0, os.SEEK_END)
        manifest.write(canonical(record).decode("utf-8") + "\n")
        manifest.flush()
        os.fsync(manifest.fileno())

    print(f"PASS snapshot {args.symbol} {args.batch_id} {record['snapshot_sha256']}")
    return 0


def verify_symbol(repo_root: Path, symbol: str) -> list[str]:
    failures: list[str] = []
    symbol_root = repo_root / "research" / "symbols" / symbol
    history_root = symbol_root / "history"
    manifest_path = history_root / "MANIFEST.jsonl"
    try:
        records = load_manifest(manifest_path)
    except (OSError, HistoryError) as error:
        return [str(error)]
    expected_paths: set[Path] = set()
    decisions_text = (
        (symbol_root / "DECISIONS.md").read_text(encoding="utf-8")
        if (symbol_root / "DECISIONS.md").is_file()
        else ""
    )
    for record in records:
        if record.get("symbol") != symbol:
            failures.append(f"{symbol}: manifest symbol mismatch")
        snapshot_path = repo_root / str(record.get("snapshot_path", ""))
        expected_paths.add(snapshot_path.resolve())
        if not snapshot_path.is_file():
            failures.append(f"{symbol}: missing snapshot {snapshot_path.name}")
        elif sha256_bytes(snapshot_path.read_bytes()) != record.get("snapshot_sha256"):
            failures.append(f"{symbol}: snapshot hash mismatch {snapshot_path.name}")
        decision_row = record.get("decision_row")
        if not isinstance(decision_row, str) or sha256_bytes(decision_row.encode("utf-8")) != record.get("decision_row_sha256"):
            failures.append(f"{symbol}: decision row hash mismatch")
        elif decisions_text.count(decision_row) != 1:
            failures.append(f"{symbol}: decision row missing or duplicated")
    actual_paths = {
        path.resolve() for path in history_root.glob("*.md") if path.is_file()
    } if history_root.is_dir() else set()
    for path in sorted(actual_paths - expected_paths):
        failures.append(f"{symbol}: unmanifested snapshot {path.name}")
    if records:
        latest_path = symbol_root / "LATEST.md"
        if not latest_path.is_file() or sha256_bytes(latest_path.read_bytes()) != records[-1].get("latest_sha256"):
            failures.append(f"{symbol}: LATEST.md does not match last manifested write")
    return failures


def verify(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    symbols = [args.symbol] if args.symbol else sorted(
        path.name for path in (repo_root / "research" / "symbols").iterdir() if path.is_dir()
    )
    failures: list[str] = []
    for symbol in symbols:
        validate_symbol(symbol)
        failures.extend(verify_symbol(repo_root, symbol))
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print(f"PASS verified immutable history for {len(symbols)} symbol(s)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    snapshot_parser = commands.add_parser("snapshot")
    snapshot_parser.add_argument("--repo-root", type=Path, required=True)
    snapshot_parser.add_argument("--symbol", required=True)
    snapshot_parser.add_argument("--batch-id", required=True)
    snapshot_parser.add_argument("--decision-cutoff", required=True)
    snapshot_parser.add_argument("--recorded-at", required=True)
    snapshot_parser.add_argument("--draft", type=Path, required=True)
    snapshot_parser.add_argument("--decision-record", type=Path, required=True)
    snapshot_parser.set_defaults(handler=snapshot)

    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--repo-root", type=Path, required=True)
    verify_parser.add_argument("--symbol")
    verify_parser.set_defaults(handler=verify)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.handler(args)
    except (HistoryError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
