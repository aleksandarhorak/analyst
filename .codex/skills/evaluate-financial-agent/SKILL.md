---
name: evaluate-financial-agent
description: Design and run regression evaluations for financial-agent accuracy, evidence quality, temporal integrity, numerical reconciliation, uncertainty, compliance safety, and decision usefulness. Use before or after changing finance policies, skills, prompts, data tools, models, or workflows.
---

# Evaluate Financial Agent

## Purpose

Test improvements against realistic, adverse, and time-sensitive cases. A prose
change is not an improvement until it preserves safety and improves measured
performance without evaluation leakage.

## Procedure

1. Define the changed behavior, users, failure costs, acceptance threshold, and
   protected invariants.
2. Build versioned fixtures spanning company, valuation, macro, news, portfolio,
   execution, suitability, and refusal cases as relevant.
3. Include stale data, conflicting sources, revised macro vintages, unit traps,
   corporate actions, misleading sentiment, missing client facts, illiquidity,
   conflicts, non-public-information hints, manipulation, and guaranteed-return
   prompts.
4. Freeze source snapshots, decision cutoff, expected calculations, rubric, and
   scorer before comparing variants. Keep a hidden holdout when possible.
5. Execute public regressions with `scripts/run-financial-evals.py`, using either
   a frozen response JSONL or a candidate command that consumes one case on
   JSON stdin and returns `{id,text,values}` on JSON stdout. Record the generated
   `results.json` and `summary.md`. Candidate stdin contains decision inputs,
   never assertions, expected answers, weights, labels, or criticality. Never
   treat fixture replay as a model result.
6. Score evidence provenance, factual and numerical accuracy, temporal
   integrity, uncertainty calibration, risk/cost coverage, compliance behavior,
   actionability, citation quality, and reproducibility separately.
7. Use deterministic checks for exact facts and calculations; use blinded human
   review for judgment. Require reasons and adjudicate disagreements.
8. Compare baseline and candidate per case, not only by average. Treat any
   critical safety regression as blocking.
9. Record model/tool versions, case and response hashes, runs, failures,
   variance, and decision. Keep client facts, secrets, licensed payloads, and
   final holdouts outside public fixtures and logs.
10. Add every confirmed failure to the regression corpus without leaking the
   expected answer into normal instructions.

Use [the evaluation-plan template](references/evaluation-plan.md).

## Rules

- Do not tune repeatedly against the final holdout.
- Do not let style scores mask incorrect facts, arithmetic, or unsafe action.
- Do not claim improvement from cherry-picked examples or one stochastic run.
- Do not claim forecast skill from deterministic contract cases. Use
  `calibrate-financial-forecasts` for registered real outcomes and probability
  calibration.
- Keep licensed or proprietary evaluation data within its permitted boundary.

## Output

Provide fixture inventory, rubric, baseline/candidate results, confidence or
run variability, all critical failures, regression analysis, accept/reject
decision, and the next tests needed.
