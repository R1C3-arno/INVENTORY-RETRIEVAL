import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class SimulationConfig:
    Q: int
    m: float
    M: float
    n: int
    a: float
    b: float
    delta: float
    h: float
    num_scenarios: int

    demand_dist: str = "uniform"
    sigma: float = 0.15

    @property
    def theta(self) -> float:
        import numpy as np
        return self.M / self.m

    @property
    def threshold(self) -> float:
        import numpy as np
        return self.Q / (1 + np.log(self.theta))


class ConfigLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

    def load_default_config(self) -> SimulationConfig:
        config_file = self.data_dir / "default_config.json"
        with open(config_file, 'r') as f:
            data = json.load(f)

        sim_params = data["simulation"]

        # Log: Fallback an toàn
        sim_params.setdefault("demand_dist", "uniform")
        sim_params.setdefault("sigma", 0.15)

        return SimulationConfig(**sim_params)

    def load_scenario(self, scenario_name: str) -> SimulationConfig:
        scenarios_file = self.data_dir / "test_scenarios.json"
        with open(scenarios_file, 'r') as f:
            data = json.load(f)

        for scenario in data["scenarios"]:
            if scenario["name"] == scenario_name:
                return SimulationConfig(**scenario["params"])

        raise ValueError(f"Scenario not found: {scenario_name}")

    def load_fixed_prices(self, sequence_name: str) -> list[float]:
        scenarios_file = self.data_dir / "test_scenarios.json"
        with open(scenarios_file, 'r') as f:
            data = json.load(f)

        if sequence_name not in data["fixed_price_sequences"]:
            raise ValueError(f"Price sequence not found: {sequence_name}")

        return data["fixed_price_sequences"][sequence_name]

    def load_stores(self) -> list[Dict[str, Any]]:
        stores_file = self.data_dir / "vietnam_stores.json"
        with open(stores_file, 'r') as f:
            data = json.load(f)
        return data["stores"]

    def load_benchmark_cases(self) -> list[Dict[str, Any]]:
        benchmark_file = self.data_dir / "benchmark_cases.json"
        with open(benchmark_file, 'r') as f:
            data = json.load(f)
        return data["test_cases"]

    def get_available_scenarios(self) -> list[str]:
        scenarios_file = self.data_dir / "test_scenarios.json"
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        return [s["name"] for s in data["scenarios"]]