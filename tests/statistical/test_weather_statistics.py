"""Statistical tests verifying stochastic behavior of weather models and pace variation."""

import numpy as np

from app.schemas.race import WeatherConfig, WeatherModelType, WeatherState
from app.services.random_source import RandomSource
from app.services.weather import WeatherEngine


def test_bernoulli_distribution_convergence():
    """Verify that sample rain frequency converges to configured Bernoulli probability."""
    p_true = 0.35
    total_laps = 10000
    config = WeatherConfig(
        model_type=WeatherModelType.BERNOULLI,
        bernoulli_rain_probability=p_true,
        initial_rain_probability=p_true,
    )
    rng = RandomSource(seed=777)
    trajectory = WeatherEngine.generate_trajectory(config, total_laps=total_laps, random_source=rng)

    rain_count = sum(1 for s in trajectory if s == WeatherState.RAIN)
    p_hat = rain_count / total_laps

    # Theoretical standard error: sqrt(p * (1-p) / N)
    std_err = np.sqrt(p_true * (1 - p_true) / total_laps)
    # 99.7% confidence margin (3 * std_err)
    tolerance = 3 * std_err

    assert abs(p_hat - p_true) < tolerance, (
        f"Bernoulli sample mean {p_hat:.4f} deviated from {p_true} by more than {tolerance:.4f}"
    )


def test_markov_transition_probabilities_convergence():
    """Verify that empirical transition counts match configured Markov transition matrix."""
    p_dry_dry = 0.80
    p_dry_rain = 0.20
    p_rain_dry = 0.35
    p_rain_rain = 0.65

    config = WeatherConfig(
        model_type=WeatherModelType.MARKOV,
        initial_state=WeatherState.DRY,
        markov_transition_matrix=[
            [p_dry_dry, p_dry_rain],
            [p_rain_dry, p_rain_rain],
        ],
    )
    total_laps = 15000
    rng = RandomSource(seed=888)
    trajectory = WeatherEngine.generate_trajectory(config, total_laps=total_laps, random_source=rng)

    # Count transitions
    n_dd = 0
    n_dr = 0
    n_rd = 0
    n_rr = 0

    for i in range(len(trajectory) - 1):
        s_curr = trajectory[i]
        s_next = trajectory[i + 1]
        if s_curr == WeatherState.DRY and s_next == WeatherState.DRY:
            n_dd += 1
        elif s_curr == WeatherState.DRY and s_next == WeatherState.RAIN:
            n_dr += 1
        elif s_curr == WeatherState.RAIN and s_next == WeatherState.DRY:
            n_rd += 1
        elif s_curr == WeatherState.RAIN and s_next == WeatherState.RAIN:
            n_rr += 1

    emp_p_dd = n_dd / (n_dd + n_dr)
    emp_p_rr = n_rr / (n_rd + n_rr)

    assert abs(emp_p_dd - p_dry_dry) < 0.02, (
        f"Empirical P(Dry->Dry) {emp_p_dd:.4f} differed from {p_dry_dry}"
    )
    assert abs(emp_p_rr - p_rain_rain) < 0.02, (
        f"Empirical P(Rain->Rain) {emp_p_rr:.4f} differed from {p_rain_rain}"
    )


def test_normal_pace_variation_statistics():
    """Verify that RandomSource normal generator has configured mean and standard deviation."""
    target_mu = 0.0
    target_sigma = 0.30
    sample_size = 20000

    rng = RandomSource(seed=999)
    samples = np.array([rng.normal(target_mu, target_sigma) for _ in range(sample_size)])

    sample_mean = float(np.mean(samples))
    sample_std = float(np.std(samples, ddof=1))

    # Mean tolerance (3 * sigma / sqrt(N))
    mean_tol = 3.0 * (target_sigma / np.sqrt(sample_size))
    # Variance / std tolerance
    std_tol = 0.015

    assert abs(sample_mean - target_mu) < mean_tol, (
        f"Sample mean {sample_mean:.4f} exceeded tolerance {mean_tol:.4f}"
    )
    assert abs(sample_std - target_sigma) < std_tol, (
        f"Sample std {sample_std:.4f} exceeded tolerance {std_tol:.4f}"
    )
