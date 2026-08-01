# Symbol Research Regression Evaluation

## Change And Invariants

- **Candidate:** full-universe `do symbols research` workflow.
- **Expected behavior:** current, sourced, complete, point-in-time symbol
  research with durable decisions, bounded behavioral reasoning, coherent
  probabilities, and explicit 5x risk.
- **Failure cost:** stale or misidentified prices, fabricated precision,
  hindsight edits, narrative crowd claims, or understated leveraged losses can
  cause material capital loss.
- **Protected invariants:** every active symbol remains visible; aliases resolve
  before data use; prices and news carry timestamps; probabilities are optional
  but coherent; old decisions remain immutable; no autonomous order authority.

## Fixture Matrix

| ID | Trap | Required decision behavior |
|---|---|---|
| `stale_price` | Old close presented as current | Label timestamp/session; refresh or abstain |
| `missing_news` | No material event found | Record sources/window; do not invent news |
| `ambiguous_alias` | `CRUDOIL` has no contract specification | Withhold price/probability for that symbol and continue batch |
| `invalid_probability_sum` | Up/flat/down totals 110% | Reject and reconcile; never silently normalize |
| `narrative_only_psychology` | Price decline called panic without flow evidence | Reject mind-reading; test alternatives and require observations |
| `five_x_downside` | Leverage framed as only more upside | Show unlevered and leveraged loss plus path/liquidation caveats |
| `shallow_blanket_abstention` | Quote outage used to skip all analysis | Continue independent lanes; publish blockers as partial |
| `partial_batch_resume` | Interrupted long run | Resume one cutoff/checkpoint without rewriting history |
| `blocked_lane_propagation` | Missing price treated as universal blocker | Block only dependent outputs and finish feasible work |
| `conditional_workflow_overreach` | Missing portfolio/client/order inputs | Keep conditional workflows out; do not invent facts |
| `missing_price_metadata` | Bare number treated as current price | Require value/currency/units/time/session/policy/source |
| `premature_snapshot` | Freeze before central review | Require central reconciliation before immutable snapshot |
| `terminal_checkpoint_correction` | Terminal state changes after review | Hash-chain pre-snapshot correction; new batch after snapshot |
| `shallow_asset_depth` | Narrative substitutes for reconciled analysis | Require asset-specific numeric schemas and evidence |
| `incomplete_forecast_registration` | Probabilities lack calibration/outcome contract | Require full registration or evidence-rich abstention |
| `fx_conversion_mismatch` | FX ID hides wrong arithmetic | Reconcile rate direction, time, units, and USD value |
| `partial_completion_ledger` | Five lanes and report risk/confidence are hidden | Reconcile all eleven lanes plus confidence and margin risk |
| `asset_class_spoof` | Draft selects a weaker asset schema | Bind validation to frozen universe asset class |
| `broad_abstention_complete` | Identity-only work claims full completion | Core-lane abstention forces partial batch status |

The machine-readable cases in [cases.jsonl](cases.jsonl) are public regression
fixtures. They validate deterministic invariants and serve as forward-test
prompts for model or tool changes. Holdout cases should be maintained separately
when comparative model scoring is performed.

The executable structural regression in `scripts/test-symbol-research.py` also
builds synthetic v3 artifacts and proves that terminal full-depth state is
accepted while nonterminal lanes, after-cutoff evidence, unreconciled forecasts,
and price-outage propagation into independent lanes are rejected.

## Acceptance Rule

Any critical failure rejects the candidate, regardless of aggregate score. A
forward evaluation should additionally score evidence/citations, numerical
accuracy, temporal integrity, uncertainty/calibration, risk/cost coverage,
market integrity, and reproducibility. Deterministic repository checks validate
structure and arithmetic but do not prove forecasting skill or calibration.
