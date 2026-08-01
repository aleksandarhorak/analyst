# Financial Agent Prompt Cookbook

Replace bracketed fields before submitting a prompt. Add `respond in chat only`
when you do not want repository changes, or `preserve a versioned repository
result` when the workflow should update its governed output files.

## General Template

```text
Analyze [company/instrument/question] for [decision purpose].

Scope: [research / valuation / portfolio risk / execution / education]
Exact instrument: [issuer, ticker, exchange, share class, contract, fund, product]
Market and currency: [market], [currency]
As of: [current time or historical decision cutoff]
Horizon: [time horizon]
Capacity: [impersonal research / synthetic client exercise / other]

Use current primary sources and preserve publication times and data vintages.
Separate reported facts, calculations, estimates, scenarios, and opinions.
Show material inputs, downside, costs, alternatives, disconfirming evidence,
invalidation, and unresolved questions. If evidence is insufficient, abstain
instead of inventing values.

Deliver: [format]. [Respond in chat only / preserve a versioned repository result].
```

## Optional Modifiers

Append only the modifiers that match the request:

```text
Do not edit files; answer in chat only.
```

```text
Preserve the result in the repository using its immutable history and tested
delivery workflow. Do not publish remotely.
```

```text
Use bounded parallel subagents for genuinely independent lanes where useful.
Give every lane the same identity, cutoff, units, and evidence rules. Keep
dependent work, shared files, Git operations, regulated judgments, and final
synthesis with the lead agent.
```

`do symbols research` already enables suitable bounded parallel lanes; this
modifier is mainly for other large requests.

## Complete Watchlist Research

### Complete Watchlist Batch

```text
do symbols research
```

This exact command runs the potentially hours-long, resumable master workflow
for every active row in `SYMBOLS.md`. It automatically composes every applicable
identity/evidence, price, company-fundamental or product, valuation/scenario,
news, shared-macro and per-symbol transmission, observable behavior, complete
impersonal thesis, four-horizon forecast, downside/5x, and monitoring lane. A
missing dependency blocks only dependent outputs; all feasible work continues.

The agent preserves one batch ID, cutoff, universe hash, checkpoint, shared
macro artifact, batch-local drafts/calculations/evidence ledgers, immutable
per-symbol decisions, and a reconciled `REPORT.md`. It resumes unfinished lanes
without changing the cutoff or rewriting completed history. Central
reconciliation precedes snapshots; governed pre-snapshot corrections are
hash-chained, while post-snapshot corrections use a new batch. A run with
external blockers is `partial`, not falsely `complete`.

Portfolio fit requires supplied positions and mandate. Suitability requires
governed client facts, jurisdiction, and capacity. Detailed execution requires
instrument/venue, side, size, urgency, and time window. The batch never invents
those inputs and never places orders.

## Company Research And Valuation

The recipes in this and the next section can be run alone. The complete
watchlist command invokes each applicable specialist workflow automatically;
they are not optional follow-up steps for that batch.

### Research One Company

```text
Perform an evidence-led fundamental analysis of [TICKER] on [EXCHANGE], as of
now, in USD, for an impersonal [3-year] investment horizon. Verify the issuer
and share class first. Use the latest filings, earnings materials, and other
primary sources. Analyze the business model, industry position, revenue and
margin drivers, financial statements, earnings quality, liquidity, debt,
capital allocation, governance, dilution, and distress risks. Reconcile material
numbers and distinguish facts from estimates. Finish with strengths, risks,
disconfirmers, invalidation conditions, missing evidence, and what should be
researched next. Do not make a personalized recommendation.
```

### Value a Company

```text
Value [COMPANY/TICKER] as of [DATE] in [CURRENCY] after verifying its exact
security and reviewing current primary evidence. Build economically linked
base, bull, and bear forecasts. Use at least two suitable valuation methods,
such as DCF, reverse DCF, comparables, or sum of parts. Show revenue, margin,
reinvestment, free-cash-flow, net-debt, dilution, discount-rate, and terminal
assumptions. Reconcile enterprise value to equity value and provide a valuation
range with sensitivities, scenario triggers, probabilities only if defensible,
and the evidence that would invalidate each case.
```

### Build a Complete Investment Thesis

