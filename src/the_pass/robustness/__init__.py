"""Statistical validation and deterministic stress tooling."""

from .statistics import (
    WalkForwardSplit,
    block_bootstrap_means,
    cscv_pbo,
    deflated_sharpe_ratio,
    effective_sample_size,
    lag1_autocorrelation,
    mean_difference_permutation_pvalue,
    probabilistic_sharpe_ratio,
    probabilistic_sharpe_ratio_effective,
    purged_walk_forward_splits,
    reality_check,
    regime_statistics,
    select_train_winner,
    sensitivity_report,
)
from .stress import (
    MANDATORY_STRESS_SCENARIOS,
    StressParameters,
    run_stress_suite,
    stress_parameters_from_cost_waterfall,
)
from .workflow import run_strategy_sweep

__all__ = [
    "MANDATORY_STRESS_SCENARIOS",
    "StressParameters",
    "WalkForwardSplit",
    "block_bootstrap_means",
    "cscv_pbo",
    "deflated_sharpe_ratio",
    "effective_sample_size",
    "lag1_autocorrelation",
    "mean_difference_permutation_pvalue",
    "probabilistic_sharpe_ratio",
    "probabilistic_sharpe_ratio_effective",
    "purged_walk_forward_splits",
    "reality_check",
    "regime_statistics",
    "select_train_winner",
    "run_stress_suite",
    "stress_parameters_from_cost_waterfall",
    "run_strategy_sweep",
    "sensitivity_report",
]
