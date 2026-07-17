"""Versioned deterministic cost, liquidity, and operational stress scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Sequence


MANDATORY_STRESS_SCENARIOS = (
    "fees_x1_5",
    "slippage_x2",
    "latency_x2",
    "depth_x0_5",
    "depth_x0_25",
    "maker_fill_probability_x0_5",
    "funding_worst_decile",
    "exchange_outage",
    "missing_interval",
    "correlated_gap",
    "forced_deleverage",
)


@dataclass(frozen=True)
class StressParameters:
    gross_pnl: Decimal
    fees: Decimal
    slippage: Decimal
    spread: Decimal = Decimal(0)
    funding: Decimal = Decimal(0)
    impact: Decimal = Decimal(0)
    borrow: Decimal = Decimal(0)
    roll: Decimal = Decimal(0)
    other_costs: Decimal = Decimal(0)
    missed_fill_cost: Decimal = Decimal(0)
    outage_loss: Decimal = Decimal(0)
    gap_loss: Decimal = Decimal(0)
    deleverage_loss: Decimal = Decimal(0)
    inputs_source: str = "caller"


def stress_parameters_from_cost_waterfall(
    cost_waterfall: Mapping[str, Any],
    selected_oos_returns: Sequence[float],
) -> StressParameters:
    """Derive monetary stress inputs from package costs and aligned OOS returns."""

    if not selected_oos_returns:
        raise ValueError("stress evidence requires selected OOS returns")
    costs = cost_waterfall.get("costs")
    if not isinstance(costs, Mapping):
        raise ValueError("cost waterfall must contain a costs object")
    returns = [Decimal(str(value)) for value in selected_oos_returns]
    if any(not value.is_finite() for value in returns):
        raise ValueError("stress returns must be finite")
    gross_pnl = Decimal(str(cost_waterfall["gross_pnl"]))
    compounded = Decimal(1)
    for value in returns:
        compounded *= Decimal(1) + value
    compounded -= Decimal(1)
    scale = (
        abs(gross_pnl / compounded)
        if compounded != 0
        else max(abs(gross_pnl), Decimal(1))
    )
    worst_period = max(Decimal(0), -min(returns)) * scale
    wealth = Decimal(1)
    peak = Decimal(1)
    maximum_drawdown = Decimal(0)
    for value in returns:
        wealth *= Decimal(1) + value
        peak = max(peak, wealth)
        maximum_drawdown = max(maximum_drawdown, peak - wealth)
    known_costs = {
        "fees",
        "spread",
        "slippage",
        "funding",
        "impact",
        "borrow",
        "roll",
        "rejects_or_missed_fills",
    }
    numeric_costs: dict[str, Decimal] = {}
    for key, value in costs.items():
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise ValueError(f"cost component {key!r} must be numeric or null")
        converted = Decimal(str(value))
        if not converted.is_finite():
            raise ValueError(f"cost component {key!r} must be finite")
        numeric_costs[str(key)] = converted
    return StressParameters(
        gross_pnl=gross_pnl,
        fees=numeric_costs.get("fees", Decimal(0)),
        spread=numeric_costs.get("spread", Decimal(0)),
        slippage=numeric_costs.get("slippage", Decimal(0)),
        funding=numeric_costs.get("funding", Decimal(0)),
        impact=numeric_costs.get("impact", Decimal(0)),
        borrow=numeric_costs.get("borrow", Decimal(0)),
        roll=numeric_costs.get("roll", Decimal(0)),
        other_costs=sum(
            (value for key, value in numeric_costs.items() if key not in known_costs),
            Decimal(0),
        ),
        missed_fill_cost=numeric_costs.get(
            "rejects_or_missed_fills", Decimal(0)
        ),
        outage_loss=worst_period,
        gap_loss=worst_period * 2,
        deleverage_loss=maximum_drawdown * scale,
        inputs_source="cost_waterfall",
    )


def run_stress_suite(parameters: StressParameters) -> list[dict[str, Any]]:
    scenarios = (
        ("fees_x1_5", Decimal("1.5"), Decimal(1), Decimal(1), Decimal(1), Decimal(0)),
        ("slippage_x2", Decimal(1), Decimal(2), Decimal(1), Decimal(1), Decimal(0)),
        ("latency_x2", Decimal(1), Decimal("1.5"), Decimal(1), Decimal(1), parameters.missed_fill_cost),
        ("depth_x0_5", Decimal(1), Decimal(2), Decimal(1), Decimal(1), parameters.missed_fill_cost),
        ("depth_x0_25", Decimal(1), Decimal(4), Decimal(1), Decimal(1), parameters.missed_fill_cost * 2),
        ("maker_fill_probability_x0_5", Decimal(1), Decimal(1), Decimal(1), Decimal(1), parameters.missed_fill_cost * 2),
        ("funding_worst_decile", Decimal(1), Decimal(1), Decimal(2), Decimal(1), Decimal(0)),
    )
    results = []
    fixed_costs = (
        parameters.spread
        + parameters.impact
        + parameters.borrow
        + parameters.roll
        + parameters.other_costs
    )
    for name, fee_multiple, slippage_multiple, funding_multiple, _fill_multiple, extra in scenarios:
        net = (
            parameters.gross_pnl
            - parameters.fees * fee_multiple
            - fixed_costs
            - parameters.slippage * slippage_multiple
            - parameters.funding * funding_multiple
            - parameters.missed_fill_cost
            - extra
        )
        passed = net > 0
        results.append(
            {
                "scenario": name,
                "net_pnl": float(net),
                "pass": passed,
                "status": "pass" if passed else "blocked",
                "summary": "scenario remains net positive" if passed else "scenario is net negative and blocks promotion",
                "inputs_source": parameters.inputs_source,
                "formula": "cost_component_multiplier",
            }
        )
    for name, loss, formula in (
        ("exchange_outage", parameters.outage_loss, "worst_observed_oos_period_loss"),
        ("missing_interval", parameters.outage_loss, "worst_observed_oos_period_loss"),
        ("correlated_gap", parameters.gap_loss, "two_times_worst_observed_oos_period_loss"),
        ("forced_deleverage", parameters.deleverage_loss, "maximum_oos_drawdown_segment"),
    ):
        net = (
            parameters.gross_pnl
            - parameters.fees
            - fixed_costs
            - parameters.slippage
            - parameters.funding
            - parameters.missed_fill_cost
            - loss
        )
        passed = net > 0
        results.append(
            {
                "scenario": name,
                "net_pnl": float(net),
                "pass": passed,
                "status": "pass" if passed else "blocked",
                "summary": "scenario remains net positive" if passed else "scenario is net negative and blocks promotion",
                "inputs_source": parameters.inputs_source,
                "formula": formula,
            }
        )
    return results
