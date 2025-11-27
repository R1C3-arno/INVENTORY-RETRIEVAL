import numpy as np
from typing import List, Dict


class ScenarioGenerator:
    def __init__(self, m: float, M: float):
        self.m = m
        self.M = M

    def random_uniform(self, n: int, seed: int = None) -> List[float]:
        if seed is not None:
            np.random.seed(seed)
        return np.random.uniform(self.m, self.M, n).tolist()

    def trending(self, n: int, trend: str = "increasing", noise: float = 0.1) -> List[float]:
        base = np.linspace(self.m, self.M, n)

        if trend == "decreasing":
            base = base[::-1]
        elif trend == "cyclic":
            base = (self.M + self.m) / 2 + (self.M - self.m) / 2 * np.sin(np.linspace(0, 4 * np.pi, n))

        noise_vals = np.random.uniform(-noise * (self.M - self.m),
                                       noise * (self.M - self.m), n)
        return np.clip(base + noise_vals, self.m, self.M).tolist()

    def extreme_volatility(self, n: int) -> List[float]:
        prices = []
        for _ in range(n):
            if np.random.random() < 0.5:
                prices.append(np.random.uniform(self.m, self.m + (self.M - self.m) * 0.3))
            else:
                prices.append(np.random.uniform(self.M - (self.M - self.m) * 0.3, self.M))
        return prices

    def realistic_market(self, n: int, initial_price: float = None) -> List[float]:
        if initial_price is None:
            initial_price = (self.m + self.M) / 2

        prices = [initial_price]
        volatility = 0.1

        for _ in range(n - 1):
            change = np.random.normal(0, volatility * prices[-1])
            new_price = prices[-1] + change
            new_price = np.clip(new_price, self.m, self.M)
            prices.append(new_price)

        return prices

    def generate_batch(self, n: int, num_scenarios: int, strategy: str = "random") -> List[List[float]]:
        scenarios = []
        for _ in range(num_scenarios):
            if strategy == "random":
                scenarios.append(self.random_uniform(n))
            elif strategy == "trending":
                trend = np.random.choice(["increasing", "decreasing", "cyclic"])
                scenarios.append(self.trending(n, trend))
            elif strategy == "mixed":
                if np.random.random() < 0.5:
                    scenarios.append(self.random_uniform(n))
                else:
                    scenarios.append(self.realistic_market(n))
        return scenarios