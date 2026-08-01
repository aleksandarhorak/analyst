# Real Model Evaluation And Forecast Outcomes

This runbook separates three different claims:

1. **Harness correctness:** deterministic fixtures prove transport, scoring,
   hashing, and safety gates work.
2. **Model quality:** a real frozen candidate must beat an appropriate baseline
   on public and controlled hidden cases and pass blinded human review.
3. **Forecast skill:** preregistered forecasts must mature and be resolved from
   independent market evidence before calibration can be measured.

Passing one layer does not establish the next.

## Current Status

The repository contains public synthetic cases and passing fixtures. It does
not contain a licensed live-data feed, secret holdout, real candidate result,
independent reviewer result, or matured genuine forecast outcome. Do not claim
that those resources exist until a controlled run verifies them.

## 1. Freeze the Evaluation

Before running either baseline or candidate, record:

- the exact change and expected behavior;
- model and tool versions;
- public-case commit and hash;
- holdout custodian, version, and secure path;
- fixed baseline responses or baseline model version;
- repeat count, timeout, minimum score, and critical gate;
- reviewer qualifications, blinding, independence, and adjudicator;
- acceptance criteria and prohibited regressions.

Never tune repeatedly against the final holdout. Confirmed failures may enter a
future public regression set only after the evaluation decision is frozen and
without copying protected or licensed content.

## 2. Prepare a Candidate Command

The candidate is an external executable. It receives one JSON object on stdin:

```json
{
  "id": "case-id",
  "lane": "company",
  "prompt": "decision prompt",
  "decision_cutoff": "2025-08-01T12:00:00Z",
  "context": {}
}
```

`context` is omitted when unused. The command returns exactly one response on
stdout:

```json
{"id":"case-id","text":"candidate answer","values":{}}
```

The candidate never receives assertions, expected values, weights, labels, or
criticality. Keep credentials, client facts, licensed data, proprietary system
prompts, and holdout answer keys out of its command line and output.

Use a fixed model snapshot and deterministic tool configuration where possible.
For multi-agent behavior, preserve a separately protected orchestration trace
showing assignments, cutoffs, tool calls, and synthesis; the public result
runner scores final behavior but does not prove that subagents were actually
used safely.

## 3. Run Public and Controlled Holdout Cases

Keep holdouts, baseline responses, candidate artifacts, and run output in an
approved non-Git directory. Place all runner options before
`--candidate-command`, because the remaining arguments belong to the candidate:

```bash
python3 scripts/run-financial-evals.py \
  --cases evaluations/financial-agent/cases.jsonl \
  --holdout-cases /approved/controlled/holdout-cases.jsonl \
  --baseline-responses /approved/controlled/baseline-responses.jsonl \
  --output-dir /approved/non-git/evaluations/candidate-v1-run1 \
  --run-id candidate-v1-run1 \
  --model-version exact-model-snapshot \
  --tool-version exact-tool-version \
  --minimum-score 0.90 \
  --repeat-count 5 \
  --timeout 120 \
  --candidate-command /absolute/path/financial-agent-candidate
```

The output directory must not already exist. The runner writes:

- `results.json`: hashes, dimensions, per-case assertions, repeats, variance,
  baseline comparison, critical failures, and deterministic decision;
- `summary.md`: concise score and case table;
- `review-bundle.jsonl`: the prompts and actual candidate responses for human
  review, with no assertions or expected answers.

The review bundle contains controlled holdout prompts and candidate responses.
Protect it at the same level as the holdout and delete or retain it under the
approved evaluation policy. Its SHA-256 is stored in `results.json`.

Any critical assertion failure rejects the candidate regardless of average
score. Review every case, repeat range, dimension, baseline delta, and critical
result; do not accept from the headline score alone.

## 4. Conduct Blinded Human Review

Use at least two qualified reviewers who are independent of the candidate
change and each other. Give them the controlled review bundle, evaluation
purpose, rubric, and source access—but not baseline/candidate labels, expected
answers, automated assertion results, or each other's judgments.

Initialize hash-bound worksheets outside Git:

