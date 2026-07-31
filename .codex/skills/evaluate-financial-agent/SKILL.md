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
5. Score evidence provenance, factual and numerical accuracy, temporal
   integrity, uncertainty calibration, risk/cost coverage, compliance behavior,
   actionability, citation quality, and reproducibility separately.
6. Use deterministic checks for exact facts and calculations; use blinded human
   review for judgment. Require reasons and adjudicate disagreements.
7. Compare baseline and candidate per case, not only by average. Treat any
   critical safety regression as blocking.
8. Record model/tool versions, prompts, runs, failures, variance, and decision.
9. Add every confirmed failure to the regression corpus without leaking the
   expected answer into normal instructions.

Use [the evaluation-plan template](references/evaluation-plan.md).

## Rules

- Do not tune repeatedly against the final holdout.
- Do not let style scores mask incorrect facts, arithmetic, or unsafe action.
- Do not claim improvement from cherry-picked examples or one stochastic run.
- Keep licensed or proprietary evaluation data within its permitted boundary.

## Output

Provide fixture inventory, rubric, baseline/candidate results, confidence or
run variability, all critical failures, regression analysis, accept/reject
decision, and the next tests needed.
