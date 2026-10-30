"""Monte Carlo Tree Search (MCTS) for sequential pit-stop and tire strategy optimization."""

import math
from dataclasses import dataclass, field
from typing import Optional

from app.schemas.race import RaceConfig, TireCompound
from app.schemas.strategy import PitStopDecision, Strategy, StrategyConstraints
from app.services.race_simulator import RaceSimulator
from app.services.random_source import RandomSource


@dataclass(frozen=True)
class MCTSAction:
    """Action taken at the end of a lap."""

    is_pit: bool
    compound: Optional[TireCompound] = None  # None if is_pit is False

    def __str__(self) -> str:
        if self.is_pit and self.compound:
            return f"PIT({self.compound.value})"
        return "STAY"


@dataclass
class MCTSNode:
    """Search tree node representing a race state."""

    lap: int
    compound: TireCompound
    tire_age: int
    stops_taken: int
    parent: Optional["MCTSNode"] = None
    action_from_parent: Optional[MCTSAction] = None
    children: list["MCTSNode"] = field(default_factory=list)
    unexplored_actions: list[MCTSAction] = field(default_factory=list)
    visits: int = 0
    total_reward: float = 0.0
    accumulated_race_time: float = 0.0

    @property
    def q_value(self) -> float:
        """Average reward."""
        return self.total_reward / self.visits if self.visits > 0 else 0.0

    @property
    def average_race_time(self) -> float:
        """Average race time from rollouts passing through this node."""
        return self.accumulated_race_time / self.visits if self.visits > 0 else 0.0

    def is_fully_expanded(self) -> bool:
        return len(self.unexplored_actions) == 0

    def is_terminal(self, total_laps: int) -> bool:
        return self.lap >= total_laps


