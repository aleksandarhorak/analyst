#!/usr/bin/env python3
"""Synthetic provider process for contract and preflight regressions."""

from __future__ import annotations

import json
import os
import sys
import time


def main() -> int:
    request = json.load(sys.stdin)
    request_id = request["request_id"]
    if "SYNTHETIC_UNRELATED_SECRET" in os.environ:
        print("unrelated parent environment leaked", file=sys.stderr)
        return 9
    if request_id.startswith("allowed-env"):
        if os.environ.get("SYNTHETIC_PROVIDER_KEY") != "synthetic-provider-value":
            print("explicit provider environment missing", file=sys.stderr)
            return 8
    if request_id.startswith("timeout"):
        time.sleep(1)
    if request_id.startswith("nonzero"):
        print("synthetic confidential diagnostic", file=sys.stderr)
        return 7
    if request_id.startswith("invalid-json"):
        sys.stdout.write("not-json")
        return 0
    if request_id.startswith("oversized"):
        sys.stdout.write("x" * (21 * 1024 * 1024))
        return 0

    cutoff = request["decision_cutoff"]
    kind = request["kind"]
    common = {
        "field": "last_trade" if kind == "price" else "headline",
        "value": 200.25 if kind == "price" else "Synthetic issuer update",
        "unit": "USD_per_share" if kind == "price" else None,
        "currency": "USD" if kind == "price" else None,
        "classification": "reported_fact",
        "event_time": cutoff,
        "published_at": cutoff,
        "as_of": cutoff,
        "source_locator": f"synthetic:{kind}:{request_id}",
    }
    if kind == "price":
        common.update(
            {
                "session": request["requirements"]["session"],
                "latency": "real_time",
                "adjustment": "unadjusted",
            }
        )
    else:
        common.update(
            {
                "publisher": "Synthetic Wire",
                "canonical_url": f"https://news.example/{request_id}",
                "correction_status": "original",
                "document_id": f"document:{request_id}",
                "headline": "Synthetic issuer update",
                "updated_at": cutoff,
            }
        )
    response = {
        "schema_version": "provider-response-v1",
        "request_id": request_id,
        "provider": "synthetic-process-provider",
        "complete": True,
        "instrument": request["instrument"],
        "source_url": f"https://provider.example/records/{request_id}",
        "rights": "Synthetic fixture; redistribution allowed",
        "observations": [common],
        "errors": [],
    }
    json.dump(response, sys.stdout, separators=(",", ":"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
