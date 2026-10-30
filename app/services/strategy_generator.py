"""Candidate strategy generation engine supporting exhaustive and bounded heuristic search."""

import itertools

from app.schemas.strategy import PitStopDecision, Strategy, StrategyConstraints


class StrategyGenerator:
    """Generates legal candidate tire and pit stop strategies for a given race distance."""

    @staticmethod
    def generate_candidates(
        total_laps: int,
        constraints: StrategyConstraints,
        max_candidates: int = 100,
    ) -> list[Strategy]:
        """Generate a diverse, bounded set of legal candidate strategies.

        Uses exhaustive generation when combinations are small, otherwise falls back to
        balanced strategic windows (early, balanced, and late pit windows).
        """
        candidates = StrategyGenerator.generate_heuristic_grid(
            total_laps=total_laps,
            constraints=constraints,
            max_candidates=max_candidates,
        )
        return candidates

    @staticmethod
    def generate_exhaustive(
        total_laps: int,
        constraints: StrategyConstraints,
        max_candidates: int = 200,
    ) -> list[Strategy]:
        """Generate all mathematically legal strategies up to max_candidates."""
        results: list[Strategy] = []
        compounds = constraints.allowed_compounds
        min_stint = constraints.min_stint_length

        for k_stops in range(constraints.min_stops, constraints.max_stops + 1):
            if k_stops == 0:
                # 0-stop strategies
                for comp in compounds:
                    if constraints.mandatory_two_compounds:
                        continue  # Cannot satisfy 2-compound rule with 0 stops
                    results.append(
                        Strategy(
                            name=f"0-Stop ({comp.value})",
                            initial_compound=comp,
                            pit_stops=[],
                        )
                    )
                    if len(results) >= max_candidates:
                        return results
                continue

            # Generate all valid lap combinations
            valid_lap_tuples = StrategyGenerator._generate_valid_pit_laps(
                total_laps=total_laps,
                num_stops=k_stops,
                min_stint_length=min_stint,
            )

            for laps in valid_lap_tuples:
                # Generate compound sequences of length k_stops + 1
                for comp_seq in itertools.product(compounds, repeat=k_stops + 1):
                    if constraints.mandatory_two_compounds and len(set(comp_seq)) < 2:
                        continue

                    strat_name = (
                        f"{k_stops}-Stop ("
                        + "-".join(c.value[0] for c in comp_seq)
                        + f" @ {','.join(map(str, laps))})"
                    )
                    pit_stops = [
                        PitStopDecision(lap=lap, compound=comp_seq[idx + 1])
                        for idx, lap in enumerate(laps)
                    ]
                    results.append(
                        Strategy(
                            name=strat_name,
                            initial_compound=comp_seq[0],
                            pit_stops=pit_stops,
                        )
                    )
                    if len(results) >= max_candidates:
                        return results

        return results

    @staticmethod
    def generate_heuristic_grid(
        total_laps: int,
        constraints: StrategyConstraints,
        max_candidates: int = 100,
    ) -> list[Strategy]:
        """Generate a curated strategic grid with early, balanced, and late pit windows."""
        results: list[Strategy] = []
        compounds = constraints.allowed_compounds
        min_stint = constraints.min_stint_length

        for k_stops in range(constraints.min_stops, constraints.max_stops + 1):
            if k_stops == 0:
                for comp in compounds:
                    if not constraints.mandatory_two_compounds:
                        results.append(
                            Strategy(
                                name=f"0-Stop ({comp.value})",
                                initial_compound=comp,
                                pit_stops=[],
                            )
                        )
                continue

            # Determine key pit windows
            target_laps_list: list[list[int]] = []
            if k_stops == 1:
                # 1-stop: nominal split at total_laps / 2, with offsets
                mid = total_laps // 2
                offsets = [-6, -3, 0, 3, 6]
                for off in offsets:
                    lap = mid + off
                    if min_stint <= lap <= total_laps - min_stint:
                        target_laps_list.append([lap])
            elif k_stops == 2:
                # 2-stop: nominal splits at 1/3 and 2/3
                third = total_laps / 3.0
                stagger_configs = [
                    (round(third), round(2 * third)),
                    (round(third) - 3, round(2 * third) + 2),
                    (round(third) + 3, round(2 * third) - 2),
                    (round(third) - 4, round(2 * third) - 4),
                ]
                for l1, l2 in stagger_configs:
                    if (
                        l1 >= min_stint
                        and (l2 - l1) >= min_stint
                        and (total_laps - l2) >= min_stint
                    ):
                        target_laps_list.append([l1, l2])
            elif k_stops == 3:
                # 3-stop: quarters
                q = total_laps // 4
                laps = [q, 2 * q, 3 * q]
                if (
                    all(laps[i + 1] - laps[i] >= min_stint for i in range(len(laps) - 1))
                    and laps[0] >= min_stint
                    and total_laps - laps[-1] >= min_stint
                ):
                    target_laps_list.append(laps)

            # Generate compound combinations
            for laps in target_laps_list:
                for comp_seq in itertools.product(compounds, repeat=k_stops + 1):
                    if constraints.mandatory_two_compounds and len(set(comp_seq)) < 2:
                        continue

                    # Filter out nonsensical transitions (e.g. Wet to Wet on Dry)
                    name_code = "-".join(c.value[0] for c in comp_seq)
                    strat_name = f"{k_stops}-Stop ({name_code} @ {','.join(map(str, laps))})"
                    pit_stops = [
                        PitStopDecision(lap=laps[i], compound=comp_seq[i + 1])
                        for i in range(k_stops)
                    ]
                    strat = Strategy(
                        name=strat_name,
                        initial_compound=comp_seq[0],
                        pit_stops=pit_stops,
                    )
                    results.append(strat)
                    if len(results) >= max_candidates:
                        return results

        return results

    @staticmethod
    def _generate_valid_pit_laps(
        total_laps: int,
        num_stops: int,
        min_stint_length: int,
    ) -> list[tuple[int, ...]]:
        """Find all chronologically valid pit stop lap tuples satisfying min stint length."""
        valid_tuples: list[tuple[int, ...]] = []

        def backtrack(current: list[int], last_lap: int, remaining_stops: int) -> None:
            if remaining_stops == 0:
                if (total_laps - last_lap) >= min_stint_length:
                    valid_tuples.append(tuple(current))
                return

            min_next = last_lap + min_stint_length
            max_next = total_laps - (remaining_stops * min_stint_length)

            for next_lap in range(min_next, max_next + 1):
                backtrack(current + [next_lap], next_lap, remaining_stops - 1)

        backtrack([], 0, num_stops)
        return valid_tuples