class MCTSEngine:
    """Upper Confidence Bounds for Trees (UCT) strategic pit optimizer."""

    def __init__(
        self,
        config: RaceConfig,
        constraints: StrategyConstraints,
        exploration_constant: float = 1.414,
    ) -> None:
        self.config = config
        self.constraints = constraints
        self.c = exploration_constant

        # Reference bounds for normalizing race time into [0, 1] reward
        # Theoretical best: all laps at baseline on fresh softs with no SC
        # Theoretical worst: heavy degradation or wrong tires
        self.t_ref_best = config.total_laps * (config.baseline_lap_time - 1.0)
        self.t_ref_worst = config.total_laps * (config.baseline_lap_time + 25.0)

    def search(
        self,
        initial_compound: TireCompound,
        iterations: int,
        random_source: RandomSource,
    ) -> Strategy:
        """Execute MCTS search starting from lap 1 with initial_compound.

        Args:
            initial_compound: Fitted tire compound at race start.
            iterations: Number of MCTS simulation iterations (budget).
            random_source: Independent PRNG.

        Returns:
            Recommended Strategy derived from the most visited search trajectory.
        """
        root = MCTSNode(
            lap=1,
            compound=initial_compound,
            tire_age=0,
            stops_taken=0,
        )
        root.unexplored_actions = self._get_legal_actions(root)

        for _ in range(iterations):
            # 1. Selection
            node = self._select(root)

            # 2. Expansion
            if not node.is_terminal(self.config.total_laps) and not node.is_fully_expanded():
                node = self._expand(node)

            # 3. Rollout / Simulation
            race_time = self._rollout(node, random_source)

            # 4. Backpropagation
            reward = self._calculate_reward(race_time)
            self._backpropagate(node, reward, race_time)

        # 5. Extract best strategy following robust child (most visited)
        return self._extract_strategy(root, initial_compound)

    def _get_legal_actions(self, node: MCTSNode) -> list[MCTSAction]:
        """Determine legal actions from the current node state."""
        if node.lap >= self.config.total_laps:
            return []

        actions: list[MCTSAction] = []
        laps_remaining = self.config.total_laps - node.lap
        current_stint_len = node.tire_age + 1

        # Can stay if we don't violate minimum required stops in the future
        min_stops_needed = max(0, self.constraints.min_stops - node.stops_taken)
        max_possible_future_stops = laps_remaining // self.constraints.min_stint_length

        if max_possible_future_stops >= min_stops_needed:
            actions.append(MCTSAction(is_pit=False))

        # Can pit if stint meets min_stint_length and stops_taken < max_stops
        can_pit = (
            current_stint_len >= self.constraints.min_stint_length
            and node.stops_taken < self.constraints.max_stops
            and laps_remaining >= self.constraints.min_stint_length
        )

        if can_pit:
            for compound in self.constraints.allowed_compounds:
                actions.append(MCTSAction(is_pit=True, compound=compound))

        # Fallback if no actions generated (e.g. edge constraint): stay
        if not actions:
            actions.append(MCTSAction(is_pit=False))

        return actions

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Traverse tree using UCT selection until an unexpanded or terminal node is reached."""
        current = node
        while not current.is_terminal(self.config.total_laps) and current.is_fully_expanded():
            if not current.children:
                break
            current = self._best_uct_child(current)
        return current

    def _best_uct_child(self, node: MCTSNode) -> MCTSNode:
        """Select child with maximum UCT score."""
        best_score = -float("inf")
        best_child = node.children[0]
        log_n = math.log(max(1, node.visits))

        for child in node.children:
            if child.visits == 0:
                return child
            exploitation = child.total_reward / child.visits
            exploration = self.c * math.sqrt(log_n / child.visits)
            uct_score = exploitation + exploration

            if uct_score > best_score:
                best_score = uct_score
                best_child = child

        return best_child

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand one unexplored legal action from node."""
        action = node.unexplored_actions.pop(0)

        if action.is_pit and action.compound:
            next_compound = action.compound
            next_age = 0
            next_stops = node.stops_taken + 1
        else:
            next_compound = node.compound
            next_age = node.tire_age + 1
            next_stops = node.stops_taken

        child = MCTSNode(
            lap=node.lap + 1,
            compound=next_compound,
            tire_age=next_age,
            stops_taken=next_stops,
            parent=node,
            action_from_parent=action,
        )
        child.unexplored_actions = self._get_legal_actions(child)
        node.children.append(child)
        return child

    def _rollout(self, node: MCTSNode, random_source: RandomSource) -> float:
        """Simulate a complete continuation of the race from node to finish."""
        # Construct the partial strategy taken from root to this node
        pit_stops: list[PitStopDecision] = []
        curr = node
        while curr.parent is not None:
            if (
                curr.action_from_parent
                and curr.action_from_parent.is_pit
                and curr.action_from_parent.compound
            ):
                # The pit stop occurred at the end of parent's lap
                pit_stops.append(
                    PitStopDecision(lap=curr.parent.lap, compound=curr.action_from_parent.compound)
                )
            curr = curr.parent

        pit_stops.reverse()

        # Complete strategy from node.lap to total_laps using heuristic rule
        sim_curr_lap = node.lap
        sim_age = node.tire_age
        sim_stops = node.stops_taken
        sim_compound = node.compound

        while sim_curr_lap < self.config.total_laps:
            laps_remaining = self.config.total_laps - sim_curr_lap
            stint_len = sim_age + 1

            # Pit decision heuristic: pit if tire heavily degraded and rules permit
            should_pit = (
                sim_stops < self.constraints.max_stops
                and stint_len >= self.constraints.min_stint_length
                and laps_remaining >= self.constraints.min_stint_length
                and (stint_len >= 18 or sim_stops < self.constraints.min_stops)
            )

            if should_pit:
                # Select best available alternative compound
                next_comp = (
                    TireCompound.HARD
                    if sim_compound != TireCompound.HARD
                    and TireCompound.HARD in self.constraints.allowed_compounds
                    else TireCompound.MEDIUM
                )
                pit_stops.append(PitStopDecision(lap=sim_curr_lap, compound=next_comp))
                sim_stops += 1
                sim_age = 0
                sim_compound = next_comp
            else:
                sim_age += 1

            sim_curr_lap += 1

        # Simulate complete strategy
        strat = Strategy(
            name="MCTS Rollout",
            initial_compound=curr.compound,
            pit_stops=pit_stops,
        )
        sim_result = RaceSimulator.simulate(
            config=self.config,
            strategy=strat,
            random_source=random_source,
            record_telemetry=False,
        )
        return sim_result.total_race_time

    def _calculate_reward(self, race_time: float) -> float:
        """Map total race time to normalized reward [0, 1] where lower time = higher reward."""
        if self.t_ref_worst <= self.t_ref_best:
            return 0.5
        normalized = (self.t_ref_worst - race_time) / (self.t_ref_worst - self.t_ref_best)
        return max(0.0, min(1.0, normalized))

    def _backpropagate(self, node: MCTSNode, reward: float, race_time: float) -> None:
        """Propagate reward and visit count up to root."""
        curr: Optional[MCTSNode] = node
        while curr is not None:
            curr.visits += 1
            curr.total_reward += reward
            curr.accumulated_race_time += race_time
            curr = curr.parent

    def _extract_strategy(self, root: MCTSNode, initial_compound: TireCompound) -> Strategy:
        """Extract strategy following the most visited path from root."""
        pit_stops: list[PitStopDecision] = []
        curr = root

        while curr.children:
            # Pick most visited child
            best_child = max(curr.children, key=lambda c: c.visits)
            if (
                best_child.action_from_parent
                and best_child.action_from_parent.is_pit
                and best_child.action_from_parent.compound
            ):
                pit_stops.append(
                    PitStopDecision(lap=curr.lap, compound=best_child.action_from_parent.compound)
                )
            curr = best_child

        # Sort pit stops chronologically and eliminate duplicate laps if any
        pit_stops = sorted({ps.lap: ps for ps in pit_stops}.values(), key=lambda ps: ps.lap)

        return Strategy(
            name=f"MCTS Recommended ({len(pit_stops)}-Stop)",
            initial_compound=initial_compound,
            pit_stops=pit_stops,
        )
