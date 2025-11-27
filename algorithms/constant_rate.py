## base line 1

from .base import Algorithm


class ConstantRate(Algorithm):
    def name(self) -> str:
        return "Constant-Rate"

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        rate = self.Q / n
        return min(rate, inventory)