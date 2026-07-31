# Decision: Financial Analyst And Broker-Support Agent Architecture

## Problem

Replace a language-specific C++ development agent with a best-practice financial
analyst and broker-support agent while retaining the research, planning, testing,
and Git mechanisms needed to improve the agent safely.

## Constraints

- Financial information is time-sensitive, probabilistic, and often revised.
- Research and recommendations can create material loss and regulatory risk.
- Historical statistical significance does not imply current, net, executable
  alpha.
- Broker duties depend on jurisdiction, role, client, product, and transaction.
- Skills must remain concise, independently triggerable, and nonduplicative.
- The repository must keep a deterministic development and review workflow.

## Decision Criteria

1. Evidence quality and auditability.
2. Numerical and temporal correctness.
3. Client protection, market integrity, and regulatory humility.
4. Clear ownership of each analytical capability.
5. Decision usefulness after costs, liquidity, risk, and uncertainty.
6. Testability and maintainability of future agent changes.

## Options Considered

### Keep The C++ Template And Add Finance Prompts

Rejected. Language/toolchain rules consume context, create conflicting defaults,
and do not supply financial controls.

### Put All Finance Guidance In AGENTS.md

Rejected. A monolithic prompt would be difficult to trigger selectively, test,
or update and would duplicate detailed procedures.

### Depend Primarily On External Finance Plugins

Rejected as the core architecture. Connectors may improve data access, but the
agent's research standards, analysis process, suitability controls, and audit
trail must remain repository-owned and reviewable.

### Compact Core Policy Plus Modular Finance Skills

Selected. `AGENTS.md` owns non-negotiable conduct and workflow. Bounded skills
own repeatable analyses. An orchestration skill combines them for an investment
thesis. A financial-agent evaluation skill and Git quality gate support ongoing
improvement.

## Evidence Summary

- Market-microstructure research shows that spread, adverse selection, depth,
  resilience, market impact, latency, and transaction costs determine whether a
  trade is executable; stylized models are diagnostic benchmarks, not oracles.
- Retail-account evidence shows high turnover can destroy gross security-selection
  results after costs. Backtest research shows one holdout and a high in-sample
  Sharpe do not control broad strategy search.
- Company research supports structured analysis of statements, profitability,
  earnings quality, capital allocation, industry economics, distress, governance,
  and forecast conflicts, but repeatedly warns against using historical scores as
  automatic alpha.
- Macroeconomic research supports real-time vintages, simple benchmarks,
  horizon-specific out-of-sample testing, causal-identification grades, regime
  warnings, and distribution forecasts rather than deterministic calls.
- News research shows that event identity, subject, timing, and source matter more
  than generic tone. Domain language models improve classification but can fail
  on arithmetic, context, and neutral-versus-positive distinctions; false or
  low-credibility content can spread rapidly through human and bot amplification.
- Professional standards require diligence, reasonable basis, independence,
  fact/opinion separation, fair performance reporting, client profiling, costs,
  alternatives, conflicts, suitability, and best execution.

## Recommended Choice

Retain and adapt:

- `technical-research`
- `implementation-planning`
- `git-tested-delivery`

Remove:

- all nine `cpp-*` and `tbb-concurrency` skills
- C++ dependency-hygiene policy and checks
- C++/CMake/TBB-specific ignore and verification rules

Add:

1. `verify-financial-evidence`
2. `analyze-company-fundamentals`
3. `value-company-and-forecast`
4. `analyze-macroeconomy`
5. `analyze-news-catalysts`
6. `plan-trade-execution`
7. `manage-portfolio-risk`
8. `build-investment-thesis`
9. `check-broker-suitability`
10. `evaluate-financial-agent`

## Why This Choice

The capability boundaries mirror the evidence: source integrity precedes
analysis; company quality and valuation are related but distinct; macro and news
have different time and causal structures; portfolio selection and execution are
separate decisions; personalized recommendations require a client and compliance
gate; and agent improvement requires its own regression discipline.

## Operating Model

Every decision-ready output should carry:

- instrument, jurisdiction/capacity, currency, horizon, and as-of timestamp;
- primary sources and a point-in-time evidence ledger;
- reported facts, derived values, estimates, scenarios, and opinions kept
  distinct;
- base, bull, and bear cases with probabilities or explicit confidence;
- valuation range, catalysts, disconfirming evidence, and invalidation criteria;
- portfolio, liquidity, execution, fee, tax, and downside implications;
- suitability/conflict review when a person or account is involved;
- unresolved gaps and a clear abstention when evidence is insufficient.

## Rejected Alternatives

- A single finance-generalist skill: too broad to trigger and test reliably.
- Separate skills for every ratio, asset, order type, or jurisdiction: excessive
  fragmentation and duplicated controls.
- Automatic order placement: outside the requested repository and unsafe without
  verified authority, account controls, current rules, and production testing.
- Hard-coded rating formulas: false precision and regime fragility.

## Risks And Unknowns

- No instruction set can make uncertain markets predictable or ensure profit.
- Data connectors may introduce stale, revised, licensed, or survivorship-biased
  inputs; live tool work must validate provenance and timestamps.
- Legal classification and duties require current jurisdiction-specific review.
- The paper base is primarily U.S.-centric and several studies are historical.
- Skill quality must be evaluated on realistic cases and adverse examples over
  time; a documentation-only migration is a foundation, not proof of excellence.

## Implementation Implications

- Replace root policy and skills rather than layer finance onto C++ guidance.
- Keep detailed paper notes in research, not in always-loaded instructions.
- Add templates to each finance skill for repeatable, auditable outputs.
- Replace dependency hygiene with checks for required skill inventory, stale C++
  policy, paper counts, metadata, and active task state.
- Preserve branch, stage-commit, CI, and automatic tested merge behavior.

## Verification Plan

- Validate each skill's frontmatter and UI metadata.
- Check that exactly the retained and selected skills exist and no C++ skill or
  routing text remains.
- Check at least ten manifest entries per research lane.
- Run shell syntax and branch-policy tests.
- Run the stage and final repository quality gates.
- Review the finance guardrails for claims of licensure, guaranteed returns,
  autonomous execution, MNPI use, manipulation, and unsupported certainty.

## Source Index

See [sources.md](sources.md) and [papers/manifest.md](papers/manifest.md).

## Open Questions

- Which jurisdictions, asset classes, data vendors, and client types will be
  primary in deployment?
- Will future connectors provide licensed point-in-time fundamentals, consensus
  vintages, order books, portfolios, or execution reports?
- What benchmark case set and human review panel should govern future agent
  evaluation?
