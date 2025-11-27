##đây là file abstract ( cứ coi như đây là đại cương cho mấy file sau làm theo)
## tưởng tượng cái file này là đại cương phép cộng á
## mấy file khác xài lại phép cộng nhưng mà sẽ cộng theo cách khác nhau, cộng số thực, số ảo, số nguyên ...
## đây khai báo 2 công thức đại cương (class cha ): def name, và def decide, thằng nào sài lại Algorithms đều phải kế thừa 2 hàm đó
## đây là cái khung xương để xây các thuật toán khác
## run() để mô phỏng 1 kịch bản giá
## run(): trừ inventory, tính demand,tính revenue,lưu lịch sử


from abc import ABC, abstractmethod
import numpy as np
from typing import List
from models import AlgorithmResult


class DemandModel:
    def __init__(self, a: float, b: float, delta: float):
        self.a = a
        self.b = b
        self.delta = delta

    def expected(self, price: float) -> float:
        return max(0.0, self.a - self.b * price)

    def actual(self, price: float) -> float:
        base = self.expected(price)
        fluctuation = np.random.uniform(1 - self.delta, 1 + self.delta)
        return base * fluctuation


class Algorithm(ABC):
    def __init__(self, Q: int, m: float, M: float, demand: DemandModel):
        self.Q = Q
        self.m = m
        self.M = M
        self.theta = M / m
        self.demand = demand

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        pass

    def run(self, prices: List[float]) -> AlgorithmResult:
        n = len(prices)
        inventory = float(self.Q)
        cumulative = 0.0

        retrievals = []
        revenues = []
        inventory_levels = [self.Q]

        for t, price in enumerate(prices, start=1):
            retrieval = self.decide(t, n, price, inventory, cumulative)
            retrieval = max(0.0, min(retrieval, inventory))

            demand = self.demand.actual(price)
            sales = min(retrieval, demand)
            revenue = price * sales

            inventory -= retrieval
            cumulative += retrieval

            retrievals.append(retrieval)
            revenues.append(revenue)
            inventory_levels.append(int(inventory))

        return AlgorithmResult(
            name=self.name(),
            total_revenue=sum(revenues),
            retrievals=retrievals,
            revenues=revenues,
            inventory=inventory_levels
        )