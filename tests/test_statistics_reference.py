from __future__ import annotations

import unittest

import numpy as np

from the_pass.robustness import (
    cscv_pbo,
    deflated_sharpe_ratio,
    probabilistic_sharpe_ratio,
    reality_check,
)


class StatisticsReferenceTests(unittest.TestCase):
    def test_psr_matches_hand_derived_bailey_lopez_de_prado_value(self) -> None:
        returns = [0.01, -0.02, 0.015, 0.005, -0.01, 0.02]
        # Hand derivation (sample conventions match the published estimator):
        # mean=0.003333333333333333, std(ddof=1)=0.015383974345619103,
        # SR=0.2166756950087197, skew=-0.704958951366398,
        # Pearson kurtosis=2.0701249752033326.  The BLdP variance term is
        # 1-skew*SR+((kurtosis-1)/4)*SR^2=1.1653076230310515;
        # z=SR*sqrt(6-1)/sqrt(variance)=0.4488227958042463 and Phi(z) below.
        expected_psr = 0.673220253522502
        self.assertAlmostEqual(
            probabilistic_sharpe_ratio(returns), expected_psr, places=9
        )

    def test_dsr_matches_hand_derived_expected_maximum(self) -> None:
        returns = [0.01, -0.02, 0.015, 0.005, -0.01, 0.02]
        trial_sharpes = [-0.2, 0.0, 0.1, 0.3]
        # std(trials, ddof=1)=0.20816659994661327.  With four trials and
        # Euler gamma=0.5772156649015329, the BLdP approximation
        # sigma*((1-gamma)*Phi^-1(.75)+gamma*Phi^-1(1-1/(4e))) gives
        # E[max SR]=0.21901683103771502.  Substitution into the PSR equation
        # gives z=-0.004849437394671554 and DSR=0.49806536196993634.
        expected_dsr = 0.49806536196993634
        self.assertAlmostEqual(
            deflated_sharpe_ratio(returns, trial_sharpes=trial_sharpes),
            expected_dsr,
            places=9,
        )

    def test_cscv_pbo_extremes_and_hand_counted_intermediate(self) -> None:
        # Each column totals 12.  Therefore every two-block IS winner is the
        # strict OOS loser in its complementary two blocks: 6/6 negative logits.
        always_loses_oos = [
            [-1.0, 0.0, 5.0],
            [9.0, -9.0, -7.0],
            [6.0, 9.0, -5.0],
            [-2.0, 12.0, 19.0],
        ]
        # Variant zero strictly wins every block, hence every IS/OOS split:
        # 0/6 negative logits.
        always_wins_oos = [
            [3.0, 2.0, 1.0],
            [4.0, 2.0, 0.0],
            [5.0, 1.0, 0.0],
            [6.0, 2.0, 1.0],
        ]
        # The six complementary splits have logit signs -,+,-,+,+,-, so the
        # hand-counted overfit fraction is 3/6=0.5.
        intermediate = [
            [2.0, 0.0, -3.0],
            [3.0, 1.0, 1.0],
            [-9.0, -4.0, 9.0],
            [-1.0, -1.0, 4.0],
        ]
        self.assertEqual(cscv_pbo(always_loses_oos, blocks=4)["pbo"], 1.0)
        self.assertEqual(cscv_pbo(always_wins_oos, blocks=4)["pbo"], 0.0)
        self.assertEqual(cscv_pbo(intermediate, blocks=4)["pbo"], 0.5)

    def test_reality_check_degenerate_and_seeded_reference_values(self) -> None:
        # Centering an all-zero matrix produces a zero bootstrap distribution;
        # observed_max is also zero, so every draw exceeds it and p=1 exactly.
        degenerate = reality_check(
            [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            bootstrap_samples=20,
            seed=3,
        )
        self.assertEqual(degenerate["reality_check_pvalue"], 1.0)
        self.assertEqual(degenerate["spa_pvalue"], 1.0)
        self.assertEqual(degenerate["block_length"], 2)

        seeded_matrix = [
            [0.01, -0.01, 0.002],
            [-0.02, 0.01, -0.003],
            [0.015, -0.005, 0.004],
            [0.005, 0.002, -0.001],
            [-0.01, 0.003, 0.002],
            [0.02, -0.004, 0.005],
        ]
        # ceil(6**(1/3))=2. Circular two-row blocks with seed 11 produce
        # 27/100 maxima and 8/100 SPA maxima at or above the observations. The
        # +1 correction therefore gives 28/101 and 9/101 respectively.
        seeded = reality_check(seeded_matrix, bootstrap_samples=100, seed=11)
        self.assertEqual(seeded["reality_check_pvalue"], 28 / 101)
        self.assertEqual(seeded["spa_pvalue"], 9 / 101)
        self.assertEqual(seeded["block_length"], 2)

    def test_block_sign_flip_reference_value_and_recorded_length(self) -> None:
        from the_pass.robustness import mean_difference_permutation_pvalue

        # ceil(4**(1/3))=2, so each draw flips two circular contiguous blocks.
        # Seed 3 produces 6/20 draws with both blocks positive; with the +1
        # correction the one-sided p-value is (6+1)/(20+1)=1/3.
        result = mean_difference_permutation_pvalue(
            [1.0] * 4, [0.0] * 4, samples=20, seed=3
        )
        self.assertEqual(result, {"pvalue": 1 / 3, "block_length": 2})

    def test_random_walk_strategy_calibration_smoke(self) -> None:
        # 200 independent zero-drift strategies, represented by their 160
        # seeded random-walk increments.  A broad [0.3, 0.7] tolerance detects
        # severe rank/calibration regressions without demanding an exact draw.
        generator = np.random.default_rng(20260717)
        strategy_returns = generator.normal(0.0, 1.0, size=(160, 200))
        pbo = cscv_pbo(strategy_returns, blocks=8)["pbo"]
        self.assertGreaterEqual(pbo, 0.3)
        self.assertLessEqual(pbo, 0.7)


if __name__ == "__main__":
    unittest.main()
