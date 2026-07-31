# Executable Financial-Agent Evaluations

`cases.jsonl` contains public, synthetic adverse cases. The runner evaluates a
frozen JSONL response set or invokes an external candidate command once per case
over JSON stdin/stdout. It records hashes, per-assertion results, dimensions,
tool/model versions, critical failures, and an accept/reject decision.

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

Any failed critical assertion rejects the candidate, regardless of its average
score. Deterministic assertions test explicit contracts; qualified blinded
review remains necessary for nuanced correctness and investment usefulness.