```bash
python3 scripts/check-human-review.py init \
  --results /approved/non-git/evaluations/candidate-v1-run1/results.json \
  --review-bundle /approved/non-git/evaluations/candidate-v1-run1/review-bundle.jsonl \
  --reviewer-id blind-r1 \
  --output /approved/controlled/reviews/blind-r1.jsonl

python3 scripts/check-human-review.py init \
  --results /approved/non-git/evaluations/candidate-v1-run1/results.json \
  --review-bundle /approved/non-git/evaluations/candidate-v1-run1/review-bundle.jsonl \
  --reviewer-id blind-r2 \
  --output /approved/controlled/reviews/blind-r2.jsonl
```

Each reviewer replaces `pending` with `pass` or `fail`, scores at least three
applicable dimensions from 1 to 5, marks any critical failure, and gives a
specific reason of at least 20 characters. `null` is allowed only for a genuinely
inapplicable dimension. Reviewer IDs are pseudonyms, not names or emails.

Validate completed reviews:

```bash
python3 scripts/check-human-review.py check \
  --results /approved/non-git/evaluations/candidate-v1-run1/results.json \
  --review-bundle /approved/non-git/evaluations/candidate-v1-run1/review-bundle.jsonl \
  --reviews /approved/controlled/reviews/blind-r1.jsonl \
  --reviews /approved/controlled/reviews/blind-r2.jsonl
```

The validator rejects missing coverage, fewer than two reviewers, unblinded or
non-independent records, weak score/reason fields, duplicate reviews, hash
mismatches, and unresolved disagreement. If reviewers conflict or only one
reports a critical failure, a third independent adjudicator must produce a
bound `human-adjudication-v1` JSONL record and it must be supplied with
`--adjudications`.

The candidate is accepted only when deterministic checks accept and every human
case passes unanimously or through valid independent adjudication. A unanimous
human failure remains a rejection.

## 5. Register Genuine Forecasts

Do not manufacture a probability distribution merely to populate the ledger.
When an analysis has a verified start value, explicit flat band, defensible
calibration basis, exact target, and validated evidence packets, prepare a
`forecast-record-v1` JSON file and register it before the outcome:

```bash
python3 .codex/skills/calibrate-financial-forecasts/scripts/forecast_ledger.py \
  register \
  --forecasts forecasts/forecasts.jsonl \
  --outcomes forecasts/outcomes.jsonl \
  --record /approved/forecast-inputs/forecast-record.json \
  --evidence-packet /approved/evidence/start-price.json \
  --evidence-packet /approved/evidence/supporting-evidence.json
```

The writer validates packet content hashes, identity, cutoff, creation time,
probability arithmetic, flat band, and duplicate IDs. A packet ID without the
actual validated packet is insufficient.

After the target time—not before—acquire an independent total-return or
contract-consistent outcome packet. Document splits, distributions, rolls,
settlement, holidays, FX, and missing-market-day treatment, then resolve:

```bash
python3 .codex/skills/calibrate-financial-forecasts/scripts/forecast_ledger.py \
  resolve \
  --forecasts forecasts/forecasts.jsonl \
  --outcomes forecasts/outcomes.jsonl \
  --record /approved/forecast-inputs/outcome-record.json \
  --outcome-packet /approved/evidence/verified-outcome.json
```

Never backdate, edit, delete, or re-register a forecast after learning the
outcome. Abstentions belong in coverage tracking, not as invented probabilities.

Verify and score only after outcomes mature:

```bash
python3 .codex/skills/calibrate-financial-forecasts/scripts/forecast_ledger.py \
  verify --forecasts forecasts/forecasts.jsonl --outcomes forecasts/outcomes.jsonl

python3 .codex/skills/calibrate-financial-forecasts/scripts/forecast_ledger.py \
  score --forecasts forecasts/forecasts.jsonl --outcomes forecasts/outcomes.jsonl
```

Report sample size, unresolved forecasts, coverage, Brier loss, log loss,
accuracy, fixed-baseline deltas, reliability-bin counts, sparse-sample warnings,
worst cases, and eligible horizon/asset/regime/method groups. Sparse or empty
samples prohibit forecast-skill claims.

## Acceptance Record

Preserve, under the approved boundary:

- public and holdout hashes, candidate/baseline versions, and run command hash;
- `results.json`, `summary.md`, and review-bundle hash;
- blinded reviews, adjudications, reviewer qualifications, and agreement;
- all critical failures, regressions, and the accept/reject decision;
- registered forecasts, independently verified outcomes, calibration metrics,
  and method-version decisions when those outcomes eventually exist.

Repository fixtures remain regression evidence only. Never rewrite this status
based on an untracked anecdotal test or a favorable market outcome.
