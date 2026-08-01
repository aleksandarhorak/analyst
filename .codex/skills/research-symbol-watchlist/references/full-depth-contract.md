# Full-Depth Watchlist Contract

## Meaning Of The Exact Command

`do symbols research` is the master full-depth workflow for every active row in
`SYMBOLS.md`. It is not a quote scan, a news digest, or a list of optional
follow-up analyses. A run may take hours. It keeps one batch ID, decision cutoff,
active-universe hash, and reporting currency and resumes unfinished lanes rather
than restarting completed work or changing the cutoff.

The batch is impersonal research. It must not invent portfolio holdings, client
facts, jurisdiction, order details, or professional authority.

## Required Lanes

Every active symbol must reach a terminal state in each lane below. `complete`
means the analysis and its evidence are present. `abstained` means the analyst
performed the feasible work but a defensible conclusion is unavailable, with a
specific reason and next action. `blocked` means an external dependency stopped
otherwise feasible work. `not_applicable` requires an asset-specific reason.

1. `identity_evidence`: exact entity, security/product, venue, class, native
   units, currency, and point-in-time source mapping.
2. `price_market`: current or most recent valid value, timestamp, session,
   delay, liquidity context, and USD conversion when needed.
3. `fundamentals_product`: reconciled company fundamentals for equities; exact
   contract, physical/curve/basis/roll/settlement analysis for commodities and
   futures; suitable underlying/index mechanics for other products.
4. `valuation_scenarios`: economically linked base, bull, and bear cases and at
   least two suitable valuation lenses for companies, or a documented reason
   plus a substitute sensitivity. Non-company products receive equivalent
   scenario and payoff analysis rather than a fabricated company valuation.
5. `news_catalysts`: verified chronology, prior expectation, novelty,
   materiality, observed response, and transmission, or a sourced no-material-
   news search result.
6. `macro_transmission`: the shared batch regime mapped to this instrument's
   cash flows, discount rate, currency, demand, financing, or physical balance.
7. `market_behavior`: observable participant- and horizon-specific evidence,
   alternatives, and a falsifier, or a justified abstention from psychology.
8. `investment_thesis`: variant view, market-implied view, scenario outcomes,
   catalysts, contrary case, disconfirmers, invalidation, and decision status.
9. `directional_forecast`: the four fixed horizons, registered distributions
   when defensible, or horizon-specific abstentions.
10. `downside_leverage`: unlevered downside, approximate gross 5x exposure,
    liquidity and implementation risks, costs, path, gap, margin-call, and
    forced-liquidation effects.
11. `monitoring`: evidence that would confirm or disconfirm the view, catalysts,
    outcome dates, and next review.

Headlines do not complete fundamentals, valuation, macro, behavior, thesis, or
risk lanes. An `insufficient evidence` conclusion does not prove the research
was performed; the machine-readable lane record must show what was attempted,
what evidence was reviewed, what specifically remains missing, and the next
action.

Structured v3 state also records the native and USD observation value,
observation time, currency, units, session, live/delayed/close policy, price and
FX evidence IDs, reconciliations, valuation methods and scenarios, news window,
macro channels, observable behavior, thesis components, and monitoring signals.
Preserve contradictory or after-cutoff evidence as ineligible ledger entries;
never let a completed conclusion rely on it. When publication time is unknown,
record a substantive archived availability basis or abstain.

## Dependency Isolation

A missing dependency blocks only outputs that actually depend on it. For
example, an unavailable current price can block price-based valuation,
registered directional forecasts, and quantified downside while filings,
business analysis, product mechanics, news, macro transmission, observable
behavior, and a bounded thesis continue. A provider-wide outage is recorded
once in batch preflight and referenced by affected lanes; it is not permission
for a generic all-symbol response.

An unresolved alias receives a documented product-resolution search and
candidate map. Do not substitute another security, index, future, fund, spot
reference, or CFD. Identity-dependent lanes remain visibly blocked while the
shared macro and other genuinely independent work continues where meaningful.

## Shared And Parallel Work

Run these shared stages once: universe/identity registry, provider preflight,
macro regime, central reconciliation, and publication. Map the shared macro
evidence into every applicable symbol rather than duplicating a generic macro
paragraph.

Use bounded parallel lanes automatically when they are independent. Give every
worker the same identity registry, cutoff, units, source hierarchy, and output
contract. Assign exclusive symbols or files. Workers do read-only acquisition
and analysis by default; the lead owns shared batch state, regulated judgments,
immutable snapshots, `REPORT.md`, Git operations, reconciliation, and final
synthesis. A failed worker remains visible and is retried or marked blocked.

## Resumption And Publication

Initialize `research/batches/<batch-id>/RUN.json` and `MACRO.md` with
`python3 .codex/skills/research-symbol-watchlist/scripts/symbol_research_batch.py init`.
Initialization also creates per-symbol `LATEST.draft.md`, decision, calculation,
and evidence workspaces plus shared identity, preflight, reconciliation,
publication, and hash-chained correction artifacts. Checkpoint each completed
wave with its artifact path and evidence/attempt IDs. Resume the
same branch, TODO, batch ID, cutoff, and completed lane state. Never use evidence
published after the preserved cutoff merely because the run resumed later.

Before snapshotting any symbol, central reconciliation must be complete. Its
governed batch-local `latest-v3` draft must contain a valid
`symbol-research-state-v1` control block and every lane must be terminal. Before
publishing `report-v3`, every active symbol must have a current immutable
snapshot for the same batch, and `RUN.json` must pass final verification. A run
with external blockers is published as `partial`, never mislabeled `complete`.
No active symbol may be silently omitted.

Before snapshot, correct a terminal checkpoint only through `correct-lane` or
`correct-shared`; the change requires a reason and is appended to
`CORRECTIONS.jsonl`. Once a symbol snapshot exists, corrections require a new
batch so the immutable record remains intact.

## Conditional Workflows

- Review portfolio fit or sizing only when positions, mandate, objectives, and
  constraints are supplied.
- Run suitability only after client-data governance and current jurisdiction,
  capacity, and material client facts are established.
- Build a detailed execution plan only with exact product/venue, side, size,
  urgency, and time window. Otherwise report instrument-level liquidity and
  implementation risk only. Never place, route, modify, or cancel an order.
- Historical verification applies to material point-in-time claims; it is not a
  separate generic deliverable for every symbol.
- Agent evaluation validates agent, policy, skill, tool, or model changes (or
  an explicit evaluation request); it is not a routine per-symbol research lane.
