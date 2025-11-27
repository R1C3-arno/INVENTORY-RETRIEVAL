import numpy as np
from typing import List, Dict
from tqdm import tqdm

from models import AlgorithmResult, BatchResult
from algorithms.base import Algorithm, DemandModel


class SimulationRunner:
    def __init__(self, config):
        self.config = config
        self.demand = DemandModel(config.a, config.b, config.delta)

    def generate_prices(self) -> List[float]:
        return np.random.uniform(self.config.m, self.config.M, self.config.n).tolist()

    def run_single(self, algorithms: List[Algorithm]) -> Dict[str, AlgorithmResult]:
        prices = self.generate_prices()
        results = {}
        for alg in algorithms:
            result = alg.run(prices)
            results[alg.name()] = result
        return results, prices

    def run_batch(self, algorithms: List[Algorithm]) -> Dict[str, BatchResult]:
        batch_results = {alg.name(): [] for alg in algorithms}

        for _ in tqdm(range(self.config.num_scenarios), desc="Running scenarios"):
            prices = self.generate_prices()
            for alg in algorithms:
                result = alg.run(prices)
                batch_results[alg.name()].append(result.total_revenue)

        return {
            name: BatchResult(name=name, revenues=revenues)
            for name, revenues in batch_results.items()
        }