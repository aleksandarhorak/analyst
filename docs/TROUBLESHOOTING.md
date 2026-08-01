# Troubleshooting

## The Agent Says `Insufficient Evidence`

This is a stop condition, not a generic error. Read the stated missing inputs.
Common causes are:

- unresolved instrument or issuer identity;
- no authorized current price or news packet;
- stale, partial, after-cutoff, wrong-currency, wrong-session, or wrong-unit data;
- incomplete filings, estimates, valuation, portfolio, or product terms;
- no defensible calibration basis or verified forecast starting value;
- missing material client or jurisdiction facts.

Supply or authorize the missing evidence, narrow the question, or accept the
abstention. Do not ask the agent to fill gaps with guesses.

## A Symbol or Alias Is Unresolved

Specify the exact exchange-listed security, share class, fund, benchmark,
contract month, settlement method, continuous-roll rule, or broker product. For
commodities and index aliases, also supply the venue, multiplier, currency,
expiry, margin terms, and whether the exposure is spot, future, ETF, index, or
CFD.

Ticker similarity is not identity. The registry must be updated with verified
stable identifiers before the adapter can accept the instrument.

## Internet or a Source Is Unavailable

Current work requires browsing. Retry only when access is authorized and the
source is expected to be available. Preserve the failure state and cutoff; do
not substitute a later observation into a historical decision or silently use
an aggregator.

Official SEC, FRED/ALFRED, and CFTC acquisition may require network permission.
Live price/news requires a separately authorized provider adapter.

## An Evidence Packet Is Rejected

Run the packet validator and inspect only non-sensitive diagnostics:

```bash
python3 .codex/skills/acquire-point-in-time-financial-data/scripts/acquire_financial_data.py \
  validate /path/outside-repo/packet.json --registry-key AAPL
```

Check:

- exact instrument ID, symbol, venue, share class, and asset class;
- decision cutoff versus event, publication, as-of, and access times;
- maximum age, currency, session, latency, adjustment, units, and revisions;
- completeness, provider errors, source URL, rights, and raw hash;
- unsupported fields or credential-bearing provenance.

Do not weaken validation to accept a convenient packet.

## SEC Requests Fail

For live SEC access, set a descriptive contact value at runtime:

```bash
export FINANCIAL_DATA_USER_AGENT='Organization contact@example.com'
```

Respect SEC fair-access policies. Confirm that the CIK, issuer name, taxonomy,
concept, form, period, and unit match the registry and intended claim.

## FRED or ALFRED Requests Fail

Set `FRED_API_KEY` in the runtime environment or approved secret store. Never
put it in Git, command arguments, packets, screenshots, or logs. For historical
analysis, request explicit `realtime_start` and `realtime_end`; today's revised
value is not a substitute for the value known at the historical cutoff.

## A Watchlist Run Changes Many Files

That is expected for `do symbols research`. A complete batch covers every
active symbol and normally updates root `REPORT.md`, each `LATEST.md`, append-only
`DECISIONS.md`, immutable history snapshots, and hash manifests. `SYMBOLS.md`
changes only for a verified identity, status, or universe change.

Review the batch coverage and manifests; never delete history to reduce the
diff.

## No Directional Probabilities Appear

The agent needs an exact instrument, verified start value, explicit flat band,
one probability distribution totaling 100%, a defensible calibration basis,
and a preregistered outcome definition. If any decisive element is missing, it
should record `insufficient evidence` without percentages.

Future calibration additionally requires the outcome date to arrive and the
verified total-return or contract-consistent outcome packet to be appended.

## The Client-Data Check Fails

Stop. Remove real identity, account, financial, tax, holding, communication,
credential, and payment information from the repository and its pending diff.
Do not merely obfuscate it. Use synthetic fixtures and redacted references; real
client facts belong only in an approved secure client system with authorized
retention and deletion.

Run the self-test and repository scan again:

```bash
python3 scripts/check-client-data.py --self-test
```

## A Fixture Evaluation Scores 100%

The committed passing responses and replay candidate test the evaluation
harness. They do not prove model quality, financial accuracy, multi-agent
orchestration, or forecast skill.

A model claim needs an actual frozen baseline and candidate, repeat runs,
controlled hidden cases, hashes, critical-safety review, and qualified blinded
human judgment. Forecast-skill claims also need genuine preregistered forecasts
and independently verified matured outcomes.

## A Parallel Lane Fails or Conflicts

The lead agent should mark the lane partial or failed, preserve missing coverage,
and verify contradictory sources. It must not concatenate unchecked responses,
vote across conflicting evidence, silently change cutoffs, or let two agents edit
the same file. Re-run a bounded lane when safe; otherwise abstain or report the
unresolved conflict.

## A Quality Gate Fails

Read the first exact failure, repair the smallest underlying issue on the work
branch, rerun the focused test, then rerun the gate. Do not bypass checks, commit
a known failure, or merge failing work into `dev`.

```bash
scripts/agent-quality-gate.sh --stage
scripts/agent-quality-gate.sh
```

For further help, return to the [README](../README.md) or select a more precise
request from the [prompt cookbook](PROMPTS.md).
