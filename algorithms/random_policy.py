##base line 3

import numpy as np
from .base import Algorithm


class RandomPolicy(Algorithm):
    def name(self) -> str:
        return "Random"

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        return np.random.uniform(0, 0.3) * inventory