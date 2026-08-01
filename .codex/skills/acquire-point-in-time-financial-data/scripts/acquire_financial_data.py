#!/usr/bin/env python3
"""Acquire official or provider data into a validated evidence-packet-v1."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


SCHEMA_VERSION = "evidence-packet-v1"
ADAPTER_VERSION = "1.0.0"
MAX_RESPONSE_BYTES = 20 * 1024 * 1024
DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / "references/instrument-registry-v1.json"
PACKET_FIELDS = {
    "schema_version", "packet_id", "created_at", "decision_cutoff", "adapter",
    "source", "request", "instrument", "observations", "quality",
}
REQUIRED_OBSERVATION_FIELDS = {
    "claim_id",
    "field",
    "value",
    "unit",
    "currency",
    "classification",
    "event_time",
    "published_at",
    "as_of",
    "revision",
    "source_locator",
}
CLASSIFICATIONS = {"reported_fact", "derived_fact", "estimate", "scenario", "opinion"}
OBSERVATION_FIELDS = REQUIRED_OBSERVATION_FIELDS | {"metadata"}
INSTRUMENT_FIELDS = {"id", "symbol", "asset_class", "venue", "resolution_status"}
SENSITIVE_KEYS = {
    "api_key", "apikey", "authorization", "password", "secret", "token", "access_token",
    "client_secret", "private_key",
}


class AcquisitionError(RuntimeError):
    """An expected fail-closed acquisition or validation error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_datetime(value: str, field: str) -> datetime:
    if not isinstance(value, str):
        raise AcquisitionError(f"{field} must be an ISO 8601 date-time with timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise AcquisitionError(f"{field} must be an ISO 8601 date-time with timezone") from error
    if parsed.tzinfo is None:
        raise AcquisitionError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def temporal_after_cutoff(value: str, cutoff: datetime) -> bool:
    try:
        if len(value) == 10:
            return date.fromisoformat(value) > cutoff.date()
        return parse_datetime(value, "observation time") > cutoff
    except ValueError as error:
        raise AcquisitionError(f"invalid observation date: {value}") from error


def validate_date_or_datetime(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise AcquisitionError(f"{field} must be a nonempty ISO 8601 date or date-time")
    try:
        if len(value) == 10:
            date.fromisoformat(value)
        else:
            parse_datetime(value, field)
    except ValueError as error:
        raise AcquisitionError(f"{field} must be an ISO 8601 date or date-time") from error


def exact_fields(value: Any, required: set[str], allowed: set[str], field: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{field} must be an object"]
    errors: list[str] = []
    if missing := required - value.keys():
        errors.append(f"{field} missing fields: {sorted(missing)}")
    if extra := value.keys() - allowed:
        errors.append(f"{field} has unsupported fields: {sorted(extra)}")
    return errors


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalize_identity_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def load_registry(path: Path) -> dict[str, dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AcquisitionError(f"instrument registry is unreadable: {error}") from error
    errors = exact_fields(
        data,
        {"schema_version", "as_of", "source", "instruments"},
        {"schema_version", "as_of", "source", "instruments"},
        "instrument registry",
    )
    if errors:
        raise AcquisitionError("; ".join(errors))
    if data["schema_version"] != "instrument-registry-v1":
        raise AcquisitionError("instrument registry schema mismatch")
    try:
        date.fromisoformat(data["as_of"])
    except (TypeError, ValueError) as error:
        raise AcquisitionError("instrument registry as_of must be an ISO date") from error
    source_errors = exact_fields(
        data["source"],
        {"authority", "url", "accessed_at", "scope"},
        {"authority", "url", "accessed_at", "scope"},
        "instrument registry source",
    )
    if source_errors:
        raise AcquisitionError("; ".join(source_errors))
    if not str(data["source"].get("url", "")).startswith("https://"):
        raise AcquisitionError("instrument registry source URL must use HTTPS")
    parse_datetime(data["source"].get("accessed_at"), "instrument registry accessed_at")
    instruments = data.get("instruments")
    if not isinstance(instruments, list) or not instruments:
        raise AcquisitionError("instrument registry instruments must be a nonempty array")
    registry: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(instruments):
        if not isinstance(item, dict):
            raise AcquisitionError(f"instrument registry entry {index} must be an object")
        key = item.get("key")
        status = item.get("resolution_status")
        if not nonempty_string(key) or key in registry:
            raise AcquisitionError(f"instrument registry entry {index} has missing or duplicate key")
        if status == "resolved":
            required = {
                "key", "resolution_status", "instrument_id", "symbol", "name", "asset_class",
                "venue", "currency", "security_type", "identifiers",
            }
            errors = exact_fields(item, required, required, f"instrument registry entry {key}")
            if errors:
                raise AcquisitionError("; ".join(errors))
            for field in ("instrument_id", "symbol", "name", "asset_class", "security_type"):
                if not nonempty_string(item[field]):
                    raise AcquisitionError(f"instrument registry entry {key} has invalid {field}")
            if item["venue"] is not None and not nonempty_string(item["venue"]):
                raise AcquisitionError(f"instrument registry entry {key} has invalid venue")
            if item["currency"] is not None and not nonempty_string(item["currency"]):
                raise AcquisitionError(f"instrument registry entry {key} has invalid currency")
            if not isinstance(item["identifiers"], dict) or not item["identifiers"]:
                raise AcquisitionError(f"instrument registry entry {key} lacks identifiers")
        elif status == "unresolved":
            required = {"key", "resolution_status", "name", "asset_class", "reason"}
            errors = exact_fields(item, required, required, f"instrument registry entry {key}")
            if errors:
                raise AcquisitionError("; ".join(errors))
            if any(not nonempty_string(item[field]) for field in ("name", "asset_class", "reason")):
                raise AcquisitionError(f"instrument registry entry {key} is incomplete")
        else:
            raise AcquisitionError(f"instrument registry entry {key} has invalid resolution_status")
        registry[key] = item
    return registry


def registry_entry(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry(args.registry)
    key = args.registry_key or args.symbol
    entry = registry.get(key)
    if entry is None:
        raise AcquisitionError(f"instrument registry has no entry for {key}")
    if entry["resolution_status"] != "resolved":
        raise AcquisitionError(f"instrument {key} is unresolved: {entry['reason']}")
    expected = {
        "instrument_id": args.instrument_id,
        "symbol": args.symbol,
        "asset_class": args.asset_class,
        "venue": args.venue,
    }
    for field, supplied in expected.items():
        if entry[field] != supplied:
            raise AcquisitionError(
                f"instrument registry mismatch for {field}: expected {entry[field]!r}, got {supplied!r}"
            )
    return entry


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json_bytes(raw: bytes, context: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AcquisitionError(f"{context} did not return valid UTF-8 JSON") from error


def read_limited_file(path: Path) -> bytes:
    if path.stat().st_size > MAX_RESPONSE_BYTES:
        raise AcquisitionError(f"fixture exceeds {MAX_RESPONSE_BYTES} bytes")
    return path.read_bytes()


def fetch_bytes(url: str, user_agent: str, timeout: float, retries: int) -> bytes:
    request = Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:  # noqa: S310 - explicit HTTPS endpoints
                length = response.headers.get("Content-Length")
                if length and int(length) > MAX_RESPONSE_BYTES:
                    raise AcquisitionError(f"response exceeds {MAX_RESPONSE_BYTES} bytes")
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise AcquisitionError(f"response exceeds {MAX_RESPONSE_BYTES} bytes")
                return raw
        except HTTPError as error:
            last_error = error
            if error.code != 429 and not 500 <= error.code < 600:
                break
        except URLError as error:
            last_error = error
        if attempt < retries:
            time.sleep(min(2**attempt, 4))
    raise AcquisitionError(f"HTTPS acquisition failed after {retries + 1} attempt(s): {last_error}")


def acquire_raw(
    input_file: Path | None,
    network_url: str,
    user_agent: str,
    timeout: float,
    retries: int,
) -> bytes:
    if input_file:
        return read_limited_file(input_file)
    return fetch_bytes(network_url, user_agent, timeout, retries)


def normalize_number(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    try:
        number = float(stripped)
    except ValueError:
        return value
    if not math.isfinite(number):
        raise AcquisitionError("non-finite numeric value")
    return int(number) if number.is_integer() else number


def sensitive_paths(value: Any, path: str = "request") -> list[str]:
    matches: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).casefold().replace("-", "_")
            child_path = f"{path}.{key}"
            if normalized in SENSITIVE_KEYS:
                matches.append(child_path)
            matches.extend(sensitive_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            matches.extend(sensitive_paths(child, f"{path}[{index}]"))
    return matches


def observation(
    *,
    claim_id: str,
    field: str,
    value: Any,
    unit: str | None,
    currency: str | None,
    event_time: str,
    published_at: str,
    as_of: str,
    revision: dict[str, Any],
    source_locator: str,
    classification: str = "reported_fact",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "claim_id": claim_id,
        "field": field,
        "value": value,
        "unit": unit,
        "currency": currency,
        "classification": classification,
        "event_time": event_time,
        "published_at": published_at,
        "as_of": as_of,
        "revision": revision,
        "source_locator": source_locator,
    }
    if metadata:
        item["metadata"] = metadata
    return item


def build_packet(
    *,
    adapter_name: str,
    authority: str,
    source_url: str,
    rights: str,
    raw: bytes,
    retrieved_at: str,
    cutoff: str,
    request_details: dict[str, Any],
    instrument: dict[str, Any],
    observations: list[dict[str, Any]],
    initial_flags: list[str] | None = None,
    initial_errors: list[str] | None = None,
) -> dict[str, Any]:
    cutoff_time = parse_datetime(cutoff, "decision_cutoff")
    parse_datetime(retrieved_at, "retrieved_at")
    flags = list(initial_flags or [])
    errors = list(initial_errors or [])
    for path in sensitive_paths(request_details):
        errors.append(f"sensitive credential key in packet request: {path}")
    if re.search(r"(?i)(?:api[_-]?key|access[_-]?token|authorization|password|secret)=", source_url):
        errors.append("sensitive credential parameter in source URL")
    seen: set[str] = set()
    if not observations:
        errors.append("no observations matched the explicit request")
    for item in observations:
        missing = REQUIRED_OBSERVATION_FIELDS - item.keys()
        if missing:
            errors.append(f"observation missing fields: {sorted(missing)}")
            continue
        if item["classification"] not in CLASSIFICATIONS:
            errors.append(f"unsupported classification: {item['classification']}")
        claim_id = str(item["claim_id"])
        if claim_id in seen:
            errors.append(f"duplicate claim_id: {claim_id}")
        seen.add(claim_id)
        try:
            if temporal_after_cutoff(str(item["published_at"]), cutoff_time):
                errors.append(f"after-cutoff evidence: {claim_id}")
        except AcquisitionError as error:
            errors.append(f"{claim_id}: {error}")
        if len(str(item["published_at"])) == 10:
            if str(item["published_at"]) == cutoff_time.date().isoformat():
                errors.append(f"cutoff-day date-granularity publication time is ambiguous: {claim_id}")
            else:
                flags.append(f"date-granularity publication time: {claim_id}")
    flags = sorted(set(flags))
    errors = sorted(set(errors))
    status = "fail" if errors else "warning" if flags else "pass"
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "packet_id": "",
        "created_at": retrieved_at,
        "decision_cutoff": cutoff,
        "adapter": {"name": adapter_name, "version": ADAPTER_VERSION},
        "source": {
            "authority": authority,
            "url": source_url,
            "retrieved_at": retrieved_at,
            "raw_sha256": sha256_bytes(raw),
            "rights": rights,
        },
        "request": request_details,
        "instrument": instrument,
        "observations": observations,
        "quality": {"status": status, "flags": flags, "errors": errors},
    }
    packet["packet_id"] = f"sha256:{sha256_bytes(canonical_json({k: v for k, v in packet.items() if k != 'packet_id'}))}"
    return packet


def validate_packet(packet: Any) -> list[str]:
    """Validate the complete dependency-free evidence-packet-v1 contract."""
    errors = exact_fields(packet, PACKET_FIELDS, PACKET_FIELDS, "packet")
    if errors or not isinstance(packet, dict):
        return sorted(set(errors))
    if packet["schema_version"] != SCHEMA_VERSION:
        errors.append("unsupported schema_version")
    packet_id = packet["packet_id"]
    if not isinstance(packet_id, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", packet_id):
        errors.append("packet_id must be a sha256 content identifier")
    expected_id = f"sha256:{sha256_bytes(canonical_json({k: v for k, v in packet.items() if k != 'packet_id'}))}"
    if packet_id != expected_id:
        errors.append("packet_id does not match packet contents")
    try:
        cutoff = parse_datetime(packet["decision_cutoff"], "decision_cutoff")
    except AcquisitionError as error:
        errors.append(str(error))
        cutoff = datetime.max.replace(tzinfo=timezone.utc)
    try:
        parse_datetime(packet["created_at"], "created_at")
    except AcquisitionError as error:
        errors.append(str(error))

    adapter = packet["adapter"]
    errors.extend(exact_fields(adapter, {"name", "version"}, {"name", "version"}, "adapter"))
    if isinstance(adapter, dict):
        if not nonempty_string(adapter.get("name")) or not nonempty_string(adapter.get("version")):
            errors.append("adapter name and version must be nonempty strings")

    source = packet["source"]
    source_fields = {"authority", "url", "retrieved_at", "raw_sha256", "rights"}
    errors.extend(exact_fields(source, source_fields, source_fields, "source"))
    if isinstance(source, dict):
        for field in ("authority", "rights"):
            if not nonempty_string(source.get(field)):
                errors.append(f"source {field} must be a nonempty string")
        source_url = source.get("url")
        if not nonempty_string(source_url) or not source_url.startswith("https://"):
            errors.append("source URL must be a nonempty HTTPS URI")
        raw_sha = source.get("raw_sha256")
        if not isinstance(raw_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", raw_sha):
            errors.append("source raw_sha256 must be 64 lowercase hexadecimal characters")
        try:
            parse_datetime(source.get("retrieved_at"), "source retrieved_at")
        except AcquisitionError as error:
            errors.append(str(error))
    else:
        source_url = ""

    if not isinstance(packet["request"], dict):
        errors.append("request must be an object")
    instrument = packet["instrument"]
    errors.extend(
        exact_fields(
            instrument,
            {"id", "symbol", "asset_class", "resolution_status"},
            INSTRUMENT_FIELDS,
            "instrument",
        )
    )
    if isinstance(instrument, dict):
        for field in ("id", "symbol", "asset_class"):
            if not nonempty_string(instrument.get(field)):
                errors.append(f"instrument {field} must be a nonempty string")
        if instrument.get("venue") is not None and not nonempty_string(instrument.get("venue")):
            errors.append("instrument venue must be a string or null")
        if instrument.get("resolution_status") != "resolved":
            errors.append("instrument is not explicitly resolved")

    observations = packet["observations"]
    if not isinstance(observations, list) or not observations:
        errors.append("observations must be a nonempty array")
    else:
        seen: set[str] = set()
        for index, item in enumerate(observations):
            label = f"observation {index}"
            item_errors = exact_fields(item, REQUIRED_OBSERVATION_FIELDS, OBSERVATION_FIELDS, label)
            errors.extend(item_errors)
            if item_errors or not isinstance(item, dict):
                continue
            claim_id = item["claim_id"]
            if not nonempty_string(claim_id):
                errors.append(f"{label} claim_id must be a nonempty string")
            elif claim_id in seen:
                errors.append(f"duplicate claim_id: {claim_id}")
            seen.add(claim_id)
            for field in ("field", "source_locator"):
                if not nonempty_string(item[field]):
                    errors.append(f"{label} {field} must be a nonempty string")
            for field in ("unit", "currency"):
                if item[field] is not None and not isinstance(item[field], str):
                    errors.append(f"{label} {field} must be a string or null")
            if item["classification"] not in CLASSIFICATIONS:
                errors.append(f"{label} has unsupported classification")
            if not isinstance(item["revision"], dict):
                errors.append(f"{label} revision must be an object")
            if "metadata" in item and not isinstance(item["metadata"], dict):
                errors.append(f"{label} metadata must be an object")
            for field in ("event_time", "published_at", "as_of"):
                try:
                    validate_date_or_datetime(item[field], f"{label} {field}")
                except AcquisitionError as error:
                    errors.append(str(error))
            published = item["published_at"]
            if isinstance(published, str):
                try:
                    if temporal_after_cutoff(published, cutoff):
                        errors.append(f"after-cutoff evidence: {claim_id}")
                    elif len(published) == 10 and published == cutoff.date().isoformat():
                        errors.append(
                            f"cutoff-day date-granularity publication time is ambiguous: {claim_id}"
                        )
                except AcquisitionError as error:
                    errors.append(f"{claim_id}: {error}")

    quality = packet["quality"]
    quality_fields = {"status", "flags", "errors"}
    errors.extend(exact_fields(quality, quality_fields, quality_fields, "quality"))
    if isinstance(quality, dict):
        status = quality.get("status")
        flags = quality.get("flags")
        quality_errors = quality.get("errors")
        if status not in {"pass", "warning", "fail"}:
            errors.append("quality status is invalid")
        if not isinstance(flags, list) or any(not isinstance(item, str) for item in flags):
            errors.append("quality flags must be an array of strings")
        if not isinstance(quality_errors, list) or any(not isinstance(item, str) for item in quality_errors):
            errors.append("quality errors must be an array of strings")
        if isinstance(flags, list) and isinstance(quality_errors, list):
            expected_status = "fail" if quality_errors else "warning" if flags else "pass"
            if status != expected_status:
                errors.append(f"quality status is inconsistent; expected {expected_status}")
        if status == "fail":
            errors.append("packet quality status is fail")

    for path in sensitive_paths(packet["request"]):
        errors.append(f"sensitive credential key in packet request: {path}")
    if re.search(r"(?i)(?:api[_-]?key|access[_-]?token|authorization|password|secret)=", str(source_url)):
        errors.append("sensitive credential parameter in source URL")
    return sorted(set(errors))


def validate_packet_registry(
    packet: dict[str, Any], registry_path: Path, registry_key: str | None
) -> list[str]:
    try:
        registry = load_registry(registry_path)
    except AcquisitionError as error:
        return [str(error)]
    instrument = packet.get("instrument")
    if not isinstance(instrument, dict):
        return ["packet instrument cannot be reconciled to registry"]
    key = registry_key or instrument.get("symbol")
    entry = registry.get(key)
    if entry is None:
        return [f"instrument registry has no entry for {key}"]
    if entry["resolution_status"] != "resolved":
        return [f"instrument {key} is unresolved: {entry['reason']}"]
    packet_identity = {
        "instrument_id": instrument.get("id"),
        "symbol": instrument.get("symbol"),
        "asset_class": instrument.get("asset_class"),
        "venue": instrument.get("venue"),
    }
    return [
        f"packet instrument registry mismatch for {field}: expected {entry[field]!r}, got {actual!r}"
        for field, actual in packet_identity.items()
        if entry[field] != actual
    ]


def instrument_from_args(args: argparse.Namespace) -> dict[str, Any]:
    registry_entry(args)
    return {
        "id": args.instrument_id,
        "symbol": args.symbol,
        "asset_class": args.asset_class,
        "venue": args.venue,
        "resolution_status": "resolved",
    }


def run_sec(args: argparse.Namespace) -> dict[str, Any]:
    entry = registry_entry(args)
    cik = args.cik.zfill(10)
    if entry["identifiers"].get("sec_cik") != cik:
        raise AcquisitionError("SEC CIK does not match instrument registry")
    source_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    user_agent = args.user_agent or os.environ.get("FINANCIAL_DATA_USER_AGENT", "")
    if not args.input_file and not user_agent:
        raise AcquisitionError("live SEC access requires FINANCIAL_DATA_USER_AGENT")
    raw = acquire_raw(args.input_file, source_url, user_agent, args.timeout, args.retries)
    data = load_json_bytes(raw, "SEC EDGAR")
    if not isinstance(data, dict):
        raise AcquisitionError("SEC response must be an object")
    response_cik = str(data.get("cik", "")).zfill(10)
    if response_cik != cik:
        raise AcquisitionError("SEC response CIK does not match request and instrument registry")
    entity_name = data.get("entityName")
    if not nonempty_string(entity_name) or normalize_identity_name(entity_name) != normalize_identity_name(entry["name"]):
        raise AcquisitionError("SEC response issuer name does not match instrument registry")
    try:
        units = data["facts"][args.taxonomy][args.concept]["units"]
    except (KeyError, TypeError) as error:
        raise AcquisitionError("SEC response lacks requested taxonomy/concept units") from error
    selected_units = [args.unit] if args.unit else sorted(units)
    records: list[dict[str, Any]] = []
    for unit in selected_units:
        if unit not in units:
            continue
        for index, fact in enumerate(units[unit]):
            end = fact.get("end")
            filed = fact.get("filed")
            accession = fact.get("accn")
            if end is None or filed is None or accession is None or "val" not in fact:
                continue
            field = f"{args.taxonomy}:{args.concept}"
            records.append(
                observation(
                    claim_id=f"sec:{cik}:{accession}:{field}:{unit}:{index}",
                    field=field,
                    value=fact["val"],
                    unit=unit,
                    currency=unit if len(unit) == 3 and unit.isupper() else None,
                    event_time=end,
                    published_at=filed,
                    as_of=end,
                    revision={"accession": accession, "filed": filed, "frame": fact.get("frame")},
                    source_locator=f"facts.{args.taxonomy}.{args.concept}.units.{unit}[{index}]",
                    metadata={
                        "form": fact.get("form"),
                        "fiscal_year": fact.get("fy"),
                        "fiscal_period": fact.get("fp"),
                        "start": fact.get("start"),
                    },
                )
            )
    flags = [] if args.unit else ["unit not pinned; all reported units retained"]
    return build_packet(
        adapter_name="sec-edgar-companyfacts",
        authority="U.S. Securities and Exchange Commission",
        source_url=source_url,
        rights="Subject to SEC.gov website policies and fair-access requirements",
        raw=raw,
        retrieved_at=args.retrieved_at,
        cutoff=args.decision_cutoff,
        request_details={
            "cik": cik,
            "taxonomy": args.taxonomy,
            "concept": args.concept,
            "unit": args.unit,
        },
        instrument=instrument_from_args(args),
        observations=records,
        initial_flags=flags,
    )


def run_fred(args: argparse.Namespace) -> dict[str, Any]:
    entry = registry_entry(args)
    if entry["identifiers"].get("fred_series_id") != args.series_id:
        raise AcquisitionError("FRED series does not match instrument registry")
    public_query = {
        "series_id": args.series_id,
        "realtime_start": args.realtime_start,
        "realtime_end": args.realtime_end,
        "file_type": "json",
    }
    public_url = f"https://api.stlouisfed.org/fred/series/observations?{urlencode(public_query)}"
    key = os.environ.get("FRED_API_KEY", "")
    if not args.input_file and not key:
        raise AcquisitionError("live FRED access requires FRED_API_KEY")
    network_url = f"{public_url}&api_key={quote(key)}" if key else public_url
    user_agent = args.user_agent or "AnalystFinancialData/1.0"
    raw = acquire_raw(args.input_file, network_url, user_agent, args.timeout, args.retries)
    data = load_json_bytes(raw, "FRED/ALFRED")
    if not isinstance(data, dict) or not isinstance(data.get("observations"), list):
        raise AcquisitionError("FRED response lacks observations")
    records: list[dict[str, Any]] = []
    missing_values = 0
    for index, item in enumerate(data["observations"]):
        if item.get("value") in {None, "."}:
            missing_values += 1
            continue
        event_date = item.get("date")
        known_from = item.get("realtime_start")
        known_until = item.get("realtime_end")
        if not event_date or not known_from or not known_until:
            continue
        records.append(
            observation(
                claim_id=f"fred:{args.series_id}:{event_date}:{known_from}",
                field=args.series_id,
                value=normalize_number(item["value"]),
                unit=args.unit,
                currency=args.currency,
                event_time=event_date,
                published_at=known_from,
                as_of=event_date,
                revision={"realtime_start": known_from, "realtime_end": known_until},
                source_locator=f"observations[{index}]",
                metadata={"frequency": args.frequency},
            )
        )
    flags = [f"{missing_values} missing-value observation(s) omitted"] if missing_values else []
    return build_packet(
        adapter_name="fred-alfred-observations",
        authority="Federal Reserve Bank of St. Louis",
        source_url=public_url,
        rights="Subject to FRED API terms and each series source's usage notes",
        raw=raw,
        retrieved_at=args.retrieved_at,
        cutoff=args.decision_cutoff,
        request_details=public_query,
        instrument=instrument_from_args(args),
        observations=records,
        initial_flags=flags,
    )


def run_cftc(args: argparse.Namespace) -> dict[str, Any]:
    entry = registry_entry(args)
    if entry["identifiers"].get("cftc_contract_market_code") != args.contract_market_code:
        raise AcquisitionError("CFTC contract-market code does not match instrument registry")
    where = f"cftc_contract_market_code='{args.contract_market_code}'"
    query = {"$where": where, "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": args.limit}
    source_url = f"https://publicreporting.cftc.gov/resource/{args.dataset_id}.json?{urlencode(query)}"
    user_agent = args.user_agent or "AnalystFinancialData/1.0"
    raw = acquire_raw(args.input_file, source_url, user_agent, args.timeout, args.retries)
    data = load_json_bytes(raw, "CFTC PRE")
    if not isinstance(data, list):
        raise AcquisitionError("CFTC response must be an array")
    fields = args.field or ["open_interest_all"]
    records: list[dict[str, Any]] = []
    for row_index, row in enumerate(data):
        if row.get("cftc_contract_market_code") != args.contract_market_code:
            continue
        report_date = str(row.get("report_date_as_yyyy_mm_dd", ""))[:10]
        if not report_date:
            continue
        for field in fields:
            if field not in row:
                continue
            records.append(
                observation(
                    claim_id=f"cftc:{args.dataset_id}:{args.contract_market_code}:{report_date}:{field}",
                    field=field,
                    value=normalize_number(row[field]),
                    unit="contracts",
                    currency=None,
                    event_time=report_date,
                    published_at=args.published_at,
                    as_of=report_date,
                    revision={"historical_backdated_updates": False},
                    source_locator=f"rows[{row_index}].{field}",
                    metadata={
                        "market_name": row.get("market_and_exchange_names"),
                        "commodity_name": row.get("commodity_name"),
                        "reporting_lag": "typically Tuesday positions released Friday",
                    },
                )
            )
    return build_packet(
        adapter_name="cftc-cot-pre",
        authority="U.S. Commodity Futures Trading Commission",
        source_url=source_url,
        rights="CFTC public reporting data; verify current web and redistribution policies",
        raw=raw,
        retrieved_at=args.retrieved_at,
        cutoff=args.decision_cutoff,
        request_details={
            "dataset_id": args.dataset_id,
            "contract_market_code": args.contract_market_code,
            "fields": fields,
            "limit": args.limit,
            "published_at": args.published_at,
        },
        instrument=instrument_from_args(args),
        observations=records,
        initial_flags=["COT categories and reportability do not reveal trader intent"],
    )


def provider_request(args: argparse.Namespace) -> dict[str, Any]:
    provider_instrument = instrument_from_args(args)
    provider_instrument.pop("resolution_status")
    return {
        "schema_version": "provider-request-v1",
        "request_id": args.request_id,
        "kind": args.kind,
        "decision_cutoff": args.decision_cutoff,
        "instrument": provider_instrument,
        "requirements": {
            "currency": args.currency,
            "session": args.session,
            "maximum_age_seconds": args.maximum_age_seconds,
        },
    }


def run_provider(args: argparse.Namespace) -> dict[str, Any]:
    registry_entry(args)
    if args.kind == "price":
        if not args.currency or not args.session or args.maximum_age_seconds is None:
            raise AcquisitionError(
                "price provider requests require currency, session, and maximum_age_seconds"
            )
        if args.maximum_age_seconds < 0:
            raise AcquisitionError("maximum_age_seconds must be nonnegative")
    request_payload = provider_request(args)
    if args.input_file:
        raw = read_limited_file(args.input_file)
    else:
        if not args.command:
            raise AcquisitionError("provider requires --input-file or a command after --command")
        try:
            completed = subprocess.run(
                args.command,
                input=canonical_json(request_payload),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=args.timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise AcquisitionError(f"provider process failed: {error}") from error
        if completed.returncode != 0:
            stderr_hash = sha256_bytes(completed.stderr)
            raise AcquisitionError(
                f"provider exited {completed.returncode}; stderr_sha256={stderr_hash}"
            )
        if len(completed.stdout) > MAX_RESPONSE_BYTES:
            raise AcquisitionError(f"provider response exceeds {MAX_RESPONSE_BYTES} bytes")
        raw = completed.stdout
    data = load_json_bytes(raw, "provider")
    if not isinstance(data, dict) or data.get("schema_version") != "provider-response-v1":
        raise AcquisitionError("provider response schema mismatch")
    if data.get("request_id") != args.request_id:
        raise AcquisitionError("provider request_id mismatch")
    provider_instrument = data.get("instrument")
    expected_instrument = request_payload["instrument"]
    if not isinstance(provider_instrument, dict) or provider_instrument != expected_instrument:
        raise AcquisitionError("provider instrument identity mismatch across ID, symbol, venue, or asset class")
    provider_errors = data.get("errors")
    if data.get("complete") is not True or not isinstance(provider_errors, list) or provider_errors:
        raise AcquisitionError("provider response is partial or contains errors")
    if not data.get("provider") or not data.get("rights") or not data.get("source_url"):
        raise AcquisitionError("provider provenance or rights are incomplete")
    source_observations = data.get("observations")
    if not isinstance(source_observations, list):
        raise AcquisitionError("provider observations must be an array")
    records: list[dict[str, Any]] = []
    for index, item in enumerate(source_observations):
        required = {
            "field", "value", "unit", "currency", "classification", "event_time",
            "published_at", "as_of", "source_locator",
        }
        if not isinstance(item, dict) or (missing := required - item.keys()):
            raise AcquisitionError(f"provider observation {index} missing fields: {sorted(missing)}")
        if args.kind == "price":
            if item.get("latency") not in {"real_time", "delayed", "prior_close", "settlement", "indicative"}:
                raise AcquisitionError(f"provider price observation {index} lacks valid latency")
            if not item.get("session"):
                raise AcquisitionError(f"provider price observation {index} lacks session")
            if not item.get("currency"):
                raise AcquisitionError(f"provider price observation {index} lacks currency")
            if item.get("currency") != args.currency:
                raise AcquisitionError(f"provider price observation {index} currency mismatch")
            if item.get("session") != args.session:
                raise AcquisitionError(f"provider price observation {index} session mismatch")
            if not nonempty_string(item.get("adjustment")):
                raise AcquisitionError(f"provider price observation {index} lacks adjustment state")
            cutoff = parse_datetime(args.decision_cutoff, "decision_cutoff")
            as_of = parse_datetime(item.get("as_of"), f"provider observation {index} as_of")
            age_seconds = (cutoff - as_of).total_seconds()
            if age_seconds < 0:
                raise AcquisitionError(f"provider price observation {index} is after the decision cutoff")
            if age_seconds > args.maximum_age_seconds:
                raise AcquisitionError(
                    f"provider price observation {index} is stale: {age_seconds:.0f}s exceeds "
                    f"maximum_age_seconds={args.maximum_age_seconds}"
                )
        if args.kind == "news":
            news_fields = ("publisher", "canonical_url", "correction_status")
            if any(not item.get(field) for field in news_fields):
                raise AcquisitionError(
                    f"provider news observation {index} lacks publisher, canonical URL, or correction status"
                )
        records.append(
            observation(
                claim_id=f"provider:{args.request_id}:{index}:{item['field']}",
                field=item["field"],
                value=item["value"],
                unit=item["unit"],
                currency=item["currency"],
                classification=item["classification"],
                event_time=item["event_time"],
                published_at=item["published_at"],
                as_of=item["as_of"],
                revision=item.get("revision", {}),
                source_locator=item["source_locator"],
                metadata={
                    key: item[key]
                    for key in ("session", "latency", "adjustment", "publisher", "canonical_url", "correction_status")
                    if key in item
                },
            )
        )
    return build_packet(
        adapter_name=f"provider:{data['provider']}",
        authority=data["provider"],
        source_url=data["source_url"],
        rights=data["rights"],
        raw=raw,
        retrieved_at=args.retrieved_at,
        cutoff=args.decision_cutoff,
        request_details=request_payload,
        instrument=instrument_from_args(args),
        observations=records,
    )


def write_packet(packet: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output is None:
        sys.stdout.write(rendered)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(output)


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--instrument-id", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--asset-class", required=True)
    parser.add_argument("--venue")
    parser.add_argument("--decision-cutoff", required=True)
    parser.add_argument("--retrieved-at", default=utc_now())
    parser.add_argument("--input-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--user-agent", default="")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--registry-key")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="adapter", required=True)

    sec = commands.add_parser("sec-companyfacts", help="acquire SEC companyfacts concept data")
    add_common(sec)
    sec.add_argument("--cik", required=True)
    sec.add_argument("--taxonomy", required=True)
    sec.add_argument("--concept", required=True)
    sec.add_argument("--unit")
    sec.set_defaults(handler=run_sec)

    fred = commands.add_parser("fred-observations", help="acquire FRED/ALFRED observations")
    add_common(fred)
    fred.add_argument("--series-id", required=True)
    fred.add_argument("--realtime-start", required=True)
    fred.add_argument("--realtime-end", required=True)
    fred.add_argument("--unit", required=True)
    fred.add_argument("--currency")
    fred.add_argument("--frequency", required=True)
    fred.set_defaults(handler=run_fred)

    cftc = commands.add_parser("cftc-cot", help="acquire CFTC COT PRE observations")
    add_common(cftc)
    cftc.add_argument("--dataset-id", default="72hh-3qpy")
    cftc.add_argument("--contract-market-code", required=True)
    cftc.add_argument("--published-at", required=True)
    cftc.add_argument("--field", action="append")
    cftc.add_argument("--limit", type=int, default=100)
    cftc.set_defaults(handler=run_cftc)

    provider = commands.add_parser("provider", help="acquire an authorized provider response")
    add_common(provider)
    provider.add_argument("--request-id", required=True)
    provider.add_argument("--kind", choices=("price", "news"), required=True)
    provider.add_argument("--currency")
    provider.add_argument("--session")
    provider.add_argument("--maximum-age-seconds", type=int)
    provider.add_argument("--command", nargs=argparse.REMAINDER)
    provider.set_defaults(handler=run_provider)

    validate = commands.add_parser("validate", help="validate an existing evidence packet")
    validate.add_argument("packet", type=Path)
    validate.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    validate.add_argument("--registry-key")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.adapter == "validate":
            packet = json.loads(args.packet.read_text(encoding="utf-8"))
            errors = validate_packet(packet)
            if isinstance(packet, dict):
                errors.extend(validate_packet_registry(packet, args.registry, args.registry_key))
            if errors:
                for error in sorted(set(errors)):
                    print(f"FAIL {error}", file=sys.stderr)
                return 1
            print(f"PASS {packet['packet_id']}")
            return 0
        if args.retries < 0 or args.timeout <= 0:
            raise AcquisitionError("timeout must be positive and retries nonnegative")
        if getattr(args, "limit", 1) <= 0 or getattr(args, "limit", 1) > 5000:
            raise AcquisitionError("CFTC limit must be between 1 and 5000")
        packet = args.handler(args)
        write_packet(packet, args.output)
        if packet["quality"]["status"] == "fail":
            for error in packet["quality"]["errors"]:
                print(f"FAIL {error}", file=sys.stderr)
            return 2
        validation_errors = validate_packet(packet)
        validation_errors.extend(
            validate_packet_registry(packet, args.registry, args.registry_key)
        )
        if validation_errors:
            for error in sorted(set(validation_errors)):
                print(f"FAIL {error}", file=sys.stderr)
            return 1
        return 0
    except (AcquisitionError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
