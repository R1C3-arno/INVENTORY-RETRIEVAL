from dataclasses import dataclass
from typing import List, Dict


@dataclass
class AlgorithmResult:
    def __init__(self, name, total_revenue, retrievals, revenues, inventory, period_logs=None):
        self.name = name
        self.total_revenue = total_revenue
        self.retrievals = retrievals
        self.revenues = revenues
        self.inventory = inventory
        self.period_logs = period_logs or []

    @property
    def avg_retrieval(self) -> float:
        return sum(self.retrievals) / len(self.retrievals)


@dataclass
class BatchResult:
    name: str
    revenues: List[float]

    @property
    def mean(self) -> float:
        return sum(self.revenues) / len(self.revenues)

    @property
    def std(self) -> float:
        import numpy as np
        return float(np.std(self.revenues))