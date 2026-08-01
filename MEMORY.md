# Project Memory

Durable project facts only. Keep this file short, factual, and current. Do not
store chat notes, temporary failures, stale TODOs, guesses, client information,
secrets, or copied research here.

## Mission And Boundaries

- This repository defines an evidence-led financial analyst and broker-support
  agent; it does not grant professional licensure, fiduciary status, legal or
  tax authority, account access, or autonomous order authority.
- The agent separates thesis, portfolio fit, personalized suitability, and
  execution analysis. It abstains when decisive evidence or material client
  facts are missing.
- Decision-ready outputs use point-in-time primary evidence, reconcile material
  numbers, distinguish facts from estimates and opinions, show scenario ranges,
  and expose costs, downside, conflicts, disconfirmers, and invalidation.

## Architecture Decisions

- `AGENTS.md` owns compact non-negotiable conduct and repository workflow.
  Detailed repeatable procedures live in `.codex/skills/<skill-name>/`.
- Retained development capabilities are `technical-research`,
  `implementation-planning`, and `git-tested-delivery`.
- Financial capabilities are evidence verification, company fundamentals,
  valuation and forecasting, macroeconomics, news catalysts, portfolio risk,
  trade-execution planning, investment-thesis synthesis, broker-suitability
  gating, financial-agent evaluation, evidence-bounded market behavior, and a
  full-universe symbol-research workflow. Operational specialist skills also
  cover point-in-time acquisition, forecast calibration, commodity/futures
  analysis, and client-data governance.
- The research basis is tracked under `research/financial-analyst-agent/`: 41
  fully reviewed papers (10 trading, 10 company analysis, 10 economics, and 11
  news) plus current professional and regulatory primary sources as of
  2026-07-31. Local full-text downloads remain ignored.
- Rules and duties vary by jurisdiction, capacity, client, product, and facts.
  Live work retrieves current primary rules and escalates legal or compliance
  conclusions to qualified reviewers.
- `evidence-packet-v1` is the acquisition boundary. Standard-library adapters
  support SEC companyfacts, explicit FRED/ALFRED real-time periods, and CFTC COT
  PRE data; authorized price/news providers use a strict JSON process contract.
  Credentials stay at runtime and failed, partial, misidentified, wrong-unit, or
  stale or after-cutoff packets are unusable. Validation covers the complete
  packet schema, exact registered identity, currency, market session, source
  timestamps, requested cutoff, and quality state. The versioned instrument
  registry records resolved official identities and leaves ambiguous aliases
  unresolved. The design evidence is under
  `research/financial-data-and-model-governance/` as of 2026-08-01.
- Forecasts and outcomes are separate append-only JSONL ledgers under
  `forecasts/`; each record has an independently verifiable content hash rather
  than a hash chain. Registration and resolution require validated evidence
  packets whose identity, timing, return, and interval match the ledger event.
  Calibration reports a fixed baseline, score deltas, sparse-sample warnings,
  worst cases, multiclass Brier/log loss, accuracy, coverage, and reliability
  bins.
- `scripts/run-financial-evals.py` withholds all assertions and expected values
  from candidate input, validates case structure, supports repeated runs and a
  fixed baseline, and records public/holdout, rubric, scorer, candidate,
  response, and candidate-input hashes. The public suite contains 21 adverse
  cases across the financial and safety lanes. The recorded replay result is a
  harness verification only, not evidence of model quality.
- `SYMBOLS.md` is the active-universe source of truth. The exact user request
  `do symbols research` triggers current online price and news research for
  every active row, with no silent omissions.
- Durable symbol memory lives under `research/symbols/<SYMBOL>/`: `LATEST.md`,
  append-only `DECISIONS.md`, and immutable `history/<UTC-batch-id>.md`
  snapshots. Snapshot writes use exclusive creation, a hash-chained
  `history/MANIFEST.jsonl`, decision-row verification, and atomic latest-file
  replacement. Templates are versioned and migrations preserve populated
  content. Root `REPORT.md` is the cross-symbol current summary.
- Standard symbol horizons are 1 trading day, 2 weeks, 1 month, and 2 months.
  Each uses an explicit unlevered flat band and either up/flat/down
  probabilities totaling 100% or `insufficient evidence`. Reports use USD and
  separate unlevered loss from approximate 5x gross exposure before costs,
  margin calls, gaps, and liquidation.
- Behavioral analysis is restricted to observable, participant- and
  horizon-specific evidence with alternatives and falsifiers. Its 11-paper
  research basis, including institutional-herding counterevidence, is tracked
  under `research/market-behavior/` as of 2026-07-31.
- Commodity/futures work requires exact contract or broker-product identity,
  physical balance, curve/basis/roll, settlement/delivery, positioning lag, and
  margin/liquidation analysis. Generic commodity and index aliases do not imply
  a particular future, cash index, fund, or CFD.
- Real client identity, financial facts, positions, accounts, tax data, and
  communications are prohibited from repository files, Git history, symbol or
  forecast memory, evaluations, and logs. Personalized workflows require an
  approved secure client system, minimization, redacted references, lifecycle
  controls, current jurisdictional review, and synthetic repository tests. The
  repository scanner covers research and operational artifacts plus common
  contact, payment, account, government-ID, sensitive-key, and private-key
  patterns, with positive and false-positive self-tests; it remains a backstop,
  not authorization to store client data.

## Operational Baseline And Limits

- The first complete immutable operational batch is
  `2026-08-01T004949Z`: all 38 active symbols were preserved, 31 SEC-listed
  identities were resolved, and 7 generic commodity/index aliases remained
  unresolved. With no authorized live quote/news adapter and incomplete
  filing, valuation, and risk evidence, every horizon correctly records
  `insufficient evidence`; no probabilities or risk numbers were invented.
- The repository has no licensed live price/news feed or broker product
  catalogue. Exact instrument resolution and current decision-grade analysis
  therefore remain unavailable for some instruments until an authorized source
  is connected.
- No genuine registered forecasts have matured into verified outcomes, so live
  calibration is unmeasured. Evaluation also lacks a secret holdout, an actual
  model candidate run, and blinded human review; the current replay proves the
  harness mechanics only.

## Development Workflow

- Full-workflow changes plan in `TODO.md`; completed work resets it before the
  final gate. Durable facts belong here only after they are established.
- Every file-changing task uses one matching `fix/*` or `feature/*` branch.
  Stage commits run `scripts/agent-quality-gate.sh --stage`; final work-branch,
  prepared-merge, and clean merged `dev` states run the full gate.
- Passing work is tested as a prepared non-fast-forward merge, merged locally
  into `dev`, and checked again. Publishing to `main` or a remote requires the
  user's explicit instruction.
- `scripts/check-financial-agent.sh` is the repository integrity check for skill
  inventory, metadata, stale policy, research manifests, active-symbol memory,
  report coverage, probability arithmetic, adapter/evaluation/calibration
  regressions, immutable history/migrations, and client-data leak safeguards.
