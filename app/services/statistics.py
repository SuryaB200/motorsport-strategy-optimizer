"""Statistical computation services for simulation outcomes."""

import numpy as np

from app.schemas.race import ObjectiveType
from app.schemas.results import StrategySummaryStats
from app.schemas.strategy import Strategy


class SimulationStatistics:
    """Computes rigorous statistical metrics and objective values across simulation runs."""

    @staticmethod
    def compute_summary(
        strategy: Strategy,
        race_times: list[float],
        objective_type: ObjectiveType = ObjectiveType.EXPECTED_TIME,
        risk_aversion_lambda: float = 0.0,
        rank: int = 1,
    ) -> StrategySummaryStats:
        """Compute statistical summary and objective score for an array of race times.

        Args:
            strategy: Evaluated strategy.
            race_times: List of total race durations in seconds across simulated scenarios.
            objective_type: EXPECTED_TIME or RISK_SENSITIVE.
            risk_aversion_lambda: Risk weight lambda >= 0.0.
            rank: Assigned relative rank.

        Returns:
            StrategySummaryStats instance.
        """
        n = len(race_times)
        if n == 0:
            raise ValueError("Cannot calculate statistics for an empty race time sample.")

        times_arr = np.array(race_times, dtype=np.float64)
        mean_time = float(np.mean(times_arr))
        median_time = float(np.median(times_arr))
        std_time = float(np.std(times_arr, ddof=1)) if n > 1 else 0.0
        min_time = float(np.min(times_arr))
        max_time = float(np.max(times_arr))
        p95_time = float(np.percentile(times_arr, 95))

        # Standard error and 95% confidence interval for the mean
        if n > 1:
            std_err = std_time / np.sqrt(n)
            ci_low = mean_time - 1.96 * std_err
            ci_high = mean_time + 1.96 * std_err
        else:
            ci_low = mean_time
            ci_high = mean_time

        # Objective calculation
        if objective_type == ObjectiveType.RISK_SENSITIVE:
            objective_value = mean_time + (risk_aversion_lambda * std_time)
        else:
            objective_value = mean_time

        return StrategySummaryStats(
            strategy=strategy,
            simulation_count=n,
            mean_race_time=mean_time,
            median_race_time=median_time,
            std_dev_race_time=std_time,
            min_race_time=min_time,
            max_race_time=max_time,
            p95_race_time=p95_time,
            confidence_interval_95_low=ci_low,
            confidence_interval_95_high=ci_high,
            objective_value=objective_value,
            rank=rank,
        )
