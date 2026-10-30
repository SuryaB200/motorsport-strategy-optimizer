"""Stochastic weather engine supporting Bernoulli and Markov chain transitions."""

from app.schemas.race import WeatherConfig, WeatherModelType, WeatherState
from app.services.random_source import RandomSource


class WeatherEngine:
    """Simulates weather sequences across race laps."""

    @staticmethod
    def generate_trajectory(
        config: WeatherConfig,
        total_laps: int,
        random_source: RandomSource,
    ) -> list[WeatherState]:
        """Generate a complete lap-by-lap weather trajectory.

        Args:
            config: Validated weather configuration.
            total_laps: Total number of race laps (length of trajectory).
            random_source: Encapsulated PRNG.

        Returns:
            List of WeatherState enums of length total_laps (index 0 corresponds to Lap 1).
        """
        if total_laps <= 0:
            raise ValueError(f"total_laps must be positive, got {total_laps}")

        if config.model_type == WeatherModelType.BERNOULLI:
            return WeatherEngine._generate_bernoulli(config, total_laps, random_source)
        elif config.model_type == WeatherModelType.MARKOV:
            return WeatherEngine._generate_markov(config, total_laps, random_source)
        else:
            raise ValueError(f"Unsupported weather model type: {config.model_type}")

    @staticmethod
    def _generate_bernoulli(
        config: WeatherConfig,
        total_laps: int,
        rng: RandomSource,
    ) -> list[WeatherState]:
        trajectory: list[WeatherState] = []
        for lap in range(1, total_laps + 1):
            # For lap 1, use initial rain probability if configured, else standard bernoulli
            p = config.initial_rain_probability if lap == 1 else config.bernoulli_rain_probability
            is_rain = rng.bernoulli(p)
            trajectory.append(WeatherState.RAIN if is_rain else WeatherState.DRY)
        return trajectory

    @staticmethod
    def _generate_markov(
        config: WeatherConfig,
        total_laps: int,
        rng: RandomSource,
    ) -> list[WeatherState]:
        trajectory: list[WeatherState] = []
        matrix = config.markov_transition_matrix
        # matrix format: [ [P(D->D), P(D->R)], [P(R->D), P(R->R)] ]

        # Initial lap
        current_state = config.initial_state
        trajectory.append(current_state)

        for _ in range(2, total_laps + 1):
            if current_state == WeatherState.DRY:
                p_stay_dry = matrix[0][0]
                next_is_dry = rng.bernoulli(p_stay_dry)
                current_state = WeatherState.DRY if next_is_dry else WeatherState.RAIN
            else:
                p_dry_from_rain = matrix[1][0]
                next_is_dry = rng.bernoulli(p_dry_from_rain)
                current_state = WeatherState.DRY if next_is_dry else WeatherState.RAIN

            trajectory.append(current_state)

        return trajectory
