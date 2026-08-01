# Financial Analyst Agent

An evidence-led financial analyst and broker-support agent for company research,
valuation, probabilistic forecasting, macro and news analysis, portfolio risk,
execution planning, and suitability support.

The agent optimizes for decision usefulness and auditability—not persuasion. It
does not provide professional licensure, guarantee returns, hold account access,
or place orders. When exact identity, current evidence, client facts, or product
terms are insufficient, it abstains explicitly.

## Requirements

- Codex or another compatible agent environment that loads [`AGENTS.md`](AGENTS.md)
  and the skills under [`.codex/skills/`](.codex/skills/).
- Internet access for current or time-sensitive research.
- An authorized data source for decision-grade live prices or licensed news.
- An approved secure client system before using any real client information.

This repository is an instruction, workflow, and evidence layer. There is no
application server to start and no built-in brokerage connection.

## Five-Minute Start

Open the repository in the agent environment and enter:

```text
do symbols research
```

The agent will read [`SYMBOLS.md`](SYMBOLS.md), cover every active instrument,
verify identities and available evidence, preserve explicit abstentions, update
[`REPORT.md`](REPORT.md) and per-symbol memory, then run repository checks.

That prompt takes seconds to enter, but a complete current research batch can
take substantially longer and changes repository files. Read the
[worked walkthrough](docs/QUICKSTART.md) before the first run.

For a chat-only first task, try:

```text
Analyze AAPL fundamentals as of now for an impersonal three-year research
horizon. Use current primary sources, do not edit repository files, and abstain
if evidence is insufficient.
```

## Choose a Task

| Goal | Prompt recipe | Normal result |
| --- | --- | --- |
| Research the full watchlist | `do symbols research` | Versioned repository batch |
| Analyze one company | [Research one company](docs/PROMPTS.md#research-one-company) | Fundamental memo |
| Estimate company value | [Value a company](docs/PROMPTS.md#value-a-company) | Scenarios and valuation range |
| Form a complete view | [Investment thesis](docs/PROMPTS.md#build-a-complete-investment-thesis) | Decision packet |
| Assess news or earnings | [News catalyst](docs/PROMPTS.md#analyze-current-news-or-an-earnings-release) | Event chronology and materiality |
| Assess an economy | [Macroeconomy](docs/PROMPTS.md#analyze-the-macroeconomy) | Regime scenarios |
| Analyze a future/commodity | [Commodity contract](docs/PROMPTS.md#analyze-a-commodity-or-futures-contract) | Product-specific analysis |
| Review a portfolio | [Synthetic portfolio](docs/PROMPTS.md#review-a-portfolio-using-synthetic-data) | Risk and stress report |
| Screen suitability | [Suitability gate](docs/PROMPTS.md#review-suitability-without-inventing-client-facts) | Checklist, not approval |
| Plan implementation | [Execution plan](docs/PROMPTS.md#plan-trade-execution-without-placing-an-order) | Advisory plan, no orders |
| Verify a historical claim | [Point-in-time verification](docs/PROMPTS.md#verify-a-financial-claim-at-a-historical-cutoff) | Evidence ledger |
| Request probabilities | [Directional forecast](docs/PROMPTS.md#request-directional-probabilities) | Registered forecast or abstention |
| Test an agent change | [Evaluate the agent](docs/PROMPTS.md#evaluate-the-agent) | Regression decision |

See the complete [prompt cookbook](docs/PROMPTS.md) for reusable templates and
prompt-quality modifiers.

## What a Strong Request Includes

Specify the exact entity or instrument, exchange or product, decision question,
market, currency, as-of time, evidence cutoff, horizon, professional capacity,
constraints, and desired output. For example:

```text
Analyze [exact instrument] for [decision purpose] as of [cutoff], in [currency],
over [horizon]. Use current primary sources. Separate facts, calculations,
estimates, scenarios, and opinions. Show downside, costs, alternatives,
disconfirmers, invalidation, and missing evidence. [Chat only / preserve a
versioned repository result].
```

Do not ask for certainty, guaranteed returns, manipulation, autonomous orders,
or conclusions based on missing client facts.

## Parallel Work

For large tasks with independent lanes, the lead agent may use the minimum
number of subagents needed. All lanes receive the same identity, decision
cutoff, units, and evidence rules. Work is read-only by default; any edits use
one writer per path. Subagents receive no extra data access or order authority,
and the lead agent verifies every material source, calculation, diff, and final
conclusion.

Add this optional sentence to a large prompt:

```text
Use bounded parallel subagents for genuinely independent lanes where useful.
Keep dependent work, shared-file edits, Git integration, safety decisions, and
final synthesis with the lead agent.
```

## Expected Response

A substantial result should normally include:

1. exact scope, identity, market, currency, capacity, horizon, and as-of time;
2. a concise conclusion and confidence level;
3. primary evidence near each material claim;
4. reconciled calculations and clearly labeled estimates;
5. base, bull, and bear scenarios when uncertainty is material;
6. downside, liquidity, costs, conflicts, alternatives, and execution issues;
7. disconfirmers, invalidation, monitoring triggers, and unresolved questions.

`Insufficient evidence` is a valid result. It means the agent cannot support a
decision without increasing the risk of a false or unsafe claim.

## Repository Outputs

- [`SYMBOLS.md`](SYMBOLS.md): maintained watchlist and status summary.
- [`REPORT.md`](REPORT.md): latest complete watchlist batch.
- [`research/symbols/`](research/symbols/): current views, append-only decisions,
  and immutable point-in-time histories.
- [`forecasts/`](forecasts/): evidence-linked forecast and outcome ledgers.
- [`evaluations/`](evaluations/): regression cases, fixtures, and evaluation
  documentation.
- [`MEMORY.md`](MEMORY.md): durable architecture facts and operational limits;
  never client information.

## Help And Operations

- [Five-minute walkthrough](docs/QUICKSTART.md)
- [Prompt cookbook](docs/PROMPTS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Provider process contract](.codex/skills/acquire-point-in-time-financial-data/references/provider-contract.md)
- [Executable evaluation guide](evaluations/financial-agent/README.md)

## Maintainer Check

After a clean documentation, policy, skill, or code change, run:

```bash
scripts/agent-quality-gate.sh
```

Repository edits follow the feature/fix branch, verified commit, prepared merge,
and clean local `dev` workflow in [`AGENTS.md`](AGENTS.md). Publishing is always
a separate explicit action.
