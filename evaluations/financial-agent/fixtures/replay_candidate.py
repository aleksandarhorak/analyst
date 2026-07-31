#!/usr/bin/env python3
"""Return the synthetic passing response for an evaluation case on stdin."""

from __future__ import annotations

import json
from pathlib import Path
import sys


case = json.load(sys.stdin)
responses_path = Path(__file__).resolve().with_name("passing-responses.jsonl")
responses = {
    value["id"]: value
    for line in responses_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
    for value in [json.loads(line)]
}
json.dump(responses[case["id"]], sys.stdout)
