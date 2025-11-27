import os
import argparse
import numpy as np
from pathlib import Path

from config import OUTPUT_DIR
from fixtures.config_loader import ConfigLoader
from fixtures.scenario_generator import ScenarioGenerator
from fixtures.data_validator import DataValidator

from algorithms.base import DemandModel
from algorithms.alg_ir import ALG_IR
from algorithms.alg_ir_h import ALG_IR_H
from algorithms.myopic import Myopic
from algorithms.offline import Offline
from algorithms.constant_rate import ConstantRate
from algorithms.threshold import FixedThreshold
from algorithms.random_policy import RandomPolicy

from runner import SimulationRunner
from visualization.formula_proof import plot_formula_validation
from visualization.comparison import plot_algorithm_comparison
from visualization.detailed_analysis import plot_detailed_analysis


def main():
    parser = argparse.ArgumentParser(description="Inventory Retrieval Simulation")
    parser.add_argument("--config", type=str, default=None, help="Config file or scenario name")
    parser.add_argument("--prices", type=str, default=None, help="Fixed price sequence name")
    parser.add_argument("--list-scenarios", action="store_true", help="List available scenarios")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    parser.add_argument("--Q", type=int, help="Override Q")
    parser.add_argument("--m", type=float, help="Override m")
    parser.add_argument("--M", type=float, help="Override M")
    parser.add_argument("--n", type=int, help="Override n")
    parser.add_argument("--scenarios", type=int, help="Override num_scenarios")

    args = parser.parse_args()

    loader = ConfigLoader()

    if args.list_scenarios:
        print("Available scenarios:")
        for scenario in loader.get_available_scenarios():
            print(f"  - {scenario}")
        return

    if args.config:
        print(f"Loading scenario: {args.config}")
        config = loader.load_scenario(args.config)
    else:
        print("Loading default configuration")
        config = loader.load_default_config()

    if args.Q:
        config.Q = args.Q
    if args.m:
        config.m = args.m
    if args.M:
        config.M = args.M
    if args.n:
        config.n = args.n
    if args.scenarios:
        config.num_scenarios = args.scenarios

    validator = DataValidator()
    validation = validator.validate_config(config)
    if not validation.is_valid:
        print("❌ Configuration errors:")
        for error in validation.errors:
            print(f"  - {error}")
        return

    np.random.seed(args.seed)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("INVENTORY RETRIEVAL SIMULATION")
    print("=" * 60)
    print(f"Config: Q={config.Q}, m={config.m}, M={config.M}, n={config.n}")
    print(f"θ = {config.theta:.2f}, Threshold = {config.threshold:.0f}")
    print(f"Scenarios: {config.num_scenarios}")
    print("=" * 60)

    demand = DemandModel(config.a, config.b, config.delta)

    algorithms = [
        ALG_IR(config.Q, config.m, config.M, demand),
        ALG_IR_H(config.Q, config.m, config.M, demand, config.h),
        Myopic(config.Q, config.m, config.M, demand),
        Offline(config.Q, config.m, config.M, demand),
        ConstantRate(config.Q, config.m, config.M, demand),
        FixedThreshold(config.Q, config.m, config.M, demand),
        RandomPolicy(config.Q, config.m, config.M, demand)
    ]

    runner = SimulationRunner(config)

    print("\n[1/3] Running single simulation...")
    if args.prices:
        print(f"Using fixed price sequence: {args.prices}")
        prices = loader.load_fixed_prices(args.prices)
        single_results = {}
        for alg in algorithms:
            result = alg.run(prices)
            single_results[alg.name()] = result
    else:
        single_results, prices = runner.run_single(algorithms)

    print("\n[2/3] Running batch simulation...")
    batch_results = runner.run_batch(algorithms)

    print("\n[3/3] Generating visualizations...")
    plot_formula_validation(single_results, prices, config, f"{OUTPUT_DIR}/01_formula_proof.png")
    plot_algorithm_comparison(batch_results, f"{OUTPUT_DIR}/02_comparison.png")
    plot_detailed_analysis(single_results, prices, f"{OUTPUT_DIR}/03_detailed_analysis.png")

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    sorted_batch = sorted(batch_results.items(), key=lambda x: -x[1].mean)
    offline_mean = batch_results["Offline"].mean

    print(f"{'Algorithm':<20} {'Mean Revenue':>15} {'Std Dev':>12} {'CR':>8}")
    print("-" * 60)
    for name, result in sorted_batch:
        cr = result.mean / offline_mean
        print(f"{name:<20} ${result.mean:>14,.0f} ${result.std:>11,.0f} {cr:>7.3f}")

    print("\n" + "=" * 60)
    print(f"Charts saved in: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()