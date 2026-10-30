"""Tire degradation and weather-compound suitability model."""

from dataclasses import dataclass

from app.schemas.race import TireCompound, TireCompoundParameters, WeatherState


@dataclass
class TireState:
    """Represents the current physical state of the fitted tires."""

    compound: TireCompound
    age_laps: int = 0
    set_number: int = 1

    def increment_age(self) -> None:
        """Increment tire age by 1 race lap."""
        self.age_laps += 1

    def reset(self, new_compound: TireCompound) -> None:
        """Reset tire age and increment set number upon fitting new tires."""
        self.compound = new_compound
        self.age_laps = 0
        self.set_number += 1


class TireModel:
    """Calculates tire degradation and weather compatibility deltas."""

    @staticmethod
    def calculate_degradation(
        age_laps: int,
        params: TireCompoundParameters,
        circuit_wear_factor: float = 1.0,
    ) -> float:
        """Calculate degradation time loss: D(a) = (d1 * a + d2 * a^2) * wear_factor.

        Args:
            age_laps: Number of completed race laps on this tire set (a >= 0).
            params: Compound degradation parameters.
            circuit_wear_factor: Circuit abrasion multiplier (default 1.0).

        Returns:
            Degradation time loss in seconds (non-negative).
        """
        if age_laps < 0:
            raise ValueError(f"Tire age cannot be negative, got {age_laps}")
        if circuit_wear_factor < 0:
            raise ValueError(f"Circuit wear factor cannot be negative, got {circuit_wear_factor}")

        d1 = params.degradation_linear
        d2 = params.degradation_quadratic
        deg = (d1 * age_laps + d2 * (age_laps**2)) * circuit_wear_factor
        return max(0.0, deg)

    @staticmethod
    def calculate_weather_penalty(
        compound: TireCompound,
        params: TireCompoundParameters,
        weather: WeatherState,
    ) -> float:
        """Calculate mismatch penalty for the compound in the given weather condition.

        Args:
            compound: Fitted tire compound.
            params: Compound parameters.
            weather: Current track weather condition (DRY or RAIN).

        Returns:
            Pace penalty in seconds.
        """
        if weather == WeatherState.DRY:
            return params.dry_suitability_penalty
        elif weather == WeatherState.RAIN:
            return params.rain_suitability_penalty
        else:
            raise ValueError(f"Unknown weather state: {weather}")

    @staticmethod
    def calculate_total_tire_delta(
        state: TireState,
        compound_params: dict[TireCompound, TireCompoundParameters],
        weather: WeatherState,
        circuit_wear_factor: float = 1.0,
    ) -> float:
        """Calculate combined lap time effect: base_offset + degradation + weather_penalty.

        Args:
            state: Current tire state.
            compound_params: Map of all compound parameters.
            weather: Current weather.
            circuit_wear_factor: Circuit wear multiplier.

        Returns:
            Total pace delta in seconds.
        """
        if state.compound not in compound_params:
            raise ValueError(f"Parameters missing for compound {state.compound}")

        params = compound_params[state.compound]
        base_offset = params.base_pace_offset
        deg = TireModel.calculate_degradation(state.age_laps, params, circuit_wear_factor)
        weather_penalty = TireModel.calculate_weather_penalty(state.compound, params, weather)

        return base_offset + deg + weather_penalty
