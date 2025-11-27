import numpy as np
from .base import Algorithm


class ALG_IR_H(Algorithm):
    def __init__(self, Q, m, M, demand, h: float):
        super().__init__(Q, m, M, demand)
        self.h = h

    def name(self) -> str:
        return "ALG-IR-H"

    def phi_h(self, y: float, t: int, n: int) -> float:
        remaining = n - t
        m_t = self.m - remaining * self.h
        M_t = self.M - remaining * self.h

        if M_t <= m_t or m_t <= 0:
            return self.m

        theta_t = M_t / m_t
        threshold_t = self.Q / (1 + np.log(theta_t))

        if y < threshold_t:
            return m_t

        exponent = (y * (1 + np.log(theta_t)) / self.Q) - 1
        return m_t * np.exp(exponent)

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        remaining = n - t
        m_t = self.m - remaining * self.h
        M_t = self.M - remaining * self.h

        if M_t <= m_t or m_t <= 0:
            return inventory

        theta_t = M_t / m_t
        threshold_t = self.Q / (1 + np.log(theta_t))

        if cumulative < threshold_t:
            exp_demand = self.demand.expected(price)
            retrieval = min(exp_demand, inventory)
        else:
            phi_val = self.phi_h(cumulative, t, n)
            if price <= phi_val:
                retrieval = 0.0
            else:
                exp_demand = self.demand.expected(price)
                retrieval = min(exp_demand * 0.5, inventory)

        if t == n:
            retrieval = inventory

        return retrieval