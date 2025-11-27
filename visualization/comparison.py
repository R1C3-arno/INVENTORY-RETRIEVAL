## so sánh giữa các thuật toán



import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
from models import BatchResult


def plot_algorithm_comparison(batch_results: Dict[str, BatchResult], save_path: str):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    sorted_results = sorted(batch_results.items(), key=lambda x: -x[1].mean)
    names = [name for name, _ in sorted_results]
    means = [result.mean for _, result in sorted_results]

    offline_mean = batch_results["Offline"].mean
    ratios = [mean / offline_mean for mean in means]

    # Chart 1: Revenue Bar Chart
    ax1 = axes[0, 0]
    colors = plt.cm.viridis(np.linspace(0, 1, len(names)))
    bars = ax1.bar(names, means, color=colors, edgecolor='black', linewidth=1.2)

    for bar, mean in zip(bars, means):
        height = bar.get_height()
        ax1.annotate(f'${mean:,.0f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax1.set_ylabel('Mean Revenue ($)', fontsize=12, fontweight='bold')
    ax1.set_title('Mean Revenue Comparison', fontsize=14, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3, axis='y')

    # Chart 2: Competitive Ratio
    ax2 = axes[0, 1]
    bars = ax2.bar(names, ratios, color=colors, edgecolor='black', linewidth=1.2)
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Optimal')

    for bar, ratio in zip(bars, ratios):
        height = bar.get_height()
        ax2.annotate(f'{ratio:.3f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax2.set_ylabel('Competitive Ratio', fontsize=12, fontweight='bold')
    ax2.set_title('Competitive Ratio (Revenue / Offline)', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # Chart 3: Revenue Distribution Box Plot
    ax3 = axes[1, 0]
    data = [batch_results[name].revenues for name in names]
    bp = ax3.boxplot(data, labels=names, patch_artist=True)

    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax3.set_ylabel('Revenue ($)', fontsize=12, fontweight='bold')
    ax3.set_title('Revenue Distribution', fontsize=14, fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3, axis='y')

    # Chart 4: Standard Deviation
    ax4 = axes[1, 1]
    stds = [batch_results[name].std for name in names]
    bars = ax4.bar(names, stds, color=colors, edgecolor='black', linewidth=1.2)

    ax4.set_ylabel('Standard Deviation ($)', fontsize=12, fontweight='bold')
    ax4.set_title('Revenue Stability (Lower is Better)', fontsize=14, fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {save_path}")