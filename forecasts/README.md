# Forecast Outcome Memory

`forecasts.jsonl` and `outcomes.jsonl` are append-only, individually
content-hashed inputs to the forecast calibration workflow. They are not a
cryptographic chain: Git is the second audit layer for deletion or reordering.
Add records only with
`.codex/skills/calibrate-financial-forecasts/scripts/forecast_ledger.py`.

Registration requires every referenced forecast evidence packet as an
`--evidence-packet`; resolution requires the exact `--outcome-packet`. The
writer validates packet structure, hash, instrument identity, cutoff timing,
and the recorded realized-return observation before appending.

Never place client data, credentials, licensed payloads, or material non-public
information in these ledgers. Git history supplements, but does not replace,
the script's write-once and hash checks.
