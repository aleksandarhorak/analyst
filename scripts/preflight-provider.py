#!/usr/bin/env python3
"""Preflight an authorized price/news adapter without retaining its payload."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
ACQUIRE = (
    REPO_ROOT
    / ".codex/skills/acquire-point-in-time-financial-data/scripts/acquire_financial_data.py"
)
DEFAULT_REGISTRY = (
    REPO_ROOT
    / ".codex/skills/acquire-point-in-time-financial-data/references/instrument-registry-v1.json"
)


class PreflightError(RuntimeError):
    """A safe, user-actionable preflight failure."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def registry_entry(path: Path, key: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PreflightError(f"registry is unreadable: {error}") from error
    matches = [item for item in data.get("instruments", []) if item.get("key") == key]
    if len(matches) != 1:
        raise PreflightError(f"registry must contain exactly one entry for {key}")
    entry = matches[0]
    if entry.get("resolution_status") != "resolved":
        raise PreflightError(f"instrument {key} is unresolved")
    return entry


def run_kind(args: argparse.Namespace, entry: dict, kind: str, directory: Path) -> None:
    cutoff = utc_now()
    packet = directory / f"{kind}.json"
    request_id = f"preflight-{kind}-{cutoff.replace(':', '').replace('-', '')}"
    command = [
        str(Path(sys.executable).resolve()),
        str(ACQUIRE),
        "provider",
        "--registry", str(args.registry),
        "--registry-key", args.registry_key,
        "--instrument-id", entry["instrument_id"],
        "--symbol", entry["symbol"],
        "--asset-class", entry["asset_class"],
        "--decision-cutoff", cutoff,
        "--retrieved-at", cutoff,
        "--output", str(packet),
        "--timeout", str(args.timeout),
        "--request-id", request_id,
        "--kind", kind,
        "--maximum-age-seconds",
        str(
            args.price_maximum_age_seconds
            if kind == "price"
            else args.news_maximum_age_seconds
        ),
    ]
    if entry.get("venue") is not None:
        command.extend(("--venue", entry["venue"]))
    if kind == "price":
        currency = args.currency or entry.get("currency")
        if not currency:
            raise PreflightError("price preflight requires an explicit currency")
        command.extend(("--currency", currency, "--session", args.session))
    for name in args.provider_env or []:
        command.extend(("--provider-env", name))
    command.extend(("--command", *args.command))

    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        diagnostic = completed.stderr.strip() or f"adapter exited {completed.returncode}"
        raise PreflightError(f"{kind} preflight failed: {diagnostic}")
    validate = subprocess.run(
        [
            str(Path(sys.executable).resolve()),
            str(ACQUIRE),
            "validate",
            str(packet),
            "--registry", str(args.registry),
            "--registry-key", args.registry_key,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if validate.returncode != 0:
        raise PreflightError(f"{kind} packet validation failed: {validate.stderr.strip()}")
    value = json.loads(packet.read_text(encoding="utf-8"))
    print(
        f"PASS {kind}: provider={value['source']['authority']}; "
        f"packet_id={value['packet_id']}; observations={len(value['observations'])}; "
        f"quality={value['quality']['status']}; rights_present=yes"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--registry-key", default="AAPL")
    parser.add_argument("--kind", action="append", choices=("price", "news"))
    parser.add_argument("--currency")
    parser.add_argument("--session", default="regular")
    parser.add_argument("--price-maximum-age-seconds", type=int, default=60)
    parser.add_argument("--news-maximum-age-seconds", type=int, default=2_592_000)
    parser.add_argument("--provider-env", action="append")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--command", nargs=argparse.REMAINDER, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if not args.command:
            raise PreflightError("a provider executable is required after --command")
        if not Path(args.command[0]).is_absolute():
            raise PreflightError("provider command must start with an absolute executable path")
        if args.timeout <= 0:
            raise PreflightError("timeout must be positive")
        if args.price_maximum_age_seconds < 0 or args.news_maximum_age_seconds < 0:
            raise PreflightError("maximum ages must be nonnegative")
        entry = registry_entry(args.registry, args.registry_key)
        kinds = list(dict.fromkeys(args.kind or ["price", "news"]))
        with tempfile.TemporaryDirectory(prefix="analyst-provider-preflight-") as temporary:
            directory = Path(temporary)
            for kind in kinds:
                run_kind(args, entry, kind, directory)
        print("PASS provider preflight; temporary packets removed")
        return 0
    except (PreflightError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