```text
Build an auditable, impersonal investment thesis for [EXACT SECURITY] as of
[DATE/TIME], in [CURRENCY], over [HORIZON]. First verify current evidence, then
analyze fundamentals, valuation, macro exposure, material news, observable
market behavior, downside, liquidity, and implementation risk. State the
variant view, what the market may be pricing, base/bull/bear outcomes,
catalysts, costs, disconfirmers, invalidation, and monitoring plan. Compare the
idea with cash and reasonable alternatives. Keep security merit, portfolio fit,
client suitability, and execution as separate decisions. Abstain if a missing
input could reverse the conclusion.
```

## Markets, Events, And Economics

### Analyze Current News or an Earnings Release

```text
Analyze the market significance of [EVENT/CLAIM] for [EXACT ENTITY OR
INSTRUMENT] as of now. Verify the event with primary sources, reconstruct event
time versus publication time, and identify revisions. Establish what was
expected beforehand, what is genuinely new, and whether the information affects
cash flows, discount rates, financing, regulation, or only temporary flows.
Separate facts from inference, test materiality, note contradictory evidence,
and assess what may already be reflected in price without claiming that price
alone proves sentiment. Provide near-term and long-term implications,
disconfirmers, and the next observable checkpoints.
```

### Analyze the Macroeconomy

```text
Assess [COUNTRY/REGION] macro conditions as of [DATE] for a [HORIZON] outlook.
Use current primary central-bank and statistical-agency releases with the
correct vintages. Distinguish real from nominal values, levels from changes,
seasonally adjusted from unadjusted data, and initial releases from revisions.
Cover growth, inflation, labor, monetary and fiscal policy, credit, financial
conditions, currency, and external balances. Build base, upside, and downside
regimes with triggers and explain the transmission to [ASSET/SECTOR/PORTFOLIO].
State confidence, causal limitations, disconfirmers, and the next releases that
could change the view.
```

### Analyze a Commodity or Futures Contract

```text
Analyze [EXACT COMMODITY, EXCHANGE, CONTRACT MONTH OR BROKER PRODUCT] as of
[DATE/TIME], quoted in [CURRENCY AND NATIVE UNIT], over [HORIZON]. Resolve the
contract identity, multiplier, settlement, expiry, delivery rules, margin, and
roll construction before using prices. Assess physical supply and demand,
inventories, term structure, basis, seasonality, positioning and its reporting
lag, macro/FX exposure, liquidity, daily mark-to-market, and gap/liquidation
risk. Build base/bull/bear scenarios and separate spot, futures, fund, and CFD
economics. Do not treat a generic alias as a tradable instrument.
```

### Assess Market Behavior Without Guessing Psychology

```text
Assess observable market behavior around [SYMBOL/EVENT] from [START] through
[CUTOFF]. Use timestamped price, volume, volatility, flows, positioning,
survey, and news-expectation evidence where available. Identify the relevant
participants and horizon. Test attention, reference-point, underreaction,
overreaction, extrapolation, disposition, and herding explanations against
alternatives and falsifiers. Do not infer investor psychology from price alone.
Explain whether the evidence is descriptive, forecast-useful, or plausibly
causal, and state what observation would disconfirm each interpretation.
```

## Portfolio And Broker Support

### Review a Portfolio Using Synthetic Data

```text
Using only this synthetic portfolio, assess portfolio fit and risk as of
[DATE]: [POSITIONS, VALUES, CURRENCY, AND SYNTHETIC CONSTRAINTS]. Evaluate
concentration, factor and currency exposures, correlations, leverage, liquidity,
gap risk, financing, drawdown, and exit capacity. Run transparent scenarios and
stress tests, identify risk-budget breaches, and compare hold, reduce, hedge,
and cash alternatives. Separate thesis quality from portfolio fit. Show all
assumptions and calculations and do not place or route orders.
```

Do not paste real client identity, holdings, accounts, tax information, or
communications into this repository. For real client work, first use:

```text
Before handling any real client facts, apply the client-data governance gate.
Describe the approved secure-system, minimization, access, retention, deletion,
and redaction requirements. Do not copy client data into repository files,
retained prompts, fixtures, logs, forecasts, or reports.
```

