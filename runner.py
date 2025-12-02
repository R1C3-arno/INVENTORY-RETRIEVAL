import numpy as np
from typing import List, Dict
from tqdm import tqdm

from models import AlgorithmResult, BatchResult
from algorithms.base import Algorithm, DemandModel


class SimulationRunner:
    def __init__(self, config):
        self.config = config


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

    def run_verbose_single(self, algorithm: Algorithm):
        """Print detailed  for PDF export"""
        from colorama import Fore, Style, init
        init(autoreset=True)

        prices = self.generate_prices()
        n = len(prices)

        print(f"\n{'=' * 100}")
        print(f"{Fore.CYAN}Log: ALGORITHM: {algorithm.name()}{Style.RESET_ALL}")
        print(f"{'=' * 100}")
        print(f"Initial Inventory: {self.config.Q}")
        print(f"Periods: {n}")
        print(f"Price Range: [{self.config.m}, {self.config.M}]")
        print(f"Holding Cost: h={self.config.h}")
        print(f"{'=' * 100}\n")

        # OFFLINE
        if algorithm.name() == "Offline":
            print(f"{Fore.YELLOW}⚠Log:  Offline algorithm requires all prices upfront.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   Running full simulation instead of period-by-period...{Style.RESET_ALL}\n")

            result = algorithm.run(prices)

            print(f"{'Period':<8}{'Price':<10}{'Retrieval':<12}{'Revenue':<12}")
            print("-" * 50)

            for t, (price, retrieval, revenue) in enumerate(
                    zip(prices, result.retrievals, result.revenues), start=1
            ):
                color = Fore.GREEN if retrieval > 0 else Fore.YELLOW
                print(f"{color}{t:<8}{price:<10.2f}{retrieval:<12.1f}{revenue:<12.2f}{Style.RESET_ALL}")

            print("-" * 50)
            print(f"\n{Fore.CYAN}Log: SUMMARY:{Style.RESET_ALL}")
            print(f"  Total Revenue:        ${result.total_revenue:,.2f}")
            print(f"  Final Inventory:      {result.inventory[-1]}")
            print(f"  Total Retrieved:      {sum(result.retrievals):.1f}")
            print(f"  Utilization Rate:     {(sum(result.retrievals) / self.config.Q) * 100:.1f}%")
            print(f"{'=' * 100}\n")

            #  RETURN DATA FOR PDF
            return {
                "prices": prices,
                "retrievals": result.retrievals,
                "revenues": result.revenues,
                "final_inventory": result.inventory[-1],
                "total_revenue": result.total_revenue,
                "total_holding_cost": 0.0,
                "total_retrieved": sum(result.retrievals),
            }

        #  ONLINE ALGORITHMS
        inventory = float(self.config.Q)
        cumulative = 0.0
        total_revenue = 0.0
        total_holding_cost = 0.0

        print(f"{'Period':<8}{'Price':<10}{'Inventory':<12}{'Retrieval':<12}"
              f"{'δ_t':<10}{'Demand':<12}{'Sales':<10}{'Revenue':<12}{'Hold Cost':<12}{'Remaining':<12}")
        print("-" * 120)

        retrievals = []
        revenues = []

        for t, price in enumerate(prices, start=1):
            retrieval = algorithm.decide(t, n, price, inventory, cumulative)
            retrieval = max(0.0, min(retrieval, inventory))

            base_demand = algorithm.demand.expected(price)

            if algorithm.demand.distribution == "truncnorm":
                fluctuation = algorithm.demand.truncnorm.rvs()
            else:
                fluctuation = algorithm.demand.dist.rvs()

            actual_demand = base_demand * fluctuation

            sales = min(retrieval, actual_demand)
            revenue = price * sales

            remaining_after_retrieval = inventory - retrieval
            holding_cost = remaining_after_retrieval * self.config.h

            inventory -= retrieval
            cumulative += retrieval
            total_revenue += revenue
            total_holding_cost += holding_cost

            retrievals.append(retrieval)
            revenues.append(revenue)

            color = Fore.GREEN if retrieval > 0 else Fore.YELLOW
            print(f"{color}{t:<8}{price:<10.2f}{inventory + retrieval:<12.1f}{retrieval:<12.1f}"
                  f"{fluctuation:<10.3f}{actual_demand:<12.1f}{sales:<10.1f}{revenue:<12.2f}"
                  f"{holding_cost:<12.2f}{inventory:<12.1f}{Style.RESET_ALL}")

        print("-" * 120)
        print(f"\n{Fore.CYAN}Log: SUMMARY:{Style.RESET_ALL}")
        print(f"  Total Revenue:        ${total_revenue:,.2f}")
        print(f"  Total Holding Cost:   ${total_holding_cost:,.2f}")
        print(f"  Net Profit:           ${total_revenue - total_holding_cost:,.2f}")
        print(f"  Final Inventory:      {inventory:.1f}")
        print(f"  Total Retrieved:      {cumulative:.1f}")
        print(f"  Utilization Rate:     {(cumulative / self.config.Q) * 100:.1f}%")
        print(f"{'=' * 100}\n")

        # RETURN DATA FOR PDF
        return {
            "prices": prices,
            "retrievals": retrievals,
            "revenues": revenues,
            "final_inventory": inventory,
            "total_revenue": total_revenue,
            "total_holding_cost": total_holding_cost,
            "total_retrieved": cumulative,
        }
