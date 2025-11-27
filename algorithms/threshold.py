##base line 2

from .base import Algorithm


class FixedThreshold(Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price_threshold = (self.m + self.M) / 2

    def name(self) -> str:
        return "Fixed-Threshold"

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        if price < self.price_threshold:
            return 0.0
        exp_demand = self.demand.expected(price)
        return min(exp_demand, inventory)