### Review Suitability Without Inventing Client Facts

```text
Provide a suitability-gate checklist for considering [EXACT PRODUCT] in
[JURISDICTION] for a [CLIENT TYPE] in [PROFESSIONAL CAPACITY]. This is
[impersonal education / a synthetic exercise]. Verify current primary rules.
Identify the client facts that must be established, product knowledge, maximum
loss, leverage, liquidity, fees, financing, tax issues, conflicts, alternatives,
and series-of-transactions risks. Do not assume missing facts or conclude that
the recommendation is suitable. Mark all legal/compliance conclusions for
qualified human review.
```

### Plan Trade Execution Without Placing an Order

```text
Design an advisory execution plan for [EXACT INSTRUMENT AND VENUE], [SIDE],
[SIZE], with [URGENCY] and [TIME WINDOW]. Use current spread, depth, volume,
volatility, resilience, auction/halt, queue, fill, adverse-selection, and market-
impact evidence. Compare suitable order strategies and estimate commissions,
spread, impact, delay, fees/rebates, financing or borrow, FX, tax, and exit cost.
Define an implementation-shortfall benchmark, safeguards, stop conditions, and
post-trade review. Do not submit, route, modify, or cancel any order.
```

## Evidence And Forecasting

### Verify a Financial Claim at a Historical Cutoff

```text
Verify this claim as it could have been known at [DECISION CUTOFF]: [CLAIM].
Resolve the exact entity/instrument, use primary point-in-time sources, and
exclude information published after the cutoff. Preserve event time,
publication time, access time, revision/vintage, units, currency, fiscal period,
corporate actions, and contradictions. Produce an evidence ledger that labels
reported facts, derived facts, estimates, and unknowns, then state whether the
claim is supported, contradicted, or unresolved.
```

### Request Directional Probabilities

```text
For [EXACT INSTRUMENT], as of [CUTOFF], assess up/flat/down probabilities over
[HORIZON]. Define the unlevered flat band and make the probabilities total 100%.
Use only validated evidence available before the cutoff, explain the calibration
basis and uncertainty, and register the forecast before publication. If no
defensible calibration basis or verified starting value exists, state
"insufficient evidence" and do not invent probabilities. Include outcome date,
invalidation, and the evidence needed for later resolution.
```

## Repository Operations

### Add or Archive a Watchlist Symbol

```text
Update the watchlist for [SYMBOL/INSTRUMENT]. Verify the exact identity and
record an explicit as-of timestamp and research reason. [Add it with Observe
status / archive it with the date and reason]. Preserve existing decision and
history files; do not erase prior views. Run the symbol validators and report
the exact files changed.
```

### Evaluate the Agent

This recipe validates a change to the agent, policy, skill, tool, or model (or
an explicit evaluation request). It is not routine per-symbol research.

```text
Evaluate the financial agent after [CHANGE]. Use the evaluate-financial-agent
workflow with leakage-safe candidate inputs, public adverse cases, a controlled
hidden set if available, repeated runs, a frozen baseline, critical safety
gates, numerical reconciliation, temporal-integrity checks, and blinded human
review for nuanced quality. Report score distributions, regressions, critical
failures, hashes, limitations, and an accept/reject decision. Do not describe a
fixture replay as evidence of model or forecast skill.
```

### Improve This Repository

```text
Inspect the whole repository and improve [CAPABILITY]. Read AGENTS.md and every
matching skill before acting. Preserve unrelated work, use bounded parallel
subagents for independent read-only inspections where useful, follow the tested-
delivery workflow, add regression tests, run the full quality gate, and merge
passing work into local dev. Report changed files, commits, tests, limitations,
and whether anything was pushed.
```

## Weak Versus Strong Requests

Avoid requests such as:

```text
What stock will double?
Tell me if gold goes up tomorrow.
Make this portfolio safe.
Buy the best trade for me.
```

They omit identity, cutoff, horizon, currency, decision context, and risk
constraints—and may ask for certainty or authority the agent does not have.

A stronger request defines the instrument and horizon, requires current primary
evidence, requests scenarios and downside, and asks for alternatives,
uncertainty, disconfirmers, and invalidation. Use the [general template](#general-template)
as the starting point.
