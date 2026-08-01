# Executable Financial-Agent Evaluations

`cases.jsonl` contains public, synthetic adverse cases. The runner evaluates a
frozen JSONL response set or invokes an external candidate command once per case
and repeat over JSON stdin/stdout. Candidate stdin contains only `id`, `lane`,
`prompt`, `decision_cutoff`, and optional public `context`; assertions, expected
values, weights, labels, and criticality never cross the candidate boundary.

The result records public and holdout hashes separately, the frozen rubric and
scorer hashes, candidate-command or response hashes, per-assertion results,
dimensions, repeat score range, tool/model versions, baseline delta when
provided, critical failures, and an accept/reject decision.

```bash
python3 scripts/run-financial-evals.py \
  --cases evaluations/financial-agent/cases.jsonl \
  --responses evaluations/financial-agent/fixtures/passing-responses.jsonl \
  --output-dir artifacts/evaluations/example \
  --run-id example --model-version supplied-output --tool-version repo
```

An external candidate must return `{"id":"<case-id>","text":"...","values":{}}`.
Pass the executable and arguments after `--candidate-command`. Keep final
holdouts outside normal instructions and repository history; provide them with
`--holdout-cases` only for a controlled comparison. Never put client facts,
credentials, proprietary prompts, or licensed data in public fixtures or run
logs.

Use `--repeat-count` for stochastic external candidates. Use
`--baseline-responses` for a frozen baseline covering exactly the same public
and controlled-holdout cases. Because `--candidate-command` consumes the
remaining command line, place runner options before it.

Any failed critical assertion rejects the candidate, regardless of its average
score. Deterministic assertions test explicit contracts; qualified blinded
review remains necessary for nuanced correctness and investment usefulness.
The committed passing responses and replay candidate are harness tests only;
they are never evidence of model performance or forecast skill.

## Latest Harness Verification

At `2026-08-01T00:53:46Z`, the fixture replay was run three times against all
21 public cases with the passing fixture as the frozen baseline. It scored
1.000 in every repeat, delta 0.000 versus baseline, and all 153 repeated
critical assertions passed. The untracked result JSON SHA-256 was
`2e9704766a9031d3cef3f4b6e45f085c8ea335c668a942ca33ece71ef6e5bef4`;
public-case, rubric, scorer, and candidate-command hashes are recorded by the
runner. This verifies determinism, anti-leakage transport, scoring, repeats,
baseline comparison, and the critical gate only. No real candidate, controlled
hidden set, financial outcome, or blinded human review was available, so it
supports no model-quality or investment-skill claim.
