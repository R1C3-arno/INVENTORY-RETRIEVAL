from .base import Algorithm


class Myopic(Algorithm):
    def name(self) -> str:
        return "Myopic"

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        exp_demand = self.demand.expected(price)
        return min(exp_demand * 1.2, inventory)