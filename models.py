from dataclasses import dataclass
from typing import List


@dataclass
class AlgorithmResult:
    name: str
    total_revenue: float
    retrievals: List[float]
    revenues: List[float]
    inventory: List[int]

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