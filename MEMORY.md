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
  gating, and financial-agent evaluation.
- The research basis is tracked under `research/financial-analyst-agent/`: 41
  fully reviewed papers (10 trading, 10 company analysis, 10 economics, and 11
  news) plus current professional and regulatory primary sources as of
  2026-07-31. Local full-text downloads remain ignored.
- Rules and duties vary by jurisdiction, capacity, client, product, and facts.
  Live work retrieves current primary rules and escalates legal or compliance
  conclusions to qualified reviewers.

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
  inventory, metadata, stale policy, and research-lane counts.
