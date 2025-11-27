from dataclasses import dataclass
import numpy as np


@dataclass
class Config:
    Q: int
    m: float
    M: float
    n: int
    a: float
    b: float
    delta: float
    h: float
    num_scenarios: int

    @property
    def theta(self) -> float:
        return self.M / self.m

    @property
    def threshold(self) -> float:
        return self.Q / (1 + np.log(self.theta))


OUTPUT_DIR = "output"