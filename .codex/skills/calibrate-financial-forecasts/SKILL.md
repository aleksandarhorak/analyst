---
name: calibrate-financial-forecasts
description: Register directional financial forecasts before outcomes, append independently verified outcomes, and score Brier loss, log loss, accuracy, coverage, and calibration by horizon, asset class, and regime. Use whenever an analysis assigns up/flat/down probabilities, evaluates forecast skill, compares versions, monitors drift, or considers recalibration.
---

# Calibrate Financial Forecasts

## Boundary

Measure forecast behavior; do not optimize a live recommendation against an
outcome already known. Forecast and outcome ledgers are append-only. Never edit,
delete, backdate, or re-register a record to improve a score.

Read [the ledger contract](references/forecast-ledger-contract.md) before
registering a new model or changing band/outcome treatment.

## Procedure

1. Before the outcome, define stable forecast ID, UTC cutoff/creation/target
   times, exact instrument, start value and unit, horizon, asset class, regime,
   unlevered flat-return band, up/flat/down probabilities, method version, and
   supporting `evidence-packet-v1` IDs.
2. Register the record with `scripts/forecast_ledger.py register`. Probabilities
   are decimals totaling 1.0; the flat band must contain zero.
3. After the target time, acquire the realized total-return observation with
   point-in-time evidence. Make corporate-action, distribution, futures-roll,
   currency, session, and missing-market-day treatment explicit.
4. Append one outcome with `resolve`. The script derives up/flat/down from the
   registered band and rejects a second resolution.
5. Run `verify`, then `score`. Report sample size, coverage/abstention, multiclass
   Brier loss, log loss, accuracy, and reliability bins. Break results out by
   horizon, asset class, regime, and method version when sample size permits.
6. Compare against simple unconditional and prior-version baselines. Treat small
   groups and empty bins as insufficient evidence; do not select a method on the
   same holdout used for final comparison.
7. If performance breaches a predeclared threshold, investigate data drift,
   band definition, outcome treatment, regime, and method before recalibrating.
   Register a new method version; preserve the old records.

## Rules

- Score the unlevered underlying forecast. Leverage changes P&L and liquidation
  paths, not directional forecast correctness.
- Use total-return or contract-consistent outcomes. A raw split-adjusted price
  discontinuity is not a return.
- Publish log-loss clipping epsilon, bin width, sample size, unresolved count,
  and exclusions.
- An abstention is not a directional forecast. Track it in coverage rather than
  inventing probabilities or scoring it as success.
- Git is a second audit layer, not a substitute for record hashes and write-once
  commands.

## Output

Provide verified ledger counts, metrics and reliability bins, baseline
comparison, sparse-sample warnings, worst cases, drift signals, and a
continue/recalibrate/redevelop decision with a new-version plan.
