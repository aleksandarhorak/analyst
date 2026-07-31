---
name: build-investment-thesis
description: Synthesize verified fundamentals, valuation, macro, news, portfolio, and execution evidence into an auditable investment thesis. Use for a full investment memo, recommendation research, variant view, monitoring plan, or decision packet after the relevant specialist analyses are available.
---

# Build Investment Thesis

## Purpose

Orchestrate existing evidence; do not hide missing specialist work behind a
confident narrative. A supported security thesis does not automatically imply a
portfolio position or suitable client recommendation.

## Workflow

1. Define instrument, jurisdiction/capacity, currency, price and as-of time,
   horizon, mandate, and decision question.
2. Use `verify-financial-evidence` for the evidence ledger.
3. Use the relevant specialist skills for fundamentals, valuation, macro, and
   news. Keep their conclusions and confidence visible.
4. State market-implied expectations and the variant view. Explain why the
   difference may exist and what closes it.
5. Construct coherent base, bull, and bear cases with catalysts, path,
   valuation, probability or qualitative confidence, and time horizon.
6. Steelman the opposing case. List disconfirming evidence, thesis invalidation,
   failure modes, and monitoring signals.
7. Use `manage-portfolio-risk` for mandate fit and sizing, then
   `plan-trade-execution` for implementation feasibility and costs.
8. If a person or account will receive a recommendation, require
   `check-broker-suitability`; otherwise label the output impersonal research.
9. Reconcile each conclusion to evidence and make unresolved gaps prominent.

Use [the investment-memo template](references/investment-memo.md).

## Decision Rule

Conclude with one of: supported for further decision, watch pending named
evidence, unsupported, or abstain. Avoid mechanical buy/sell labels when client,
portfolio, price, or compliance context is incomplete.

## Output Quality

The memo must let another analyst reproduce the central calculations, see the
strongest contrary case, understand the range of outcomes after costs, and know
exactly what evidence would change the view.
