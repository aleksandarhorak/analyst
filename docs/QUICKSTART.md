# Five-Minute Agent Walkthrough

This walkthrough shows what to request and what the agent should do. Entering
the prompt takes less than five minutes; a complete current research batch may
take hours depending on universe size, source access, filings, product
complexity, and valuation work. The workflow checkpoints progress, updates many
files, and runs tests.

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
data-rich symbols. It means the complete applicable analytical pipeline, not a
price/news scan or a list of optional follow-ups.

### 2. Identity resolution

The agent first resolves the exact issuer, share class, exchange, contract,
fund, index, or broker product. A generic alias such as a commodity name or
platform index is not silently treated as a future, ETF, spot index, or CFD.

Unresolved identities remain visible and stop instrument-specific market-data
or execution conclusions.

### 3. Batch contract and resumable checkpoint

The agent establishes one UTC batch ID, decision cutoff, active-universe hash,
reporting currency, source hierarchy, and lane contract. It initializes
`research/batches/<batch-id>/RUN.json` and a shared `MACRO.md`. If interrupted,
it resumes batch-local per-symbol drafts, calculations, evidence/attempt
ledgers, and shared reconciliation from the same branch, TODO, batch, cutoff,
and unfinished lanes after
verifying completed immutable artifacts. It never introduces evidence published
after the preserved cutoff into the resumed decision.

Independent symbol groups or analytical lanes may run in bounded parallel work.
They share identity, cutoff, units, and evidence rules; the lead alone owns
shared files, snapshots, Git operations, reconciliation, and final synthesis.

### 4. Evidence acquisition and verification

The agent sets one UTC decision cutoff and seeks point-in-time evidence. It
preserves event, publication, access, and revision times; validates identifiers,
currency, units, session, freshness, and rights; and excludes after-cutoff or
failed packets.

One conclusion may stop at `insufficient evidence` when an authorized adapter
or decisive source is unavailable, but the rest of that symbol's independent
lanes and the other symbols continue. A missing price cannot excuse skipped
filing, business/product, news, macro, behavior, thesis, or monitoring work.

### 5. Full-depth analysis and forecast gate

For each symbol, the workflow completes identity/evidence, price/market,
fundamental or asset-specific product, valuation/scenario, news, macro
transmission, observable behavior, impersonal thesis, directional forecast,
downside/5x, and monitoring lanes. Every lane ends complete, justified
abstention, blocked, or not applicable with evidence and a next action.

Portfolio fit runs only with positions and a mandate; suitability only with
governed client facts and jurisdiction; detailed execution only with exact
instrument/venue, side, size, urgency, and time window. Those inputs are never
invented.

Up/flat/down probabilities are published only with a verified starting value,
defined flat band, defensible calibration basis, and preregistration. Otherwise
the horizon records `insufficient evidence` without invented percentages.

### 6. Versioned outputs

The agent updates:

- [`../REPORT.md`](../REPORT.md) for the complete current batch;
- `research/batches/<batch-id>/RUN.json` and `MACRO.md` for resumable state and
  the shared point-in-time regime, plus per-symbol drafts/calculations and
  shared identity, preflight, reconciliation, publication, and correction files;
- `research/symbols/<SYMBOL>/LATEST.md` for each latest view;
- `research/symbols/<SYMBOL>/DECISIONS.md` append-only decision history;
- `research/symbols/<SYMBOL>/history/` immutable snapshots and manifests;
- [`../SYMBOLS.md`](../SYMBOLS.md) only when verified identity or status facts
  materially change.

It then runs the affected validators and follows the tested branch/merge
workflow. It does not push unless the user separately says `publish`.

The agent validates that every active symbol has terminal lane state and a
current immutable snapshot for the same batch. External blockers make the batch
`partial`; nonterminal lanes prevent publication.

### 7. Read the result

A safe summary can look like this:

```text
Conclusion: Full-depth batch finished with explicit partial status and blockers.
Coverage: Every active row and every applicable analytical lane accounted for.
Completed work: Fundamentals/product, news, macro transmission, and bounded
thesis are preserved where sources allowed them.
Abstentions/blockers: See the per-symbol lane and forecast records.
Files: RUN.json, MACRO.md, REPORT.md, per-symbol state and immutable histories.
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
