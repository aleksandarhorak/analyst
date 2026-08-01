#!/usr/bin/env python3
"""Parse and validate versioned full-depth symbol-research control blocks."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import re
from typing import Any


LATEST_V3_MARKER = "<!-- analyst-template: latest-v3 -->"
STATE_SCHEMA = "symbol-research-state-v1"
REQUIRED_HORIZONS = ("1 trading day", "2 weeks", "1 month", "2 months")
REQUIRED_LANES = (
    "identity_evidence",
    "price_market",
    "fundamentals_product",
    "valuation_scenarios",
    "news_catalysts",
    "macro_transmission",
    "market_behavior",
    "investment_thesis",
    "directional_forecast",
    "downside_leverage",
    "monitoring",
)
LANE_LABELS = {
    "identity_evidence": "Identity and point-in-time evidence",
    "price_market": "Price and market data",
    "fundamentals_product": "Fundamentals or product analysis",
    "valuation_scenarios": "Valuation and scenarios",
    "news_catalysts": "News and catalysts",
    "macro_transmission": "Macro transmission",
    "market_behavior": "Market behavior",
    "investment_thesis": "Investment thesis",
    "directional_forecast": "Directional forecast",
    "downside_leverage": "Downside and 5x risk",
    "monitoring": "Monitoring",
}
TERMINAL_LANE_STATUSES = {"complete", "abstained", "blocked", "not_applicable"}
DISPLAY_STATUSES = {
    "complete": "Complete",
    "abstained": "Abstained",
    "blocked": "Blocked",
    "not_applicable": "Not applicable",
    "not_started": "Not started",
    "in_progress": "In progress",
}
REASON_CODES = {
    "unresolved_identity",
    "unavailable_current_price",
    "missing_primary_evidence",
    "contradictory_primary_evidence",
    "no_defensible_calibration",
    "no_observable_behavior_evidence",
    "unavailable_contract_terms",
    "provider_failure",
    "not_applicable_to_asset",
    "other_documented",
}
SOURCE_TYPES = {
    "primary",
    "official_market",
    "authorized_provider",
    "original_research",
    "secondary",
}
PRICE_POLICIES = {"live", "delayed", "official_close", "prior_close", "indicative"}
MARKET_SESSIONS = {"open", "closed", "pre_market", "after_hours", "auction", "unknown"}
REQUIRED_HEADINGS = (
    "Instrument And Batch",
    "Machine-Readable Research State",
    "Research Depth Ledger",
    "Price And Evidence",
    "Fundamentals Or Product Analysis",
    "Valuation And Scenarios",
    "News And Catalysts",
    "Macro Transmission",
    "Market Behavior",
    "Investment Thesis",
    "Directional Probabilities",
    "Downside And 5x Exposure",
    "Monitoring",
    "Decision",
    "Data Lineage",
)
BATCH_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{6}Z$")
EVIDENCE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._/-]{2,127}$")


class ContractError(RuntimeError):
    """The structured research artifact violates its versioned contract."""


def parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{field} must be an ISO 8601 date-time")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError(f"{field} must be an ISO 8601 date-time") from error
    if parsed.tzinfo is None:
        raise ContractError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def markdown_section(text: str, heading: str) -> str:
    marker = f"## {heading}\n"
    if marker not in text:
        return ""
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def json_block(text: str, heading: str) -> dict[str, Any]:
    content = markdown_section(text, heading)
    match = re.search(r"```json\n(.*?)\n```", content, flags=re.DOTALL)
    if not match:
        raise ContractError(f"{heading} must contain one fenced JSON block")
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise ContractError(f"{heading} contains invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise ContractError(f"{heading} JSON must be an object")
    return value


def _nonempty(value: Any, field: str, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ContractError(f"{field} must contain at least {minimum} characters")
    return value.strip()


def _nullable_reason(value: Any, field: str) -> None:
    if value is not None and value not in REASON_CODES:
        raise ContractError(f"{field} has unknown reason code: {value}")


def _validate_evidence(state: dict[str, Any], cutoff: datetime, terminal: bool) -> dict[str, dict[str, Any]]:
    evidence = state.get("evidence")
    if not isinstance(evidence, list):
        raise ContractError("evidence must be an array")
    indexed: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(evidence):
        field = f"evidence[{index}]"
        if not isinstance(item, dict):
            raise ContractError(f"{field} must be an object")
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not EVIDENCE_ID_PATTERN.fullmatch(evidence_id):
            raise ContractError(f"{field}.id is invalid")
        if evidence_id in indexed:
            raise ContractError(f"duplicate evidence id: {evidence_id}")
        if item.get("scope") not in {"symbol", "shared_macro"}:
            raise ContractError(f"{field}.scope must be symbol or shared_macro")
        if item.get("source_type") not in SOURCE_TYPES:
            raise ContractError(f"{field}.source_type is invalid")
        locator = _nonempty(item.get("locator"), f"{field}.locator", 8)
        if not (locator.startswith("https://") or locator.startswith("sha256:")):
            raise ContractError(f"{field}.locator must be HTTPS or a sha256 packet locator")
        accessed = parse_time(item.get("accessed_at"), f"{field}.accessed_at")
        published_value = item.get("published_at")
        published = parse_time(published_value, f"{field}.published_at") if published_value else None
        if not isinstance(item.get("cutoff_eligible"), bool):
            raise ContractError(f"{field}.cutoff_eligible must be boolean")
        if published and published > cutoff and item.get("cutoff_eligible"):
            raise ContractError(f"{field} was published after the decision cutoff")
        if published and accessed < published:
            raise ContractError(f"{field}.accessed_at precedes published_at")
        if not published and item.get("cutoff_eligible"):
            _nonempty(item.get("availability_basis"), f"{field}.availability_basis", 20)
        _nonempty(item.get("claim"), f"{field}.claim", 20)
        indexed[evidence_id] = item
    return indexed


def _validate_lanes(state: dict[str, Any], evidence: dict[str, dict[str, Any]], terminal: bool) -> None:
    lanes = state.get("lanes")
    if not isinstance(lanes, dict) or tuple(lanes) != REQUIRED_LANES:
        raise ContractError("lanes must contain every required lane in canonical order")
    summaries: list[str] = []
    for lane_name in REQUIRED_LANES:
        lane = lanes[lane_name]
        if not isinstance(lane, dict):
            raise ContractError(f"lane {lane_name} must be an object")
        status = lane.get("status")
        allowed = TERMINAL_LANE_STATUSES if terminal else TERMINAL_LANE_STATUSES | {"not_started", "in_progress"}
        if status not in allowed:
            raise ContractError(f"lane {lane_name} has invalid status: {status}")
        ids = lane.get("evidence_ids")
        if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
            raise ContractError(f"lane {lane_name}.evidence_ids must be a string array")
        if len(ids) != len(set(ids)) or any(item not in evidence for item in ids):
            raise ContractError(f"lane {lane_name} references missing or duplicate evidence")
        summary = lane.get("summary")
        reason = lane.get("reason_code")
        next_action = lane.get("next_action")
        _nullable_reason(reason, f"lane {lane_name}.reason_code")
        if status in TERMINAL_LANE_STATUSES:
            summaries.append(_nonempty(summary, f"lane {lane_name}.summary", 30))
        elif summary is not None and not isinstance(summary, str):
            raise ContractError(f"lane {lane_name}.summary must be text or null")
        if status == "complete":
            if not ids:
                raise ContractError(f"complete lane {lane_name} has no evidence")
            if any(not evidence[item].get("cutoff_eligible") for item in ids):
                raise ContractError(f"complete lane {lane_name} relies on cutoff-ineligible evidence")
            if reason is not None:
                raise ContractError(f"complete lane {lane_name} must not have a reason code")
        elif status in {"abstained", "blocked"}:
            if not ids:
                raise ContractError(f"{status} lane {lane_name} must reference evidence or an attempt record")
            if reason not in REASON_CODES:
                raise ContractError(f"{status} lane {lane_name} requires a reason code")
            _nonempty(next_action, f"lane {lane_name}.next_action", 20)
        elif status == "not_applicable":
            if not ids:
                raise ContractError(f"not_applicable lane {lane_name} must cite the identity/product basis")
            if reason != "not_applicable_to_asset":
                raise ContractError(f"not_applicable lane {lane_name} requires not_applicable_to_asset")
        if lane_name in {
            "fundamentals_product",
            "news_catalysts",
            "macro_transmission",
            "market_behavior",
        } and reason == "unavailable_current_price":
            raise ContractError(f"price unavailability cannot block independent lane {lane_name}")
    if terminal:
        if not any(lanes[name]["status"] == "complete" for name in REQUIRED_LANES):
            raise ContractError("a terminal symbol must contain at least one completed lane")
        if len(summaries) >= 7 and len(set(summaries)) == 1:
            raise ContractError("generic duplicate summaries do not demonstrate full-depth research")


def _validate_price_observation(
    state: dict[str, Any], evidence: dict[str, dict[str, Any]], cutoff: datetime, terminal: bool
) -> None:
    price = state.get("price_observation")
    if not isinstance(price, dict):
        raise ContractError("price_observation must be an object")
    status = price.get("status")
    allowed = {"verified", "unavailable", "not_applicable"} if terminal else {
        "not_started", "in_progress", "verified", "unavailable", "not_applicable"
    }
    if status not in allowed:
        raise ContractError(f"price_observation.status is invalid: {status}")
    reason = price.get("reason_code")
    _nullable_reason(reason, "price_observation.reason_code")
    price_lane = state["lanes"]["price_market"]["status"]
    numeric = ("native_value", "usd_value")
    descriptive = ("native_currency", "units", "observed_at", "market_session", "price_policy", "price_evidence_id")
    if status == "verified":
        if price_lane != "complete":
            raise ContractError("verified price observation requires a complete price_market lane")
        if not all(isinstance(price.get(name), (int, float)) and math.isfinite(price[name]) for name in numeric):
            raise ContractError("verified price observation requires finite native and USD values")
        currency = price.get("native_currency")
        if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
            raise ContractError("verified price native_currency must be a three-letter code")
        _nonempty(price.get("units"), "price_observation.units", 2)
        observed = parse_time(price.get("observed_at"), "price_observation.observed_at")
        if observed > cutoff:
            raise ContractError("price observation is after the decision cutoff")
        if price.get("market_session") not in MARKET_SESSIONS:
            raise ContractError("price observation market_session is invalid")
        if price.get("price_policy") not in PRICE_POLICIES:
            raise ContractError("price observation price_policy is invalid")
        evidence_id = price.get("price_evidence_id")
        if evidence_id not in evidence or not evidence[evidence_id].get("cutoff_eligible"):
            raise ContractError("verified price must reference cutoff-eligible price evidence")
        fx_id = price.get("fx_evidence_id")
        if currency == "USD":
            if abs(price["native_value"] - price["usd_value"]) > 0.000001 or fx_id is not None:
                raise ContractError("USD price must reconcile without an FX evidence ID")
        elif fx_id not in evidence or not evidence[fx_id].get("cutoff_eligible"):
            raise ContractError("non-USD price requires cutoff-eligible FX evidence")
        if reason is not None:
            raise ContractError("verified price observation must not have a reason code")
    elif status in {"unavailable", "not_applicable"}:
        expected_lane = {"blocked", "abstained"} if status == "unavailable" else {"not_applicable"}
        if price_lane not in expected_lane:
            raise ContractError("unavailable/not-applicable price does not reconcile with price_market lane")
        if reason not in REASON_CODES:
            raise ContractError("unavailable/not-applicable price requires a reason code")
        if any(price.get(name) is not None for name in (*numeric, *descriptive, "fx_evidence_id")):
            raise ContractError("unavailable/not-applicable price must not contain observation values")


def _string_array(value: Any, field: str, minimum: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum or any(
        not isinstance(item, str) or len(item.strip()) < 8 for item in value
    ):
        raise ContractError(f"{field} must contain at least {minimum} substantive string(s)")
    return value


def _validate_analysis_depth(state: dict[str, Any], evidence: dict[str, dict[str, Any]], cutoff: datetime) -> None:
    depth = state.get("analysis_depth")
    expected_keys = (
        "fundamentals_product",
        "valuation_scenarios",
        "news_catalysts",
        "macro_transmission",
        "market_behavior",
        "investment_thesis",
        "monitoring",
    )
    if not isinstance(depth, dict) or tuple(depth) != expected_keys:
        raise ContractError("analysis_depth is missing required sections or order")
    lanes = state["lanes"]
    if lanes["fundamentals_product"]["status"] == "complete":
        item = depth["fundamentals_product"]
        ids = _string_array(item.get("reconciliation_ids"), "analysis_depth fundamentals reconciliation_ids")
        if any(evidence_id not in evidence for evidence_id in ids):
            raise ContractError("fundamentals reconciliation references unknown evidence")
        _string_array(item.get("drivers"), "analysis_depth fundamentals drivers", 2)
        _nonempty(item.get("limitations"), "analysis_depth fundamentals limitations", 20)
    if lanes["valuation_scenarios"]["status"] == "complete":
        item = depth["valuation_scenarios"]
        method_minimum = 2 if state.get("asset_class", "").casefold() in {"stock", "equity"} else 1
        _string_array(item.get("methods"), "analysis_depth valuation methods", method_minimum)
        for scenario in ("base", "bull", "bear"):
            _nonempty(item.get(scenario), f"analysis_depth valuation {scenario}", 30)
        _nonempty(item.get("sensitivity"), "analysis_depth valuation sensitivity", 30)
    if lanes["news_catalysts"]["status"] == "complete":
        item = depth["news_catalysts"]
        start = parse_time(item.get("window_start"), "analysis_depth news window_start")
        end = parse_time(item.get("window_end"), "analysis_depth news window_end")
        if start > end or end > cutoff:
            raise ContractError("news search window is invalid or after cutoff")
        _nonempty(item.get("expectation_basis"), "analysis_depth news expectation_basis", 30)
    if lanes["macro_transmission"]["status"] == "complete":
        item = depth["macro_transmission"]
        ids = _string_array(item.get("shared_evidence_ids"), "analysis_depth macro shared_evidence_ids")
        if any(evidence_id not in evidence or evidence[evidence_id].get("scope") != "shared_macro" for evidence_id in ids):
            raise ContractError("macro transmission must reference shared macro evidence")
        _string_array(item.get("channels"), "analysis_depth macro channels")
        _nonempty(item.get("instrument_effect"), "analysis_depth macro instrument_effect", 30)
    if lanes["market_behavior"]["status"] == "complete":
        item = depth["market_behavior"]
        _string_array(item.get("observations"), "analysis_depth behavior observations")
        _string_array(item.get("alternatives"), "analysis_depth behavior alternatives")
        _nonempty(item.get("falsifier"), "analysis_depth behavior falsifier", 30)
    if lanes["investment_thesis"]["status"] == "complete":
        item = depth["investment_thesis"]
        if item.get("decision_status") not in {"observe", "investment_candidate", "avoid", "insufficient_evidence"}:
            raise ContractError("investment thesis decision_status is invalid")
        for field in ("variant_view", "market_implied_view", "contrary_case", "invalidation"):
            _nonempty(item.get(field), f"analysis_depth thesis {field}", 30)
        _string_array(item.get("catalysts"), "analysis_depth thesis catalysts")
        _string_array(item.get("disconfirmers"), "analysis_depth thesis disconfirmers")
    if lanes["monitoring"]["status"] == "complete":
        item = depth["monitoring"]
        _string_array(item.get("signals"), "analysis_depth monitoring signals", 2)
        parse_time(item.get("next_review"), "analysis_depth monitoring next_review")


def _validate_forecasts(state: dict[str, Any], terminal: bool) -> None:
    forecasts = state.get("forecasts")
    if not isinstance(forecasts, list):
        raise ContractError("forecasts must be an array")
    if not terminal and not forecasts:
        return
    if len(forecasts) != len(REQUIRED_HORIZONS):
        raise ContractError("forecasts must contain the four required horizons")
    if tuple(item.get("horizon") for item in forecasts if isinstance(item, dict)) != REQUIRED_HORIZONS:
        raise ContractError("forecast horizons are missing or out of order")
    for index, forecast in enumerate(forecasts):
        field = f"forecasts[{index}]"
        if not isinstance(forecast, dict):
            raise ContractError(f"{field} must be an object")
        status = forecast.get("status")
        if status not in {"registered", "abstained", "blocked"}:
            raise ContractError(f"{field}.status is invalid")
        reason = forecast.get("reason_code")
        _nullable_reason(reason, f"{field}.reason_code")
        numeric_fields = ("start_value", "up", "flat", "down")
        if status == "registered":
            values = [forecast.get(name) for name in numeric_fields]
            if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in values):
                raise ContractError(f"{field} registered values must be finite numbers")
            if forecast["start_value"] <= 0:
                raise ContractError(f"{field}.start_value must be positive")
            band = forecast.get("flat_band_return")
            if not isinstance(band, list) or len(band) != 2 or not all(
                isinstance(value, (int, float)) and math.isfinite(value) for value in band
            ) or band[0] > band[1]:
                raise ContractError(f"{field}.flat_band_return is invalid")
            if abs(forecast["up"] + forecast["flat"] + forecast["down"] - 100.0) > 0.01:
                raise ContractError(f"{field} probabilities do not total 100")
            _nonempty(forecast.get("forecast_id"), f"{field}.forecast_id", 8)
            if reason is not None:
                raise ContractError(f"{field} registered forecast must not have a reason code")
        else:
            if reason not in REASON_CODES:
                raise ContractError(f"{field} abstention/block requires a reason code")
            if any(forecast.get(name) is not None for name in (*numeric_fields, "flat_band_return", "forecast_id")):
                raise ContractError(f"{field} non-registered forecast must not contain numeric output or ID")


def _validate_risk(state: dict[str, Any], terminal: bool) -> None:
    risk = state.get("risk")
    if not isinstance(risk, dict):
        raise ContractError("risk must be an object")
    status = risk.get("status")
    allowed = {"complete", "abstained", "blocked"} if terminal else {
        "not_started", "in_progress", "complete", "abstained", "blocked"
    }
    if status not in allowed:
        raise ContractError(f"risk.status is invalid: {status}")
    reason = risk.get("reason_code")
    _nullable_reason(reason, "risk.reason_code")
    numeric = (
        "reference_capital_usd",
        "underlying_downside_return",
        "unlevered_pnl_usd",
        "gross_5x_pnl_usd",
    )
    if status == "complete":
        if not all(isinstance(risk.get(name), (int, float)) and math.isfinite(risk[name]) for name in numeric):
            raise ContractError("complete risk record requires finite numeric inputs")
        capital = risk["reference_capital_usd"]
        downside = risk["underlying_downside_return"]
        if capital <= 0 or downside > 0:
            raise ContractError("risk capital must be positive and downside return non-positive")
        if abs(risk["unlevered_pnl_usd"] - capital * downside) > 0.01:
            raise ContractError("unlevered risk arithmetic does not reconcile")
        if abs(risk["gross_5x_pnl_usd"] - capital * 5 * downside) > 0.01:
            raise ContractError("5x risk arithmetic does not reconcile")
        if reason is not None:
            raise ContractError("complete risk record must not have a reason code")
    elif status in {"abstained", "blocked"}:
        if reason not in REASON_CODES:
            raise ContractError("abstained/blocked risk requires a reason code")
        if any(risk.get(name) is not None for name in numeric):
            raise ContractError("abstained/blocked risk must not contain numeric output")


def _validate_depth_ledger(text: str, state: dict[str, Any], terminal: bool) -> None:
    content = markdown_section(text, "Research Depth Ledger")
    rows: list[list[str]] = []
    for line in content.splitlines():
        if not line.startswith("|") or line.startswith("|---") or "| Lane |" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 4:
            rows.append(cells)
    if [row[0] for row in rows] != [LANE_LABELS[name] for name in REQUIRED_LANES]:
        raise ContractError("Research Depth Ledger is missing or out of canonical order")
    for lane_name, row in zip(REQUIRED_LANES, rows, strict=True):
        expected = DISPLAY_STATUSES[state["lanes"][lane_name]["status"]]
        if row[1] != expected:
            raise ContractError(f"Research Depth Ledger status mismatch for {lane_name}")
        if terminal and (row[2] in {"—", "Not researched"} or len(row[2]) < 20):
            raise ContractError(f"Research Depth Ledger lacks work detail for {lane_name}")


def validate_latest_v3(text: str, symbol: str, *, require_terminal: bool) -> dict[str, Any]:
    """Return the parsed state or raise ContractError on the first violation."""

    if LATEST_V3_MARKER not in text or not text.startswith(f"# {symbol} — Latest Research\n"):
        raise ContractError("document is not the matching latest-v3 symbol artifact")
    missing = [heading for heading in REQUIRED_HEADINGS if not markdown_section(text, heading)]
    if missing:
        raise ContractError(f"missing required v3 headings: {', '.join(missing)}")
    state = json_block(text, "Machine-Readable Research State")
    if state.get("schema_version") != STATE_SCHEMA or state.get("symbol") != symbol:
        raise ContractError("state schema or symbol does not match the document")
    if state.get("reporting_currency") != "USD":
        raise ContractError("state reporting_currency must be USD")
    identity = state.get("identity_status")
    if identity not in {"resolved", "unresolved"}:
        raise ContractError("identity_status must be resolved or unresolved")
    research_status = state.get("research_status")
    allowed_research = {"complete", "partial", "blocked"} if require_terminal else {
        "not_started", "in_progress", "complete", "partial", "blocked"
    }
    if research_status not in allowed_research:
        raise ContractError(f"invalid research_status: {research_status}")
    if require_terminal:
        batch_id = state.get("batch_id")
        if not isinstance(batch_id, str) or not BATCH_PATTERN.fullmatch(batch_id):
            raise ContractError("batch_id must use YYYY-MM-DDTHHMMSSZ")
        cutoff = parse_time(state.get("decision_cutoff"), "decision_cutoff")
        completed = parse_time(state.get("access_completed_at"), "access_completed_at")
        if completed < cutoff:
            raise ContractError("access_completed_at cannot precede decision_cutoff")
        expected_checkpoint = f"research/batches/{batch_id}/RUN.json"
        if state.get("batch_checkpoint") != expected_checkpoint:
            raise ContractError("batch_checkpoint does not match batch_id")
        if identity == "resolved":
            _nonempty(state.get("exact_instrument"), "exact_instrument", 8)
        elif state.get("exact_instrument") is not None:
            raise ContractError("unresolved identity must not claim an exact instrument")
        if "Not researched" in text or "Not started" in text:
            raise ContractError("finalized v3 artifacts must not contain research placeholders")
    else:
        cutoff_value = state.get("decision_cutoff")
        cutoff = parse_time(cutoff_value, "decision_cutoff") if cutoff_value else datetime.now(timezone.utc)
    evidence = _validate_evidence(state, cutoff, require_terminal)
    _validate_lanes(state, evidence, require_terminal)
    _validate_price_observation(state, evidence, cutoff, require_terminal)
    _validate_analysis_depth(state, evidence, cutoff)
    _validate_forecasts(state, require_terminal)
    _validate_risk(state, require_terminal)
    unblockers = state.get("unblockers")
    if not isinstance(unblockers, list) or any(not isinstance(item, str) or len(item.strip()) < 20 for item in unblockers):
        raise ContractError("unblockers must be an array of substantive strings")
    if require_terminal:
        statuses = {state["lanes"][name]["status"] for name in REQUIRED_LANES}
        if "blocked" in statuses and research_status not in {"partial", "blocked"}:
            raise ContractError("a symbol with blocked lanes cannot claim complete research")
        if "blocked" not in statuses and research_status != "complete":
            raise ContractError("terminal research without blocked lanes must be complete")
        forecast_statuses = {forecast["status"] for forecast in state["forecasts"]}
        forecast_lane = state["lanes"]["directional_forecast"]["status"]
        if forecast_statuses == {"registered"} and forecast_lane != "complete":
            raise ContractError("registered forecasts require a complete directional_forecast lane")
        if "blocked" in forecast_statuses and forecast_lane not in {"blocked", "abstained"}:
            raise ContractError("blocked forecasts do not reconcile with the forecast lane")
        if forecast_statuses <= {"abstained"} and forecast_lane != "abstained":
            raise ContractError("forecast abstentions do not reconcile with the forecast lane")
        risk_status = state["risk"]["status"]
        risk_lane = state["lanes"]["downside_leverage"]["status"]
        if risk_status != risk_lane and not (
            risk_status == "abstained" and risk_lane == "blocked"
        ):
            raise ContractError("risk record does not reconcile with downside_leverage lane")
    _validate_depth_ledger(text, state, require_terminal)
    return state
