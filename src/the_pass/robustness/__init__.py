"""Statistical validation and deterministic stress tooling."""

from .statistics import (
    WalkForwardSplit,
    block_bootstrap_means,
    cscv_pbo,
    deflated_sharpe_ratio,
    effective_sample_size,
    lag1_autocorrelation,
    probabilistic_sharpe_ratio,
    probabilistic_sharpe_ratio_effective,
    purged_walk_forward_splits,
    reality_check,
    regime_statistics,
    select_train_winner,
    sensitivity_report,
)
from .stress import StressParameters, run_stress_suite
from .workflow import run_strategy_sweep

__all__ = [
    "StressParameters",
    "WalkForwardSplit",
    "block_bootstrap_means",
    "cscv_pbo",
    "deflated_sharpe_ratio",
    "effective_sample_size",
    "lag1_autocorrelation",
    "probabilistic_sharpe_ratio",
    "probabilistic_sharpe_ratio_effective",
    "purged_walk_forward_splits",
    "reality_check",
    "regime_statistics",
    "select_train_winner",
    "run_stress_suite",
    "run_strategy_sweep",
    "sensitivity_report",
]
