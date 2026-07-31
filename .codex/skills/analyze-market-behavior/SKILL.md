---
name: analyze-market-behavior
description: Assess evidence-based trader attention, sentiment, reference points, extrapolation, underreaction, overreaction, overconfidence, disposition, and herding without inferring psychology from price alone. Use when news, price, volume, volatility, flows, positioning, surveys, or market narratives may affect a financial catalyst, symbol forecast, or investment thesis.
---

# Analyze Market Behavior

## Boundary

Analyze observable market behavior and conditional mechanisms, not private
mental states. A plausible behavioral story is neither a calibrated forecast
nor proof of mispricing. Keep verified fundamentals, macro effects, market
structure, positioning, and mechanical flows visible as alternatives.

Read [the behavioral evidence guide](references/behavioral-evidence.md) before
using a mechanism in a decision-ready analysis.

## Procedure

1. Fix the instrument, venue, participant group, market session, decision-time
   cutoff, and forecast horizon. Do not treat retail, institutional, systematic,
   hedging, market-making, or commodity participants as one crowd.
2. Use `verify-financial-evidence` for current price, volume, volatility, news,
   flows, positioning, options, survey, or search inputs. Preserve source and
   timestamps.
3. Use `analyze-news-catalysts` to separate verified surprise and fundamental
   transmission from language, reach, attention, and observed market response.
4. State the candidate mechanism and reference its empirical or theoretical
   base. Identify whether the implication concerns attention, order flow,
   temporary pressure, information diffusion, or durable value.
5. Compare the observed path with the mechanism: abnormal return and volume,
   gap and reversal, volatility or skew, coverage, ownership, short interest,
   fund flows, positioning, surveys, and relevant reference levels.
6. Test nonbehavioral and counter-behavioral explanations. Counterevidence is
   mandatory when a broad herding, panic, FOMO, or capitulation claim is made.
7. Specify an expected path and horizon, alternative scenarios, falsifiers,
   confidence, and missing observations.
8. Change a directional probability only when current observations and a
   relevant calibration support the size of the change. Otherwise keep the
   mechanism as a monitored scenario or abstain.

## Rules

- Price rising is not evidence of greed; price falling is not evidence of fear.
- News tone is not economic surprise, attention is not direction, and volume is
  not investor identity.
- Do not claim that traders `will` or `usually` react a certain way without a
  matching population, setting, frequency, and base rate.
- Do not assume institutional herding. Historical evidence is mixed and depends
  on stock size and observation frequency.
- Do not use this skill to justify autonomous orders or a personalized
  recommendation.
- Mark `insufficient evidence` when identity, timing, observations, calibration,
  or alternatives cannot be resolved.

## Output

Provide observed facts, participant and horizon, candidate mechanism, evidence
for and against, fundamental and mechanical alternatives, expected path,
falsifiers, confidence, probability impact or abstention, and monitoring data.
