# Forecast Outcome Memory

`forecasts.jsonl` and `outcomes.jsonl` are append-only, hash-chained-by-record
inputs to the forecast calibration workflow. Add records only with
`.codex/skills/calibrate-financial-forecasts/scripts/forecast_ledger.py`.

Never place client data, credentials, licensed payloads, or material non-public
information in these ledgers. Git history supplements, but does not replace,
the script's write-once and hash checks.
