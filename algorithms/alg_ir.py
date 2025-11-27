import numpy as np
from .base import Algorithm


class ALG_IR(Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = self.Q / (1 + np.log(self.theta))

    def name(self) -> str:
        return "ALG-IR"

    def phi(self, y: float) -> float:
        if y < self.threshold:
            return self.m
        exponent = (y * (1 + np.log(self.theta)) / self.Q) - 1
        return self.m * np.exp(exponent)

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        if cumulative < self.threshold:
            exp_demand = self.demand.expected(price)
            max_allowed = self.threshold - cumulative
            retrieval = min(exp_demand, max_allowed, inventory)
        else:
            phi_val = self.phi(cumulative)
            if price <= phi_val:
                retrieval = 0.0
            else:
                exp_demand = self.demand.expected(price)
                retrieval = min(exp_demand * 0.5, inventory)

        if t == n:
            retrieval = inventory

        return retrieval