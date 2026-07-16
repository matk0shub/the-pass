"""Stateful Donchian fixture used by the public robustness audit."""

from decimal import Decimal

from the_pass.engine.contracts import SimulatedIntent


class RobustnessDonchianStrategy:
    strategy_id = "robustness_donchian_fixture_v1"

    def __init__(self, *, lookback: int, disabled: bool = False) -> None:
        if lookback < 2:
            raise ValueError("lookback must be at least two")
        self.lookback = lookback
        self.disabled = disabled
        self.closes: list[Decimal] = []
        self.intent_number = 0

    def on_event(self, event, context):
        close = Decimal(str(event.payload["close"]))
        current = context.positions.get(event.instrument_id, Decimal(0))
        target = current
        if context.event_index == context.total_events - 2:
            target = Decimal(0)
        elif not self.disabled and len(self.closes) >= self.lookback:
            window = self.closes[-self.lookback :]
            if close > max(window):
                target = Decimal(1)
            elif close < min(window):
                target = Decimal(-1)
        self.closes.append(close)
        delta = target - current
        if delta == 0 or context.event_index == context.total_events - 1:
            return []
        self.intent_number += 1
        return [
            SimulatedIntent(
                intent_id=f"robustness-donchian-{self.intent_number}",
                instrument_id=event.instrument_id,
                side="buy" if delta > 0 else "sell",
                quantity=abs(delta),
                decision_time_ns=context.decision_time_ns,
                intent_type="bar",
            )
        ]


def build_strategy(config):
    return RobustnessDonchianStrategy(
        lookback=int(config["lookback"]),
        disabled=bool(config.get("disabled", False)),
    )
