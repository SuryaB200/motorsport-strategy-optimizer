"""Safety Car event generation and pit-stop interaction engine."""

from app.schemas.race import SafetyCarConfig
from app.schemas.simulation import SafetyCarEvent
from app.services.random_source import RandomSource


class SafetyCarEngine:
    """Manages stochastic Safety Car deployment and race neutralization effects."""

    @staticmethod
    def generate_events(
        config: SafetyCarConfig,
        total_laps: int,
        random_source: RandomSource,
    ) -> list[SafetyCarEvent]:
        """Generate non-overlapping Safety Car deployment events across the race.

        Args:
            config: Safety Car configuration parameters.
            total_laps: Total laps in the race.
            random_source: Encapsulated PRNG.

        Returns:
            List of SafetyCarEvent instances.
        """
        if total_laps <= 0:
            raise ValueError(f"total_laps must be positive, got {total_laps}")

        events: list[SafetyCarEvent] = []
        current_lap = 1

        while current_lap <= total_laps:
            # Check if an incident occurs on this lap
            incident_occurred = random_source.bernoulli(config.incident_probability_per_lap)
            if incident_occurred:
                # Check if incident causes Safety Car deployment
                sc_deployed = random_source.bernoulli(config.deployment_given_incident_probability)
                if sc_deployed:
                    duration = random_source.integers(
                        config.min_duration_laps, config.max_duration_laps
                    )
                    start_lap = current_lap
                    end_lap = min(start_lap + duration - 1, total_laps)
                    actual_duration = end_lap - start_lap + 1

                    event = SafetyCarEvent(
                        event_id=f"sc-{len(events) + 1}",
                        start_lap=start_lap,
                        end_lap=end_lap,
                        duration_laps=actual_duration,
                    )
                    events.append(event)
                    # Advance past the event duration to prevent overlapping deployments
                    current_lap = end_lap + 1
                    continue

            current_lap += 1

        return events

    @staticmethod
    def is_safety_car_active(events: list[SafetyCarEvent], lap: int) -> bool:
        """Check whether the Safety Car is deployed on track during a given lap."""
        for event in events:
            if event.start_lap <= lap <= event.end_lap:
                return True
        return False

    @staticmethod
    def get_effective_pit_loss(config: SafetyCarConfig, sc_active: bool) -> float:
        """Calculate pit lane time loss based on race neutralization state.

        Args:
            config: Safety car configuration with pit loss parameters.
            sc_active: True if Safety Car is active during the pit entry lap.

        Returns:
            Applicable pit-lane time loss in seconds.
        """
        if sc_active:
            return config.pit_loss_safety_car
        return config.pit_loss_normal
