# Decision: Evidence-Bounded Market-Behavior Analysis

## Problem

Symbol research needs to assess how market participants may react to verified
news and price changes without inventing a crowd narrative or confusing an
attention shock with a durable change in value.

## Constraints

- Psychological state is normally latent; price, volume, volatility, options,
  flows, positioning, and communications are observable only imperfectly.
- The reviewed evidence spans different eras, samples, market structures,
  participant groups, frequencies, and methods.
- One event can simultaneously change fundamentals, discount rates, liquidity,
  attention, positioning, and beliefs.
- A plausible mechanism does not supply a calibrated probability or executable
  edge by itself.
- Leverage magnifies path, funding, margin-call, and liquidation risk; it does
  not increase forecast quality.

## Options Considered

### Add A Sentiment Score To Every Symbol

Rejected. A scalar score hides source quality, participant differences, time
horizon, negation and context, fundamental information, and contradictory
signals.

### Describe Fear, Greed, FOMO, Or Panic From Price Action

Rejected. This is circular when the same price move is both evidence and
conclusion, and it encourages unsupported mind-reading.

### Ignore Market Behavior Entirely

Rejected. Research supports conditional attention, reference-point,
extrapolation, sentiment, underreaction, and overtrading mechanisms that can
improve scenario design when measured carefully.

### Evidence-Bounded Behavioral Scenarios

Selected. The agent identifies a mechanism only when observable inputs and a
relevant empirical or theoretical base support it. It states the affected
participant group, horizon, alternative explanations, confidence, falsifiers,
and whether the implication concerns attention, flow, price pressure, or value.

## Evidence Synthesis

- Reference dependence and loss aversion explain why gains and losses relative
  to a reference point may be treated asymmetrically, but stylized choice
  experiments do not directly forecast a security return.
- Retail-account studies support attention-driven buying, reluctance to realize
  losses, and performance damage from excessive trading in their historical
  samples. These results do not describe every investor or current venue.
- Slow information diffusion can create underreaction while feedback trading
  can later create overreaction in a stylized model. The predicted path depends
  on information coverage and participation.
- Sentiment effects are historically strongest in difficult-to-value,
  difficult-to-arbitrage securities. A sentiment proxy is neither a mental-state
  measurement nor a stand-alone trading signal.
- Survey expectations often extrapolate past market returns, while media
  pessimism has been associated with temporary price pressure and volume in a
  historical sample. Both results are aggregate and context dependent.
- Pension-fund data show weak herding overall and little evidence in the largest
  stocks. The agent therefore may not assume that institutions move as one
  crowd; participant and frequency evidence are required.
- Prices can vary far more than a simple discounted-dividend benchmark implies,
  but model and discount-rate assumptions matter. Excess volatility does not
  identify a specific behavioral cause.

## Required Analysis Contract

For each claimed behavior, record:

1. verified event and market-state cutoff;
2. observable inputs and their exact source, timestamp, and units;
3. candidate participant group and why it is relevant;
4. mechanism and paper-level evidence;
5. expected path and horizon, not merely a direction;
6. fundamental, macro, liquidity, positioning, and mechanical alternatives;
7. evidence against the mechanism and conditions that would falsify it;
8. confidence and whether it changes any directional probability;
9. costs, capacity, and leverage implications when decision relevant.

Useful observations can include abnormal return and volume, volatility and skew,
gap behavior, news novelty and reach, analyst coverage, short interest, fund or
ETF flows, positioning, survey expectations, search interest, and known
reference levels. Each is a proxy requiring interpretation, not proof of a
mental state.

## Decision Rule

Use one of four outcomes:

- **supported:** mechanism, participant, horizon, and observations align;
- **plausible:** mechanism fits but decisive behavioral evidence is missing;
- **unsupported:** observations or counterevidence do not support the claim;
- **abstain:** identity, timing, evidence quality, or alternative explanations
  cannot be resolved.

Only `supported` analysis should materially change a probability estimate, and
the size of that change must be justified by calibration evidence. `Plausible`
belongs in scenarios and monitoring, not as false precision.

## Integration Decision

Add a focused `analyze-market-behavior` skill and compose it inside a separate
`research-symbol-watchlist` workflow. The batch workflow must first verify
instrument identity, prices, news, and timestamps; preserve per-symbol history;
then combine company, macro, catalyst, behavior, portfolio-risk, and execution
evidence. Behavioral analysis never overrides stronger verified evidence or an
insufficient-evidence result.

## Risks And Unknowns

- Current, licensed positioning and flow data may be unavailable.
- Behavioral relationships can decay or reverse as market structure changes.
- Public-news coverage and social data can be manipulated or bot-amplified.
- The paper set is heavily U.S. equity focused; commodities and indices require
  different participant and transmission analysis.
- A future benchmark set is needed to calibrate whether behavioral analysis
  improves forecasts rather than only explanations.

## Verification Implications

- Reject narrative-only psychology without an observation and source.
- Reject universal-herding or universal-retail claims.
- Require alternative explanations, a falsifier, and an explicit horizon.
- Require up/flat/down probabilities to sum to 100% and keep `insufficient
  evidence` available.
- Show unlevered and 5x linear-loss scenarios separately and disclose financing,
  margin-call, gap, and liquidation effects.
