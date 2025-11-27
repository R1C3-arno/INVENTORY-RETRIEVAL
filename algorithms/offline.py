from typing import List
from algorithms.base import Algorithm
from models import AlgorithmResult


class Offline(Algorithm):
    def name(self) -> str:
        return "Offline"

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        raise NotImplementedError()

    def run(self, prices: List[float]) -> AlgorithmResult:
        indexed = list(enumerate(prices))
        sorted_prices = sorted(indexed, key=lambda x: -x[1])

        allocations = [0.0] * len(prices)
        remaining = float(self.Q)

        for idx, price in sorted_prices:
            if remaining <= 0:
                break
            exp_demand = self.demand.expected(price)
            alloc = min(exp_demand, remaining)
            allocations[idx] = alloc
            remaining -= alloc

        retrievals = []
        revenues = []
        inventory_levels = [self.Q]
        cumulative = 0.0

        for price, alloc in zip(prices, allocations):
            demand = self.demand.actual(price)
            sales = min(alloc, demand)
            revenue = price * sales

            cumulative += alloc
            retrievals.append(alloc)
            revenues.append(revenue)
            inventory_levels.append(int(self.Q - cumulative))

        return AlgorithmResult(
            name=self.name(),
            total_revenue=sum(revenues),
            retrievals=retrievals,
            revenues=revenues,
            inventory=inventory_levels
        )