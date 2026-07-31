# Forecast Ledger Contract

## Forecast Record (`forecast-record-v1`)

Required input fields:

- `forecast_id`, `created_at`, `decision_cutoff`, `target_at`
- `instrument_id`, `symbol`, `asset_class`, `horizon`, `regime`
- `start_value`, `unit`, `currency`
- `flat_band.lower_return`, `flat_band.upper_return`
- `probabilities.up`, `probabilities.flat`, `probabilities.down`
- `method_version`, `evidence_packet_ids`

Timestamps are timezone-aware ISO 8601 values. Return bands and probabilities
are decimal numbers, not percentages. The target follows the cutoff; creation
must be no earlier than the cutoff and no later than the target. Evidence packet
IDs use `sha256:<64 lowercase hex>`.

## Outcome Input

Required fields:

- `forecast_id`, `resolved_at`, `outcome_as_of`, `realized_return`
- `outcome_packet_id`
- `corporate_action_treatment`, `fx_treatment`

The registered flat band determines the outcome category. `outcome_as_of` must
be at or after `target_at`, and resolution must be at or after the observed
outcome. Use an evidence packet for the exact total-return or contract-consistent
observation. Document closures, holidays, distributions, splits, symbol changes,
rolls, settlement, and currency conversion in the treatment strings.

## Integrity

Each JSONL line contains `record_sha256`, calculated from canonical JSON without
that field. Writers take an exclusive file lock, verify existing records, reject
duplicate forecast or outcome IDs, append one complete line, flush, and `fsync`.
Verification rejects malformed JSON, hashes, schemas, duplicates, orphan
outcomes, category mismatches, and impossible time ordering.

The repository implementation is a single-host ledger. Use a transactional,
access-controlled store with the same logical contract for concurrent multi-host
deployment.

## Metrics

- Multiclass Brier: sum of squared error across up/flat/down; lower is better.
- Log loss: negative log probability assigned to the realized class, clipped at
  a disclosed epsilon; lower is better.
- Accuracy: deterministic maximum-probability class equals the outcome.
- Coverage: resolved forecasts divided by registered forecasts. Abstentions are
  tracked separately if the calling workflow maintains them.
- Reliability bins: for each class, compare average predicted probability with
  observed frequency in fixed-width bins and always publish bin counts.

Aggregate metrics alone can conceal regime or asset failure. Always inspect the
all-sample group and eligible horizon, asset-class, regime, and method groups.
