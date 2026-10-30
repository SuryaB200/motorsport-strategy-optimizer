"""Independent, reproducible random number generation source."""

from typing import Optional, Sequence, TypeVar

import numpy as np

T = TypeVar("T")


class RandomSource:
    """Encapsulates a NumPy PCG64 pseudo-random generator without touching global state."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._seed = seed if seed is not None else 42
        self._rng = np.random.default_rng(self._seed)

    @property
    def seed(self) -> int:
        return self._seed

    def uniform(self, low: float = 0.0, high: float = 1.0) -> float:
        """Sample a uniform floating point number in [low, high)."""
        return float(self._rng.uniform(low, high))

    def normal(self, mean: float = 0.0, std_dev: float = 1.0) -> float:
        """Sample a normally distributed float."""
        return float(self._rng.normal(mean, std_dev))

    def bernoulli(self, p: float) -> bool:
        """Sample a Bernoulli trial returning True with probability p."""
        if not (0.0 <= p <= 1.0):
            raise ValueError(f"Bernoulli probability p must be in [0, 1], got {p}")
        return bool(self._rng.uniform(0.0, 1.0) < p)

    def integers(self, low: int, high: int) -> int:
        """Sample a discrete uniform integer in [low, high] inclusive."""
        return int(self._rng.integers(low, high + 1))

    def choice(self, sequence: Sequence[T], probabilities: Optional[Sequence[float]] = None) -> T:
        """Randomly select an element from sequence with optional weights."""
        if probabilities is not None:
            norm_p = np.array(probabilities, dtype=float)
            norm_p /= norm_p.sum()
        else:
            norm_p = None
        idx = int(self._rng.choice(len(sequence), p=norm_p))
        return sequence[idx]

    def spawn(self, count: int) -> list["RandomSource"]:
        """Spawn independent child RandomSource instances using spawned seed sequences."""
        seeds = self._rng.integers(0, 2**31 - 1, size=count)
        return [RandomSource(seed=int(s)) for s in seeds]
