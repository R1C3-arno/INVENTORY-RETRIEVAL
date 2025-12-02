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

from scipy.stats import truncnorm, uniform


class DemandModel:
    def __init__(self, a, b, delta, distribution="uniform", sigma=0.15):
        self.a = a
        self.b = b
        self.delta = delta
        self.distribution = distribution
        self.sigma = sigma

        # Support: [1-Δ, 1+Δ]
        self.lower = 1 - delta
        self.upper = 1 + delta

        if distribution == "uniform":
            self.dist = uniform(loc=self.lower, scale=2 * delta)
            self.truncnorm = None

        elif distribution == "truncnorm":
            a_, b_ = (self.lower - 1) / sigma, (self.upper - 1) / sigma
            self.truncnorm = truncnorm(a_, b_, loc=1, scale=sigma)
            self.dist = None

        else:
            raise ValueError("distribution must be 'uniform' or 'truncnorm'")

    def expected(self, price: float) -> float:
        return max(0.0, self.a - self.b * price)

    # ✅ HÀM DEMAND THỰC TẾ (uniform hoặc truncnorm)
    def actual(self, price: float) -> float:
        base = self.expected(price)

        if self.distribution == "truncnorm":
            fluctuation = self.truncnorm.rvs()
        else:
            fluctuation = self.dist.rvs()

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
        period_logs = []  #
        total_revenue = 0.0
        total_holding_cost = 0.0

        for t, price in enumerate(prices, start=1):
            inventory_before = inventory

            # 1. Quyết định lấy bao nhiêu
            retrieval = self.decide(t, n, price, inventory, cumulative)
            retrieval = max(0.0, min(retrieval, inventory))

            # 2. Demand
            base_demand = self.demand.expected(price)

            if self.demand.distribution == "truncnorm":
                fluctuation = self.demand.truncnorm.rvs()
            else:
                fluctuation = self.demand.dist.rvs()

            actual_demand = base_demand * fluctuation

            # 3. Sales & revenue
            sales = min(retrieval, actual_demand)
            revenue = price * sales

            # 4. Holding cost
            inventory_after = inventory - retrieval
            holding_cost = inventory_after * 0.0  #  nếu chưa có h thì để 0, hoặc truyền h vào

            # 5. Update trạng thái
            inventory = inventory_after
            cumulative += retrieval
            total_revenue += revenue
            total_holding_cost += holding_cost

            retrievals.append(retrieval)
            revenues.append(revenue)
            inventory_levels.append(inventory_after)

            #  6. GHI LOG ĐẦY ĐỦ CHO PDF
            period_logs.append({
                "Period": t,
                "Price": price,
                "Inventory": inventory_before,
                "Retrieval": retrieval,
                "Delta": fluctuation,
                "Demand": actual_demand,
                "Sales": sales,
                "Revenue": revenue,
                "HoldingCost": holding_cost,
                "Remaining": inventory_after
            })

        return AlgorithmResult(
            name=self.name(),
            total_revenue=total_revenue,
            retrievals=retrievals,
            revenues=revenues,
            inventory=inventory_levels,
            period_logs=period_logs
        )
