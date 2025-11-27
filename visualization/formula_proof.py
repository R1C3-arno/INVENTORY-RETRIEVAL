## Chứng minh công thức --> ra graph

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
from models import AlgorithmResult


def plot_formula_validation(results: Dict[str, AlgorithmResult], prices: list, config, save_path: str):
    alg_ir_result = results.get("ALG-IR")
    if not alg_ir_result:
        return

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Chart 1: Reservation Price Evolution (Formula 8)
    ax1 = axes[0, 0]
    cumulative = [0]
    for r in alg_ir_result.retrievals:
        cumulative.append(cumulative[-1] + r)

    phi_values = []
    threshold = config.threshold
    for y in cumulative[:-1]:
        if y < threshold:
            phi_values.append(config.m)
        else:
            exponent = (y * (1 + np.log(config.theta)) / config.Q) - 1
            phi_values.append(config.m * np.exp(exponent))

    periods = range(1, len(prices) + 1)
    ax1.plot(periods, phi_values, 'r-', linewidth=3, label='φ(y) - Reservation Price')
    ax1.plot(periods, prices, 'b--', linewidth=2, alpha=0.7, label='Market Price')
    ax1.axhline(y=config.m, color='green', linestyle=':', label=f'm = {config.m}')
    ax1.axhline(y=config.M, color='orange', linestyle=':', label=f'M = {config.M}')
    ax1.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
    ax1.set_title('Formula 8: Reservation Price φ(y) Evolution', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Chart 2: Decision Rule (Formula 11)
    ax2 = axes[0, 1]
    decisions = ['SELL' if r > 0 else 'HOLD' for r in alg_ir_result.retrievals]
    colors = ['green' if d == 'SELL' else 'red' for d in decisions]
    ax2.bar(periods, [1] * len(periods), color=colors, alpha=0.7)
    ax2.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Decision', fontsize=12, fontweight='bold')
    ax2.set_title('Formula 11: Decision Rule (SELL vs HOLD)', fontsize=14, fontweight='bold')
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['', ''])
    ax2.grid(True, alpha=0.3, axis='x')

    # Chart 3: Two-Stage Visualization
    ax3 = axes[1, 0]
    inventory = alg_ir_result.inventory[:-1]
    stage_1_inv = threshold

    ax3.fill_between(periods, 0, inventory, alpha=0.3, color='blue', label='Current Inventory')
    ax3.plot(periods, inventory, 'b-', linewidth=2)
    ax3.axhline(y=config.Q - threshold, color='red', linestyle='--', linewidth=2,
                label=f'Stage Transition (y={threshold:.0f})')
    ax3.fill_between(periods, config.Q - threshold, config.Q, alpha=0.2, color='green',
                     label='Stage 1: Abundant')
    ax3.fill_between(periods, 0, config.Q - threshold, alpha=0.2, color='orange',
                     label='Stage 2: Scarce')
    ax3.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Inventory Level', fontsize=12, fontweight='bold')
    ax3.set_title('Two-Stage Strategy Visualization', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Chart 4: Retrieval vs Price
    ax4 = axes[1, 1]
    ax4.scatter(prices, alg_ir_result.retrievals, c=colors, s=100, alpha=0.7)
    ax4.plot(prices, alg_ir_result.retrievals, 'k--', alpha=0.3)
    ax4.set_xlabel('Market Price ($)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Retrieval Quantity', fontsize=12, fontweight='bold')
    ax4.set_title('Price vs Retrieval Decision', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {save_path}")