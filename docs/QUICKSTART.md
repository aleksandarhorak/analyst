# Five-Minute Agent Walkthrough

This walkthrough shows what to request and what the agent should do. Entering
the prompt takes less than five minutes; a complete current research batch can
take longer because it may browse sources, validate evidence, update many files,
and run tests.

## Before You Start

Confirm that:

- the repository is open in a compatible agent environment;
- the agent can read [`../AGENTS.md`](../AGENTS.md) and `.codex/skills/`;
- internet access is available if you need current information;
- any live price/news adapter is separately authorized and configured;
- the work is impersonal and contains no real client information.

No service or application server needs to be launched.

## Walkthrough: Complete Watchlist

### 1. Enter the exact trigger

```text
do symbols research
```

This is a repository-changing request. It instructs the agent to process every
active row in [`../SYMBOLS.md`](../SYMBOLS.md), not only the most familiar or
data-rich symbols.

### 2. Identity resolution

The agent first resolves the exact issuer, share class, exchange, contract,
fund, index, or broker product. A generic alias such as a commodity name or
platform index is not silently treated as a future, ETF, spot index, or CFD.

Unresolved identities remain visible and stop instrument-specific market-data
or execution conclusions.

### 3. Evidence acquisition and verification

The agent sets one UTC decision cutoff and seeks point-in-time evidence. It
preserves event, publication, access, and revision times; validates identifiers,
currency, units, session, freshness, and rights; and excludes after-cutoff or
failed packets.

Current work may stop at `insufficient evidence` when an authorized quote/news
adapter or decisive primary source is unavailable. This is expected behavior.

### 4. Analysis and forecast gate

For each symbol, the workflow assesses the relevant fundamental, valuation,
macro, news, behavioral, commodity, portfolio, and execution evidence. The
standard horizons are one trading day, two weeks, one month, and two months.

Up/flat/down probabilities are published only with a verified starting value,
defined flat band, defensible calibration basis, and preregistration. Otherwise
the horizon records `insufficient evidence` without invented percentages.

### 5. Versioned outputs

The agent updates:

- [`../REPORT.md`](../REPORT.md) for the complete current batch;
- `research/symbols/<SYMBOL>/LATEST.md` for each latest view;
- `research/symbols/<SYMBOL>/DECISIONS.md` append-only decision history;
- `research/symbols/<SYMBOL>/history/` immutable snapshots and manifests;
- [`../SYMBOLS.md`](../SYMBOLS.md) only when verified identity or status facts
  materially change.

It then runs the affected validators and follows the tested branch/merge
workflow. It does not push unless the user separately says `publish`.

### 6. Read the result

A safe summary can look like this:

```text
Conclusion: Insufficient evidence for directional probabilities.
Coverage: Every active watchlist row processed.
Resolved identities: See the generated report.
Current price packets: Unavailable for specified rows.
Action: Preserve Observe status; resolve aliases and connect authorized data.
Files: REPORT.md, per-symbol LATEST.md and DECISIONS.md, history snapshots.
```

Counts and conclusions belong in the generated [`../REPORT.md`](../REPORT.md),
not this evergreen guide.

## Chat-Only Alternative

For a smaller first experience that should not edit files:

```text
Perform an impersonal fundamental review of AAPL as of now for a three-year
horizon. Verify the exact issuer and share class, use current primary sources,
show material risks and missing evidence, and respond in chat only. Do not edit
repository files.
```

The response should state the identity, cutoff, horizon, evidence used,
conclusion and confidence, calculations, risks, disconfirmers, invalidation,
and unresolved questions.

## Next Steps

- Select another task from the [root task table](../README.md#choose-a-task).
- Copy a detailed request from the [prompt cookbook](PROMPTS.md).
- Diagnose an abstention or failed check with [troubleshooting](TROUBLESHOOTING.md).
- Configure authorized sources with the [provider setup guide](PROVIDERS.md).
