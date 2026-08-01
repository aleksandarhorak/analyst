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
COMPLETION_REQUIRED_LANES = (
    "identity_evidence",
    "price_market",
    "fundamentals_product",
    "valuation_scenarios",
    "news_catalysts",
    "macro_transmission",
    "investment_thesis",
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


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError(f"{field} must be a finite number")
    return float(value)


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
    descriptive = (
        "native_currency",
        "units",
        "observed_at",
        "market_session",
        "price_policy",
        "price_evidence_id",
        "fx_observed_at",
    )
    if status == "verified":
        if price_lane != "complete":
            raise ContractError("verified price observation requires a complete price_market lane")
        if not all(
            not isinstance(price.get(name), bool)
            and isinstance(price.get(name), (int, float))
            and math.isfinite(price[name])
            for name in numeric
        ):
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
            fx_rate = price.get("fx_rate_usd_per_native_unit")
            if (
                abs(price["native_value"] - price["usd_value"]) > 0.000001
                or fx_id is not None
                or fx_rate not in {None, 1, 1.0}
                or price.get("fx_observed_at") is not None
            ):
                raise ContractError("USD price must reconcile without an FX evidence ID")
        else:
            if fx_id not in evidence or not evidence[fx_id].get("cutoff_eligible"):
                raise ContractError("non-USD price requires cutoff-eligible FX evidence")
            fx_rate = _finite(price.get("fx_rate_usd_per_native_unit"), "price_observation.fx_rate_usd_per_native_unit")
            if fx_rate <= 0:
                raise ContractError("FX rate must be positive USD per native currency unit")
            fx_observed = parse_time(price.get("fx_observed_at"), "price_observation.fx_observed_at")
            if fx_observed > cutoff:
                raise ContractError("FX observation is after the decision cutoff")
            if abs(price["usd_value"] - price["native_value"] * fx_rate) > 0.000001:
                raise ContractError("native-to-USD price conversion does not reconcile")
        if reason is not None:
            raise ContractError("verified price observation must not have a reason code")
    elif status in {"unavailable", "not_applicable"}:
        expected_lane = {"blocked", "abstained"} if status == "unavailable" else {"not_applicable"}
        if price_lane not in expected_lane:
            raise ContractError("unavailable/not-applicable price does not reconcile with price_market lane")
        if reason not in REASON_CODES:
            raise ContractError("unavailable/not-applicable price requires a reason code")
        if any(
            price.get(name) is not None
            for name in (*numeric, *descriptive, "fx_evidence_id", "fx_rate_usd_per_native_unit")
        ):
            raise ContractError("unavailable/not-applicable price must not contain observation values")


def _string_array(value: Any, field: str, minimum: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum or any(
        not isinstance(item, str) or len(item.strip()) < 8 for item in value
    ):
        raise ContractError(f"{field} must contain at least {minimum} substantive string(s)")
    return value


def _eligible_evidence_ids(
    value: Any, field: str, evidence: dict[str, dict[str, Any]], minimum: int = 1
) -> list[str]:
    ids = _string_array(value, field, minimum)
    if any(item not in evidence or not evidence[item].get("cutoff_eligible") for item in ids):
        raise ContractError(f"{field} references missing or cutoff-ineligible evidence")
    return ids


def _numeric_bridge(value: Any, field: str) -> None:
    if not isinstance(value, dict):
        raise ContractError(f"{field} must be a structured numeric bridge")
    start = _finite(value.get("start"), f"{field}.start")
    end = _finite(value.get("end"), f"{field}.end")
    drivers = value.get("drivers")
    if not isinstance(drivers, list) or not drivers:
        raise ContractError(f"{field}.drivers must contain numeric bridge components")
    changes = 0.0
    for index, driver in enumerate(drivers):
        if not isinstance(driver, dict):
            raise ContractError(f"{field}.drivers[{index}] must be an object")
        _nonempty(driver.get("name"), f"{field}.drivers[{index}].name", 8)
        changes += _finite(driver.get("change"), f"{field}.drivers[{index}].change")
    if abs(end - (start + changes)) > 0.01:
        raise ContractError(f"{field} does not reconcile start plus drivers to end")


def _validate_fundamentals_product(
    item: Any, asset_class: str, evidence: dict[str, dict[str, Any]], cutoff: datetime
) -> None:
    if not isinstance(item, dict):
        raise ContractError("analysis_depth fundamentals_product must be an object")
    analysis_type = item.get("analysis_type")
    asset = asset_class.casefold()
    expected_type = (
        "equity"
        if asset in {"stock", "equity"}
        else "commodity_future"
        if "commodity" in asset or "future" in asset
        else "other_product"
    )
    if analysis_type != expected_type:
        raise ContractError(f"fundamentals/product analysis_type must be {expected_type} for {asset_class}")
    populated = [name for name in ("equity", "commodity_future", "other_product") if item.get(name) is not None]
    if populated != [expected_type]:
        raise ContractError("only the applicable asset-specific fundamentals/product schema may be populated")
    detail = item[expected_type]
    if not isinstance(detail, dict):
        raise ContractError(f"{expected_type} analysis must be an object")
    if expected_type == "equity":
        _string_array(detail.get("periods"), "equity periods", 2)
        _eligible_evidence_ids(detail.get("statement_evidence_ids"), "equity statement evidence", evidence, 2)
        if not isinstance(detail.get("currency"), str) or not re.fullmatch(r"[A-Z]{3}", detail["currency"]):
            raise ContractError("equity currency must be a three-letter code")
        _nonempty(detail.get("scale"), "equity scale", 3)
        _numeric_bridge(detail.get("revenue_bridge"), "equity revenue_bridge")
        _numeric_bridge(detail.get("margin_bridge"), "equity margin_bridge")
        cash = detail.get("cash_flow_bridge")
        if not isinstance(cash, dict):
            raise ContractError("equity cash_flow_bridge must be an object")
        operating = _finite(cash.get("operating_cash_flow"), "equity operating_cash_flow")
        capex = _finite(cash.get("capital_expenditure"), "equity capital_expenditure")
        free_cash = _finite(cash.get("free_cash_flow"), "equity free_cash_flow")
        if capex < 0 or abs(free_cash - (operating - capex)) > 0.01:
            raise ContractError("equity free cash flow does not reconcile to operating cash flow less capex")
        debt = _finite(detail.get("debt"), "equity debt")
        cash_value = _finite(detail.get("cash"), "equity cash")
        net_debt = _finite(detail.get("net_debt"), "equity net_debt")
        if abs(net_debt - (debt - cash_value)) > 0.01:
            raise ContractError("equity net debt does not reconcile")
        basic = _finite(detail.get("basic_shares"), "equity basic_shares")
        diluted = _finite(detail.get("diluted_shares"), "equity diluted_shares")
        if basic <= 0 or diluted < basic:
            raise ContractError("equity diluted shares must be positive and not below basic shares")
        for field in ("earnings_quality", "liquidity", "capital_allocation", "governance"):
            _nonempty(detail.get(field), f"equity {field}", 30)
    elif expected_type == "commodity_future":
        for field in ("exchange", "contract_month", "native_units", "settlement", "delivery", "roll_method"):
            _nonempty(detail.get(field), f"commodity/future {field}", 3 if field != "delivery" else 20)
        multiplier = _finite(detail.get("contract_multiplier"), "commodity/future contract_multiplier")
        if multiplier <= 0:
            raise ContractError("commodity/future contract multiplier must be positive")
        curve = detail.get("curve")
        if not isinstance(curve, list) or len(curve) < 2:
            raise ContractError("commodity/future curve requires at least two contract points")
        for index, point in enumerate(curve):
            if not isinstance(point, dict):
                raise ContractError(f"commodity/future curve[{index}] must be an object")
            _nonempty(point.get("contract"), f"commodity/future curve[{index}].contract", 3)
            _finite(point.get("price"), f"commodity/future curve[{index}].price")
            observed = parse_time(point.get("observed_at"), f"commodity/future curve[{index}].observed_at")
            if observed > cutoff:
                raise ContractError("commodity/future curve point is after cutoff")
            _eligible_evidence_ids([point.get("evidence_id")], f"commodity/future curve[{index}] evidence", evidence)
        spot = _finite(detail.get("spot_value"), "commodity/future spot_value")
        future = _finite(detail.get("reference_future_value"), "commodity/future reference_future_value")
        basis = _finite(detail.get("basis_spot_minus_future"), "commodity/future basis")
        if abs(basis - (spot - future)) > 0.000001:
            raise ContractError("commodity/future basis does not reconcile")
        initial = _finite(detail.get("initial_margin"), "commodity/future initial_margin")
        maintenance = _finite(detail.get("maintenance_margin"), "commodity/future maintenance_margin")
        if initial <= 0 or maintenance <= 0 or maintenance > initial:
            raise ContractError("commodity/future margin values are invalid")
        _nonempty(detail.get("margin_currency"), "commodity/future margin_currency", 3)
        _nonempty(detail.get("physical_balance"), "commodity/future physical_balance", 30)
    else:
        for field in ("exact_underlying", "payoff", "units", "liquidity", "limitations"):
            _nonempty(detail.get(field), f"other product {field}", 20 if field != "units" else 3)
        _eligible_evidence_ids(detail.get("evidence_ids"), "other product evidence", evidence)


def _validate_valuation(
    item: Any, asset_class: str, evidence: dict[str, dict[str, Any]]
) -> None:
    if not isinstance(item, dict):
        raise ContractError("analysis_depth valuation_scenarios must be an object")
    is_equity = asset_class.casefold() in {"stock", "equity"}
    methods = item.get("methods")
    required_methods = 2 if is_equity else 1
    if not isinstance(methods, list) or len(methods) < required_methods:
        raise ContractError(f"valuation methods must contain at least {required_methods} structured method(s)")
    method_names: set[str] = set()
    for index, method in enumerate(methods):
        field = f"valuation methods[{index}]"
        if not isinstance(method, dict):
            raise ContractError(f"{field} must be an object")
        name = _nonempty(method.get("name"), f"{field}.name", 3)
        if name in method_names:
            raise ContractError("valuation methods must be distinct")
        method_names.add(name)
        if method.get("currency") != "USD":
            raise ContractError(f"{field}.currency must be USD")
        expected_unit = "per_share" if is_equity else "native_unit"
        if method.get("unit") != expected_unit:
            raise ContractError(f"{field}.unit must be {expected_unit}")
        low = _finite(method.get("low"), f"{field}.low")
        base = _finite(method.get("base"), f"{field}.base")
        high = _finite(method.get("high"), f"{field}.high")
        if not low <= base <= high:
            raise ContractError(f"{field} range must satisfy low <= base <= high")
        inputs = method.get("inputs")
        if not isinstance(inputs, list) or len(inputs) < 2:
            raise ContractError(f"{field}.inputs requires at least two structured assumptions")
        for input_index, assumption in enumerate(inputs):
            if not isinstance(assumption, dict):
                raise ContractError(f"{field}.inputs[{input_index}] must be an object")
            _nonempty(assumption.get("name"), f"{field}.inputs[{input_index}].name", 3)
            _finite(assumption.get("value"), f"{field}.inputs[{input_index}].value")
            _nonempty(assumption.get("unit"), f"{field}.inputs[{input_index}].unit", 2)
            _eligible_evidence_ids(
                assumption.get("evidence_ids"), f"{field}.inputs[{input_index}].evidence_ids", evidence
            )
        _eligible_evidence_ids(method.get("evidence_ids"), f"{field}.evidence_ids", evidence)
    scenarios = item.get("scenarios")
    if not isinstance(scenarios, dict) or tuple(scenarios) != ("base", "bull", "bear"):
        raise ContractError("valuation scenarios must contain base, bull, and bear in canonical order")
    scenario_values: dict[str, float] = {}
    for name, scenario in scenarios.items():
        if not isinstance(scenario, dict):
            raise ContractError(f"valuation scenario {name} must be an object")
        scenario_values[name] = _finite(scenario.get("value"), f"valuation scenario {name}.value")
        _string_array(scenario.get("drivers"), f"valuation scenario {name}.drivers", 2)
        _nonempty(scenario.get("trigger"), f"valuation scenario {name}.trigger", 20)
    if not scenario_values["bear"] <= scenario_values["base"] <= scenario_values["bull"]:
        raise ContractError("valuation scenario values must satisfy bear <= base <= bull")
    bridge = item.get("enterprise_to_equity")
    if is_equity:
        if not isinstance(bridge, dict) or bridge.get("currency") != "USD":
            raise ContractError("equity valuation requires a USD enterprise-to-equity bridge")
        enterprise = _finite(bridge.get("enterprise_value"), "valuation enterprise_value")
        cash_value = _finite(bridge.get("cash"), "valuation bridge cash")
        debt = _finite(bridge.get("debt"), "valuation bridge debt")
        adjustments = _finite(bridge.get("other_adjustments"), "valuation bridge other_adjustments")
        equity_value = _finite(bridge.get("equity_value"), "valuation bridge equity_value")
        shares = _finite(bridge.get("diluted_shares"), "valuation bridge diluted_shares")
        per_share = _finite(bridge.get("per_share_value"), "valuation bridge per_share_value")
        if shares <= 0 or abs(equity_value - (enterprise + cash_value - debt + adjustments)) > 0.01:
            raise ContractError("enterprise-to-equity bridge does not reconcile")
        if abs(per_share - equity_value / shares) > 0.000001:
            raise ContractError("equity per-share value does not reconcile")
        _eligible_evidence_ids(bridge.get("evidence_ids"), "valuation bridge evidence_ids", evidence)
    elif bridge is not None:
        raise ContractError("non-equity valuation must not fabricate an enterprise-to-equity bridge")
    sensitivities = item.get("sensitivities")
    if not isinstance(sensitivities, list) or not sensitivities:
        raise ContractError("valuation requires at least one structured sensitivity")
    for index, sensitivity in enumerate(sensitivities):
        if not isinstance(sensitivity, dict):
            raise ContractError(f"valuation sensitivity[{index}] must be an object")
        _nonempty(sensitivity.get("input"), f"valuation sensitivity[{index}].input", 3)
        low = _finite(sensitivity.get("low"), f"valuation sensitivity[{index}].low")
        high = _finite(sensitivity.get("high"), f"valuation sensitivity[{index}].high")
        if low > high:
            raise ContractError(f"valuation sensitivity[{index}] low exceeds high")
        _nonempty(sensitivity.get("effect"), f"valuation sensitivity[{index}].effect", 20)


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
        _validate_fundamentals_product(depth["fundamentals_product"], state.get("asset_class", ""), evidence, cutoff)
    if lanes["valuation_scenarios"]["status"] == "complete":
        _validate_valuation(depth["valuation_scenarios"], state.get("asset_class", ""), evidence)
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


def _validate_forecasts(
    state: dict[str, Any], evidence: dict[str, dict[str, Any]], cutoff: datetime, terminal: bool
) -> None:
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
            if not all(
                not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
                for value in values
            ):
                raise ContractError(f"{field} registered values must be finite numbers")
            if forecast["start_value"] <= 0:
                raise ContractError(f"{field}.start_value must be positive")
            band = forecast.get("flat_band_return")
            if not isinstance(band, list) or len(band) != 2 or not all(
                not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
                for value in band
            ) or band[0] > band[1]:
                raise ContractError(f"{field}.flat_band_return is invalid")
            if abs(forecast["up"] + forecast["flat"] + forecast["down"] - 100.0) > 0.01:
                raise ContractError(f"{field} probabilities do not total 100")
            _nonempty(forecast.get("forecast_id"), f"{field}.forecast_id", 8)
            _eligible_evidence_ids(forecast.get("evidence_ids"), f"{field}.evidence_ids", evidence)
            _nonempty(forecast.get("calibration_basis"), f"{field}.calibration_basis", 30)
            base_rate = forecast.get("base_rate")
            if not isinstance(base_rate, list) or len(base_rate) != 3 or not all(
                not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
                for value in base_rate
            ) or abs(sum(base_rate) - 100.0) > 0.01:
                raise ContractError(f"{field}.base_rate must be a three-way distribution totaling 100")
            _nonempty(forecast.get("scenario_mapping"), f"{field}.scenario_mapping", 30)
            if forecast.get("confidence") not in {"low", "medium", "high"}:
                raise ContractError(f"{field}.confidence is invalid")
            outcome = parse_time(forecast.get("outcome_at"), f"{field}.outcome_at")
            if outcome <= cutoff:
                raise ContractError(f"{field}.outcome_at must follow the decision cutoff")
            _nonempty(forecast.get("resolution_definition"), f"{field}.resolution_definition", 30)
            if any(forecast.get(name) is not None for name in ("summary", "attempt_ids", "next_action")):
                raise ContractError(f"{field} registered forecast must not contain abstention fields")
            if reason is not None:
                raise ContractError(f"{field} registered forecast must not have a reason code")
        else:
            if reason not in REASON_CODES:
                raise ContractError(f"{field} abstention/block requires a reason code")
            _nonempty(forecast.get("summary"), f"{field}.summary", 30)
            attempt_ids = _string_array(forecast.get("attempt_ids"), f"{field}.attempt_ids")
            if any(item not in evidence for item in attempt_ids):
                raise ContractError(f"{field}.attempt_ids reference unknown evidence/attempt records")
            _nonempty(forecast.get("next_action"), f"{field}.next_action", 20)
            if forecast.get("confidence") != "insufficient":
                raise ContractError(f"{field} abstention/block confidence must be insufficient")
            registered_only = (
                *numeric_fields,
                "flat_band_return",
                "forecast_id",
                "evidence_ids",
                "calibration_basis",
                "base_rate",
                "scenario_mapping",
                "outcome_at",
                "resolution_definition",
            )
            if any(forecast.get(name) is not None for name in registered_only):
                raise ContractError(f"{field} non-registered forecast must not contain registered output fields")


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
    if status in {"complete", "abstained", "blocked"}:
        if risk.get("liquidity_status") not in {"liquid", "limited", "illiquid", "unknown"}:
            raise ContractError("terminal risk liquidity_status is invalid")
        for field in ("costs_summary", "margin_liquidation_summary"):
            value = _nonempty(risk.get(field), f"risk.{field}", 30)
            if "|" in value or "\n" in value:
                raise ContractError(f"risk.{field} contains Markdown table control characters")
    if status == "complete":
        if not all(
            not isinstance(risk.get(name), bool)
            and isinstance(risk.get(name), (int, float))
            and math.isfinite(risk[name])
            for name in numeric
        ):
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


def validate_latest_v3(
    text: str, symbol: str, *, expected_asset_class: str, require_terminal: bool
) -> dict[str, Any]:
    """Return the parsed state or raise ContractError on the first violation."""

    if LATEST_V3_MARKER not in text or not text.startswith(f"# {symbol} — Latest Research\n"):
        raise ContractError("document is not the matching latest-v3 symbol artifact")
    missing = [heading for heading in REQUIRED_HEADINGS if not markdown_section(text, heading)]
    if missing:
        raise ContractError(f"missing required v3 headings: {', '.join(missing)}")
    state = json_block(text, "Machine-Readable Research State")
    if state.get("schema_version") != STATE_SCHEMA or state.get("symbol") != symbol:
        raise ContractError("state schema or symbol does not match the document")
    if state.get("asset_class") != expected_asset_class:
        raise ContractError("state asset_class does not match the frozen active universe")
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
    _validate_forecasts(state, evidence, cutoff, require_terminal)
    _validate_risk(state, require_terminal)
    unblockers = state.get("unblockers")
    if not isinstance(unblockers, list) or any(not isinstance(item, str) or len(item.strip()) < 20 for item in unblockers):
        raise ContractError("unblockers must be an array of substantive strings")
    if require_terminal:
        statuses = {state["lanes"][name]["status"] for name in REQUIRED_LANES}
        incomplete_core = [
            name for name in COMPLETION_REQUIRED_LANES if state["lanes"][name]["status"] != "complete"
        ]
        partial_required = "blocked" in statuses or bool(incomplete_core)
        if partial_required and research_status not in {"partial", "blocked"}:
            raise ContractError(
                "blocked or incomplete core lanes require partial/blocked research status: "
                + ", ".join(incomplete_core)
            )
        if not partial_required and research_status != "complete":
            raise ContractError("research with every core lane complete must use complete status")
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
