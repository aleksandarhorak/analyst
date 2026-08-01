#!/usr/bin/env python3
"""Initialize, checkpoint, finalize, and verify a resumable symbol batch."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

from symbol_research_contract import REQUIRED_LANES, parse_time
from sync_symbol_research import parse_active_universe, render


SCHEMA = "symbol-research-run-v1"
CORRECTION_SCHEMA = "symbol-research-correction-v1"
BATCH_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{6}Z$")
SHARED_STAGES = (
    "identity_registry",
    "provider_preflight",
    "macro_regime",
    "central_reconciliation",
    "publication",
)
WORK_STATUSES = {"not_started", "in_progress", "complete", "blocked", "abstained", "not_applicable"}
TERMINAL_STATUSES = {"complete", "blocked", "abstained", "not_applicable"}
SHARED_WORK_STATUSES = {"not_started", "in_progress", "complete", "blocked"}
SHARED_TERMINAL_STATUSES = {"complete", "blocked"}
MACRO_MARKER = "<!-- analyst-template: symbol-batch-macro-v1 -->"


class BatchError(RuntimeError):
    """The batch checkpoint is invalid or unsafe to update."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def content_hash(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical({key: item for key, item in value.items() if key != "record_sha256"})).hexdigest()


def load_corrections(path: Path, batch_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    previous: str | None = None
    if not path.is_file():
        raise BatchError(f"missing correction ledger: {path}")
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise BatchError(f"correction ledger line {number} is invalid JSON") from error
        if not isinstance(record, dict) or record.get("schema_version") != CORRECTION_SCHEMA:
            raise BatchError(f"correction ledger line {number} has invalid schema")
        if record.get("batch_id") != batch_id or record.get("previous_record_sha256") != previous:
            raise BatchError(f"correction ledger line {number} has a broken batch/hash chain")
        if record.get("record_sha256") != content_hash(record):
            raise BatchError(f"correction ledger line {number} has a record hash mismatch")
        previous = record["record_sha256"]
        records.append(record)
    return records


def universe_state(repo_root: Path) -> tuple[list[str], str]:
    records = parse_active_universe(repo_root / "SYMBOLS.md")
    payload = [
        {
            "symbol": record.symbol,
            "instrument": record.instrument,
            "asset_class": record.asset_class,
            "description": record.description,
        }
        for record in records
    ]
    return [record.symbol for record in records], hashlib.sha256(canonical(payload)).hexdigest()


def expected_symbol_workspaces(batch_id: str, symbols: list[str]) -> dict[str, dict[str, str]]:
    return {
        symbol: {
            "latest_draft": f"research/batches/{batch_id}/symbols/{symbol}/LATEST.draft.md",
            "decision_draft": f"research/batches/{batch_id}/symbols/{symbol}/decision.draft.json",
            "calculations": f"research/batches/{batch_id}/symbols/{symbol}/CALCULATIONS.md",
            "evidence": f"research/batches/{batch_id}/symbols/{symbol}/EVIDENCE.md",
        }
        for symbol in symbols
    }


def expected_shared_workspaces(batch_id: str) -> dict[str, str]:
    base = f"research/batches/{batch_id}"
    return {
        "identity_registry": f"{base}/IDENTITY.md",
        "provider_preflight": f"{base}/PREFLIGHT.md",
        "macro_regime": f"{base}/MACRO.md",
        "central_reconciliation": f"{base}/RECONCILIATION.md",
        "publication": f"{base}/PUBLICATION.md",
    }


def validate_artifact(repo_root: Path, batch_id: str, value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise BatchError(f"{field} must be a repository-relative batch artifact")
    prefix = f"research/batches/{batch_id}/"
    if not value.startswith(prefix) or ".." in Path(value).parts or Path(value).is_absolute():
        raise BatchError(f"{field} must remain inside {prefix}")
    path = (repo_root / value).resolve()
    batch_root = (repo_root / "research" / "batches" / batch_id).resolve()
    if batch_root not in path.parents or not path.is_file():
        raise BatchError(f"{field} is missing or outside the batch: {value}")
    return value


def run_path(repo_root: Path, batch_id: str) -> Path:
    if not BATCH_PATTERN.fullmatch(batch_id):
        raise BatchError("batch_id must use YYYY-MM-DDTHHMMSSZ")
    return repo_root / "research" / "batches" / batch_id / "RUN.json"


def atomic_replace(path: Path, data: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8") + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def write_exclusive_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def load_run(repo_root: Path, batch_id: str) -> tuple[Path, dict[str, Any]]:
    path = run_path(repo_root, batch_id)
    if not path.is_file():
        raise BatchError(f"missing checkpoint: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise BatchError(f"invalid checkpoint JSON: {error}") from error
    if not isinstance(value, dict):
        raise BatchError("checkpoint must be a JSON object")
    return path, value


def validate_run(repo_root: Path, data: dict[str, Any], *, final: bool) -> list[str]:
    failures: list[str] = []
    symbols, universe_hash = universe_state(repo_root)
    if data.get("schema_version") != SCHEMA:
        failures.append("invalid run schema")
    batch_id = data.get("batch_id")
    if not isinstance(batch_id, str) or not BATCH_PATTERN.fullmatch(batch_id):
        failures.append("invalid batch_id")
    try:
        cutoff = parse_time(data.get("decision_cutoff"), "decision_cutoff")
        created = parse_time(data.get("created_at"), "created_at")
        updated = parse_time(data.get("updated_at"), "updated_at")
        if created < cutoff or updated < created:
            failures.append("checkpoint times are not ordered cutoff <= created <= updated")
    except RuntimeError as error:
        failures.append(str(error))
    if data.get("reporting_currency") != "USD" or data.get("research_depth_contract") != "full-depth-v1":
        failures.append("run currency or depth contract is invalid")
    if data.get("active_symbols") != symbols or data.get("universe_sha256") != universe_hash:
        failures.append("active universe or universe hash has changed")
    expected_symbol_paths = expected_symbol_workspaces(str(batch_id), symbols)
    if data.get("symbol_workspaces") != expected_symbol_paths:
        failures.append("symbol workspace paths are missing or noncanonical")
    else:
        for symbol, paths in expected_symbol_paths.items():
            for name, value in paths.items():
                try:
                    validate_artifact(repo_root, str(batch_id), value, f"{symbol} {name}")
                except BatchError as error:
                    failures.append(str(error))
    expected_shared_paths = expected_shared_workspaces(str(batch_id))
    if data.get("shared_workspaces") != expected_shared_paths:
        failures.append("shared workspace paths are missing or noncanonical")
    else:
        for name, value in expected_shared_paths.items():
            try:
                validate_artifact(repo_root, str(batch_id), value, f"shared {name}")
            except BatchError as error:
                failures.append(str(error))
    shared = data.get("shared_stages")
    if not isinstance(shared, dict) or tuple(shared) != SHARED_STAGES:
        failures.append("shared stages are missing or out of order")
    else:
        for name, record in shared.items():
            if not isinstance(record, dict) or record.get("status") not in SHARED_WORK_STATUSES:
                failures.append(f"invalid shared stage: {name}")
                continue
            if final and record["status"] not in SHARED_TERMINAL_STATUSES:
                failures.append(f"nonterminal shared stage: {name}")
            if record.get("status") in SHARED_TERMINAL_STATUSES:
                if not isinstance(record.get("note"), str) or len(record["note"].strip()) < 20:
                    failures.append(f"terminal shared stage lacks substantive note: {name}")
                ids = record.get("evidence_ids")
                if not isinstance(ids, list) or not ids or any(
                    not isinstance(item, str) or len(item) < 3 for item in ids
                ):
                    failures.append(f"terminal shared stage lacks evidence/attempt IDs: {name}")
                    ids = []
                try:
                    artifact = validate_artifact(
                        repo_root, str(batch_id), record.get("artifact_path"), f"shared {name} artifact_path"
                    )
                    artifact_text = (repo_root / artifact).read_text(encoding="utf-8")
                    if "Not started" in artifact_text or "Not researched" in artifact_text:
                        failures.append(f"terminal shared artifact contains placeholders: {name}")
                    if any(item not in artifact_text for item in ids):
                        failures.append(f"terminal shared artifact omits evidence/attempt IDs: {name}")
                except BatchError as error:
                    failures.append(str(error))
    symbol_lanes = data.get("symbol_lanes")
    if not isinstance(symbol_lanes, dict) or list(symbol_lanes) != symbols:
        failures.append("symbol lane coverage is incomplete or misordered")
    else:
        for symbol, lanes in symbol_lanes.items():
            if not isinstance(lanes, dict) or tuple(lanes) != REQUIRED_LANES:
                failures.append(f"{symbol} lane coverage is incomplete or misordered")
                continue
            for lane, record in lanes.items():
                if not isinstance(record, dict) or record.get("status") not in WORK_STATUSES:
                    failures.append(f"invalid {symbol} lane: {lane}")
                    continue
                if final and record["status"] not in TERMINAL_STATUSES:
                    failures.append(f"nonterminal {symbol} lane: {lane}")
                if record.get("status") in TERMINAL_STATUSES:
                    if not isinstance(record.get("note"), str) or len(record["note"].strip()) < 20:
                        failures.append(f"terminal {symbol} lane lacks substantive note: {lane}")
                    ids = record.get("evidence_ids")
                    if not isinstance(ids, list) or not ids or any(
                        not isinstance(item, str) or len(item) < 3 for item in ids
                    ):
                        failures.append(f"terminal {symbol} lane lacks evidence/attempt IDs: {lane}")
                        ids = []
                    try:
                        artifact = validate_artifact(
                            repo_root, str(batch_id), record.get("artifact_path"), f"{symbol}/{lane} artifact_path"
                        )
                        symbol_prefix = f"research/batches/{batch_id}/symbols/{symbol}/"
                        if not artifact.startswith(symbol_prefix):
                            failures.append(f"{symbol}/{lane} artifact is outside its exclusive workspace")
                        artifact_text = (repo_root / artifact).read_text(encoding="utf-8")
                        if "Not started" in artifact_text or "Not researched" in artifact_text:
                            failures.append(f"terminal {symbol}/{lane} artifact contains placeholders")
                        if any(item not in artifact_text for item in ids):
                            failures.append(f"terminal {symbol}/{lane} artifact omits evidence/attempt IDs")
                    except BatchError as error:
                        failures.append(str(error))
    expected_corrections = f"research/batches/{batch_id}/CORRECTIONS.jsonl"
    if data.get("corrections_path") != expected_corrections:
        failures.append("correction ledger path is missing or noncanonical")
    else:
        try:
            corrections = load_corrections(repo_root / expected_corrections, str(batch_id))
            latest_corrections: dict[tuple[str, str | None, str], dict[str, Any]] = {}
            for record in corrections:
                key = (record.get("scope"), record.get("symbol"), record.get("target"))
                latest_corrections[key] = record
            for (scope, symbol, target), record in latest_corrections.items():
                current = (
                    data.get("shared_stages", {}).get(target)
                    if scope == "shared"
                    else data.get("symbol_lanes", {}).get(symbol, {}).get(target)
                )
                if current != record.get("replacement"):
                    failures.append(f"RUN.json does not reconcile with latest correction: {scope}/{symbol or ''}/{target}")
        except BatchError as error:
            failures.append(str(error))
    blockers = data.get("blockers")
    if not isinstance(blockers, list) or any(not isinstance(item, str) or len(item.strip()) < 20 for item in blockers):
        failures.append("blockers must be an array of substantive strings")
    batch_status = data.get("batch_status")
    if batch_status not in {"in_progress", "complete", "partial"}:
        failures.append("invalid batch_status")
    if final and batch_status == "in_progress":
        failures.append("final checkpoint cannot remain in_progress")
    all_statuses: list[str] = []
    if isinstance(shared, dict):
        all_statuses.extend(record.get("status") for record in shared.values() if isinstance(record, dict))
    if isinstance(symbol_lanes, dict):
        for lanes in symbol_lanes.values():
            if isinstance(lanes, dict):
                all_statuses.extend(record.get("status") for record in lanes.values() if isinstance(record, dict))
    if final:
        expected = "partial" if "blocked" in all_statuses else "complete"
        if batch_status != expected:
            failures.append(f"batch_status must be {expected} for its terminal lane states")
        macro = repo_root / "research" / "batches" / str(batch_id) / "MACRO.md"
        macro_text = macro.read_text(encoding="utf-8") if macro.is_file() else ""
        for phrase in (
            MACRO_MARKER,
            f"Batch ID: {batch_id}",
            "## Evidence Ledger",
            "## Regime Scenarios",
            "## Per-Symbol Transmission Inputs",
            "## Limitations",
        ):
            if phrase not in macro_text:
                failures.append(f"shared macro artifact is missing: {phrase}")
        macro_stage = shared.get("macro_regime", {}).get("status") if isinstance(shared, dict) else None
        expected_macro_status = "Complete" if macro_stage == "complete" else "Blocked"
        if f"- Status: {expected_macro_status}" not in macro_text:
            failures.append("shared macro artifact status does not match RUN.json")
        if "Not researched" in macro_text or "- Status: Not started" in macro_text:
            failures.append("final shared macro artifact still contains placeholders")
        if "blocked" in all_statuses and not blockers:
            failures.append("blocked final batch must list substantive blockers")
    return failures


def initialize(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    path = run_path(repo_root, args.batch_id)
    cutoff = parse_time(args.decision_cutoff, "decision_cutoff")
    created = parse_time(args.created_at, "created_at")
    if created < cutoff:
        raise BatchError("created_at cannot precede decision_cutoff")
    records = parse_active_universe(repo_root / "SYMBOLS.md")
    symbols, universe_hash = universe_state(repo_root)
    symbol_workspaces = expected_symbol_workspaces(args.batch_id, symbols)
    shared_workspaces = expected_shared_workspaces(args.batch_id)
    if path.exists():
        raise BatchError(f"batch already exists: {args.batch_id}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": SCHEMA,
        "batch_id": args.batch_id,
        "batch_status": "in_progress",
        "decision_cutoff": args.decision_cutoff,
        "created_at": args.created_at,
        "updated_at": args.created_at,
        "reporting_currency": "USD",
        "research_depth_contract": "full-depth-v1",
        "universe_sha256": universe_hash,
        "active_symbols": symbols,
        "symbol_workspaces": symbol_workspaces,
        "shared_workspaces": shared_workspaces,
        "corrections_path": f"research/batches/{args.batch_id}/CORRECTIONS.jsonl",
        "shared_stages": {
            stage: {
                "status": "not_started",
                "note": None,
                "artifact_path": None,
                "evidence_ids": [],
                "updated_at": None,
            }
            for stage in SHARED_STAGES
        },
        "symbol_lanes": {
            symbol: {
                lane: {
                    "status": "not_started",
                    "note": None,
                    "artifact_path": None,
                    "evidence_ids": [],
                    "updated_at": None,
                }
                for lane in REQUIRED_LANES
            }
            for symbol in symbols
        },
        "blockers": [],
    }
    skill_root = Path(__file__).resolve().parents[1]
    latest_template = (skill_root / "assets" / "LATEST.template.md").read_text(encoding="utf-8")
    for record in records:
        workspace = symbol_workspaces[record.symbol]
        write_exclusive_text(repo_root / workspace["latest_draft"], render(latest_template, record))
        write_exclusive_text(
            repo_root / workspace["decision_draft"],
            json.dumps(
                {
                    "price_status": None,
                    "horizon_view": None,
                    "decision": None,
                    "confidence": None,
                    "next_review": None,
                },
                indent=2,
            )
            + "\n",
        )
        write_exclusive_text(
            repo_root / workspace["calculations"],
            f"# {record.symbol} — Batch Calculations\n\n"
            "<!-- analyst-template: symbol-batch-calculations-v1 -->\n\n"
            f"- Batch ID: {args.batch_id}\n- Decision cutoff: {args.decision_cutoff}\n\n"
            "## Reconciliations\n\nNot started.\n\n"
            "## Forecast And Valuation Calculations\n\nNot started.\n\n"
            "## Downside And 5x Calculations\n\nNot started.\n",
        )
        write_exclusive_text(
            repo_root / workspace["evidence"],
            f"# {record.symbol} — Batch Evidence Ledger\n\n"
            "<!-- analyst-template: symbol-batch-evidence-v1 -->\n\n"
            f"- Batch ID: {args.batch_id}\n- Decision cutoff: {args.decision_cutoff}\n\n"
            "Record eligible and ineligible evidence, attempt IDs, timing, identity, units, contradictions, and claims here.\n",
        )
    macro = repo_root / shared_workspaces["macro_regime"]
    macro_content = (
        "# Shared Macro Regime\n\n"
        f"{MACRO_MARKER}\n\n"
        f"- Batch ID: {args.batch_id}\n"
        f"- Decision cutoff: {args.decision_cutoff}\n"
        "- Status: Not started\n\n"
        "## Evidence Ledger\n\nNot researched.\n\n"
        "## Regime Scenarios\n\nNot researched.\n\n"
        "## Per-Symbol Transmission Inputs\n\nNot researched.\n\n"
        "## Limitations\n\nNot researched.\n"
    )
    shared_titles = {
        "identity_registry": "Batch Identity Registry",
        "provider_preflight": "Provider Preflight And Source Availability",
        "central_reconciliation": "Central Reconciliation",
        "publication": "Batch Publication Reconciliation",
    }
    for stage, title in shared_titles.items():
        write_exclusive_text(
            repo_root / shared_workspaces[stage],
            f"# {title}\n\n<!-- analyst-template: symbol-batch-shared-v1 -->\n\n"
            f"- Batch ID: {args.batch_id}\n- Decision cutoff: {args.decision_cutoff}\n"
            "- Status: Not started\n\n## Evidence And Work\n\nNot started.\n",
        )
    write_exclusive_text(macro, macro_content)
    write_exclusive_text(repo_root / data["corrections_path"], "")
    write_exclusive_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"PASS initialized {args.batch_id} with {len(symbols)} symbols")
    return 0


def update_record(args: argparse.Namespace, shared: bool) -> int:
    repo_root = args.repo_root.resolve()
    path, data = load_run(repo_root, args.batch_id)
    parse_time(args.updated_at, "updated_at")
    previous = parse_time(data.get("updated_at"), "checkpoint updated_at")
    current = parse_time(args.updated_at, "updated_at")
    if current < previous:
        raise BatchError("updated_at cannot move backward")
    allowed_statuses = SHARED_WORK_STATUSES if shared else WORK_STATUSES
    if args.status not in allowed_statuses:
        raise BatchError(f"invalid status: {args.status}")
    if len(args.note.strip()) < 20:
        raise BatchError("checkpoint note must contain at least 20 characters")
    evidence_ids = args.evidence_id or []
    if len(evidence_ids) != len(set(evidence_ids)) or any(len(item.strip()) < 3 for item in evidence_ids):
        raise BatchError("evidence IDs must be unique substantive identifiers")
    if args.status in TERMINAL_STATUSES and not evidence_ids:
        raise BatchError("terminal checkpoint requires at least one evidence or attempt ID")
    artifact_path = None
    if args.artifact_path:
        artifact_path = validate_artifact(repo_root, args.batch_id, args.artifact_path, "artifact_path")
    if args.status in TERMINAL_STATUSES and artifact_path is None:
        raise BatchError("terminal checkpoint requires a persisted batch artifact")
    if shared:
        if args.stage not in SHARED_STAGES:
            raise BatchError(f"invalid shared stage: {args.stage}")
        target = data["shared_stages"][args.stage]
        label = args.stage
    else:
        if args.symbol not in data.get("symbol_lanes", {}) or args.lane not in REQUIRED_LANES:
            raise BatchError("unknown symbol or lane")
        target = data["symbol_lanes"][args.symbol][args.lane]
        label = f"{args.symbol}/{args.lane}"
    if target.get("status") in TERMINAL_STATUSES:
        raise BatchError(f"terminal checkpoint cannot be changed without a correction: {label}")
    if not shared:
        symbol_prefix = f"research/batches/{args.batch_id}/symbols/{args.symbol}/"
        if artifact_path and not artifact_path.startswith(symbol_prefix):
            raise BatchError(f"symbol lane artifact must remain inside {symbol_prefix}")
    target.update(
        {
            "status": args.status,
            "note": args.note.strip(),
            "artifact_path": artifact_path,
            "evidence_ids": evidence_ids,
            "updated_at": args.updated_at,
        }
    )
    data["updated_at"] = args.updated_at
    atomic_replace(path, data)
    print(f"PASS checkpointed {label} as {args.status}")
    return 0


def batch_snapshot_exists(repo_root: Path, batch_id: str, symbols: list[str]) -> bool:
    for symbol in symbols:
        manifest = repo_root / "research" / "symbols" / symbol / "history" / "MANIFEST.jsonl"
        if not manifest.is_file():
            continue
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if line.strip() and json.loads(line).get("batch_id") == batch_id:
                return True
    return False


def correct_record(args: argparse.Namespace, shared: bool) -> int:
    repo_root = args.repo_root.resolve()
    path, data = load_run(repo_root, args.batch_id)
    corrected_at = parse_time(args.updated_at, "updated_at")
    if corrected_at < parse_time(data.get("updated_at"), "checkpoint updated_at"):
        raise BatchError("updated_at cannot move backward")
    allowed_statuses = SHARED_WORK_STATUSES if shared else WORK_STATUSES
    if args.status not in allowed_statuses:
        raise BatchError(f"invalid correction status: {args.status}")
    if len(args.note.strip()) < 20 or len(args.correction_reason.strip()) < 30:
        raise BatchError("correction note/reason is not substantive")
    evidence_ids = args.evidence_id or []
    if len(evidence_ids) != len(set(evidence_ids)) or any(len(item.strip()) < 3 for item in evidence_ids):
        raise BatchError("correction evidence IDs must be unique substantive identifiers")
    artifact_path = None
    if args.artifact_path:
        artifact_path = validate_artifact(repo_root, args.batch_id, args.artifact_path, "artifact_path")
    if args.status in TERMINAL_STATUSES and (not evidence_ids or artifact_path is None):
        raise BatchError("terminal correction requires a persisted artifact and evidence/attempt IDs")
    if shared:
        if args.stage not in SHARED_STAGES:
            raise BatchError(f"invalid shared stage: {args.stage}")
        target = data["shared_stages"][args.stage]
        target_name = args.stage
        symbol = None
        scope = "shared"
        affected_symbols = data["active_symbols"]
    else:
        if args.symbol not in data.get("symbol_lanes", {}) or args.lane not in REQUIRED_LANES:
            raise BatchError("unknown symbol or lane")
        target = data["symbol_lanes"][args.symbol][args.lane]
        target_name = args.lane
        symbol = args.symbol
        scope = "symbol"
        affected_symbols = [args.symbol]
        symbol_prefix = f"research/batches/{args.batch_id}/symbols/{args.symbol}/"
        if artifact_path and not artifact_path.startswith(symbol_prefix):
            raise BatchError(f"symbol lane artifact must remain inside {symbol_prefix}")
    if target.get("status") not in TERMINAL_STATUSES:
        raise BatchError("correction command applies only to a terminal checkpoint")
    if batch_snapshot_exists(repo_root, args.batch_id, affected_symbols):
        raise BatchError("batch is already snapshotted; preserve it and create a new corrective batch")
    previous = json.loads(json.dumps(target))
    replacement = {
        "status": args.status,
        "note": args.note.strip(),
        "artifact_path": artifact_path,
        "evidence_ids": evidence_ids,
        "updated_at": args.updated_at,
    }
    target.clear()
    target.update(replacement)
    data["updated_at"] = args.updated_at
    correction_path = repo_root / data["corrections_path"]
    existing = load_corrections(correction_path, args.batch_id)
    correction: dict[str, Any] = {
        "schema_version": CORRECTION_SCHEMA,
        "batch_id": args.batch_id,
        "scope": scope,
        "symbol": symbol,
        "target": target_name,
        "previous": previous,
        "replacement": replacement,
        "reason": args.correction_reason.strip(),
        "corrected_at": args.updated_at,
        "previous_record_sha256": existing[-1]["record_sha256"] if existing else None,
    }
    correction["record_sha256"] = content_hash(correction)
    atomic_replace(path, data)
    with correction_path.open("a", encoding="utf-8") as handle:
        handle.write(canonical(correction).decode("utf-8") + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    print(f"PASS corrected {scope}/{symbol or ''}/{target_name} to {args.status}")
    return 0


def finalize(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    path, data = load_run(repo_root, args.batch_id)
    current = parse_time(args.updated_at, "updated_at")
    if current < parse_time(data.get("updated_at"), "checkpoint updated_at"):
        raise BatchError("updated_at cannot move backward")
    statuses = [record["status"] for record in data["shared_stages"].values()]
    for lanes in data["symbol_lanes"].values():
        statuses.extend(record["status"] for record in lanes.values())
    nonterminal = [status for status in statuses if status not in TERMINAL_STATUSES]
    if nonterminal:
        raise BatchError(f"cannot finalize with {len(nonterminal)} nonterminal lane(s)")
    data["batch_status"] = "partial" if "blocked" in statuses else "complete"
    data["updated_at"] = args.updated_at
    failures = validate_run(repo_root, data, final=True)
    if failures:
        raise BatchError("; ".join(failures))
    atomic_replace(path, data)
    print(f"PASS finalized {args.batch_id} as {data['batch_status']}")
    return 0


def verify(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    _, data = load_run(repo_root, args.batch_id)
    failures = validate_run(repo_root, data, final=args.final)
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print(f"PASS verified batch {args.batch_id} ({'final' if args.final else 'checkpoint'})")
    return 0


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--batch-id", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init_parser = commands.add_parser("init")
    add_common(init_parser)
    init_parser.add_argument("--decision-cutoff", required=True)
    init_parser.add_argument("--created-at", required=True)
    init_parser.set_defaults(handler=initialize)
    shared_parser = commands.add_parser("set-shared")
    add_common(shared_parser)
    shared_parser.add_argument("--stage", required=True)
    shared_parser.add_argument("--status", required=True)
    shared_parser.add_argument("--note", required=True)
    shared_parser.add_argument("--artifact-path")
    shared_parser.add_argument("--evidence-id", action="append")
    shared_parser.add_argument("--updated-at", required=True)
    shared_parser.set_defaults(handler=lambda args: update_record(args, True))
    lane_parser = commands.add_parser("set-lane")
    add_common(lane_parser)
    lane_parser.add_argument("--symbol", required=True)
    lane_parser.add_argument("--lane", required=True)
    lane_parser.add_argument("--status", required=True)
    lane_parser.add_argument("--note", required=True)
    lane_parser.add_argument("--artifact-path")
    lane_parser.add_argument("--evidence-id", action="append")
    lane_parser.add_argument("--updated-at", required=True)
    lane_parser.set_defaults(handler=lambda args: update_record(args, False))
    correct_shared_parser = commands.add_parser("correct-shared")
    add_common(correct_shared_parser)
    correct_shared_parser.add_argument("--stage", required=True)
    correct_shared_parser.add_argument("--status", required=True)
    correct_shared_parser.add_argument("--note", required=True)
    correct_shared_parser.add_argument("--artifact-path")
    correct_shared_parser.add_argument("--evidence-id", action="append")
    correct_shared_parser.add_argument("--correction-reason", required=True)
    correct_shared_parser.add_argument("--updated-at", required=True)
    correct_shared_parser.set_defaults(handler=lambda args: correct_record(args, True))
    correct_lane_parser = commands.add_parser("correct-lane")
    add_common(correct_lane_parser)
    correct_lane_parser.add_argument("--symbol", required=True)
    correct_lane_parser.add_argument("--lane", required=True)
    correct_lane_parser.add_argument("--status", required=True)
    correct_lane_parser.add_argument("--note", required=True)
    correct_lane_parser.add_argument("--artifact-path")
    correct_lane_parser.add_argument("--evidence-id", action="append")
    correct_lane_parser.add_argument("--correction-reason", required=True)
    correct_lane_parser.add_argument("--updated-at", required=True)
    correct_lane_parser.set_defaults(handler=lambda args: correct_record(args, False))
    finalize_parser = commands.add_parser("finalize")
    add_common(finalize_parser)
    finalize_parser.add_argument("--updated-at", required=True)
    finalize_parser.set_defaults(handler=finalize)
    verify_parser = commands.add_parser("verify")
    add_common(verify_parser)
    verify_parser.add_argument("--final", action="store_true")
    verify_parser.set_defaults(handler=verify)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.handler(args)
    except (BatchError, RuntimeError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
