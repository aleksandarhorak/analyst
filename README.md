# Financial Analyst Agent

This repository configures an evidence-led financial analyst and broker-support
agent. It is designed for research, valuation, probabilistic forecasting,
portfolio-risk review, execution planning, and suitability support while making
important claims auditable.

It does **not** provide professional licensure, promise returns, hold brokerage
authority, or place orders. When identity, current evidence, client facts, or
product terms are insufficient, the correct result is an explicit abstention.

## Quick Start

Open this repository in Codex or another compatible agent environment that
loads [`AGENTS.md`](AGENTS.md) and the skills under [`.codex/skills/`](.codex/skills/).
There is no application server to start. Ask the agent for the analysis or
repository task in normal language; it will select the relevant skills.

For the maintained watchlist, use this exact prompt:

```text
do symbols research
```

That request covers every active row in [`SYMBOLS.md`](SYMBOLS.md), updates the
per-symbol research history, and replaces [`REPORT.md`](REPORT.md). It may need
internet access and an authorized market-data/news source. Symbols without
decision-grade evidence will remain `insufficient evidence` rather than receive
invented prices or probabilities.

## How to Write a Strong Prompt

The agent performs best when the request identifies:

- the entity or exact instrument, including exchange, contract month, fund, or
  broker product when relevant;
- the decision question and whether the work is research, portfolio support,
  broker support, or education;
- the as-of time, forecast horizon, market, and currency;
- the evidence cutoff or instruction to use current primary sources;
- the desired output, such as a memo, table, scenarios, valuation range, or
  monitoring plan;
- material constraints, including leverage, liquidity, tax, mandate, or risk
  limits;
- whether the request is impersonal or uses a synthetic client profile.

Use this general template and replace the bracketed fields:

```text
Analyze [company/instrument/question] for [decision purpose].

Scope: [research / valuation / portfolio risk / execution / education]
Exact instrument: [issuer, ticker, exchange, share class, contract, fund, or product]
Market and currency: [market], [currency]
As of: [current time or historical decision cutoff]
Horizon: [time horizon]
Capacity: [impersonal research / synthetic client exercise / other]

Use current primary sources and preserve publication times and data vintages.
Separate reported facts, calculations, estimates, scenarios, and opinions.
Show material inputs, downside, costs, alternatives, disconfirming evidence,
invalidation conditions, and unresolved questions. If evidence is insufficient,
abstain instead of inventing values.

Deliver: [requested format].
```

## Copy-Ready Prompts

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

Do not paste real client identity, holdings, account details, tax information,
or communications into this repository. For real client work, use an approved
secure client system and prompt the agent first:

```text
Before handling any real client facts, apply the client-data governance gate.
Describe the approved secure-system, minimization, access, retention, deletion,
and redaction requirements. Do not copy client data into repository files,
prompts retained by the repository, fixtures, logs, forecasts, or reports.
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

### Add or Archive a Watchlist Symbol

```text
Update the watchlist for [SYMBOL/INSTRUMENT]. Verify the exact identity and
record an explicit as-of timestamp and research reason. [Add it with Observe
status / archive it with the date and reason]. Preserve existing decision and
history files; do not erase prior views. Run the symbol validators and report
the exact files changed.
```

### Evaluate the Agent

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
matching skill before acting. Preserve unrelated work, use the repository's
tested-delivery workflow, add regression tests for the changed behavior, run
the full quality gate, and merge passing work into local dev. Report changed
files, commits, tests, remaining limitations, and whether anything was pushed.
```

## Prompts That Produce Weak Results

Avoid vague requests such as:

```text
What stock will double?
Tell me if gold goes up tomorrow.
Make this portfolio safe.
Buy the best trade for me.
```

They omit identity, evidence cutoff, horizon, currency, decision context, and
risk constraints—and may ask for certainty or authority the agent does not
have. A stronger version asks for a defined instrument and horizon, current
evidence, scenarios, downside, alternatives, uncertainty, and invalidation.

## Expected Output

A substantial response should normally contain:

1. scope, exact instrument/entity, market, currency, capacity, horizon, and
   as-of timestamp;
2. a concise conclusion and confidence level;
3. primary evidence close to each material claim;
4. reconciled calculations and clearly labeled estimates;
5. base, bull, and bear scenarios when uncertainty is material;
6. downside, liquidity, costs, conflicts, alternatives, and execution issues;
7. disconfirming evidence, invalidation conditions, monitoring triggers, and
   unresolved questions.

An `insufficient evidence` result is intentional. It means the available data
cannot support a decision without increasing the risk of a false claim.

## Repository Outputs

- [`SYMBOLS.md`](SYMBOLS.md): maintained universe and current status summary.
- [`REPORT.md`](REPORT.md): latest complete watchlist batch.
- [`research/symbols/`](research/symbols/): latest views, append-only decisions,
  and immutable point-in-time histories.
- [`forecasts/`](forecasts/): evidence-linked forecast and outcome ledgers.
- [`evaluations/`](evaluations/): public regression cases, fixtures, and
  evaluation documentation.
- [`MEMORY.md`](MEMORY.md): durable architecture facts and known operational
  limits; it must never contain client information.

## Maintainer Checks

Run the full repository gate after a clean documentation, policy, skill, or
code change:

```bash
scripts/agent-quality-gate.sh
```

Focused regression commands include:

```bash
python3 scripts/test-financial-data.py
python3 scripts/test-financial-evals.py
python3 scripts/test-forecast-calibration.py
python3 scripts/test-symbol-history.py
python3 scripts/check-client-data.py --self-test
python3 scripts/check-symbol-research.py
```

Repository edits must follow the feature/fix branch, verified commit, prepared
merge, and clean `dev` workflow defined in [`AGENTS.md`](AGENTS.md). Publishing
to a remote is a separate, explicit action.
