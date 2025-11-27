## phân tích chi tiết từng số liệu theo nhiều graph khác nhau

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
from models import AlgorithmResult


def plot_detailed_analysis(results: Dict[str, AlgorithmResult], prices: list, save_path: str):
    fig, axes = plt.subplots(3, 2, figsize=(16, 18))

    periods = range(1, len(prices) + 1)

    # Chart 1: Cumulative Revenue
    ax1 = axes[0, 0]
    for name, result in results.items():
        cumulative = np.cumsum(result.revenues)
        ax1.plot(periods, cumulative, marker='o', linewidth=2, label=name, markersize=4)
    ax1.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Cumulative Revenue ($)', fontsize=12, fontweight='bold')
    ax1.set_title('Cumulative Revenue Over Time', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Chart 2: Inventory Levels
    ax2 = axes[0, 1]
    for name, result in results.items():
        ax2.plot(range(len(result.inventory)), result.inventory,
                 marker='s', linewidth=2, label=name, markersize=4)
    ax2.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Remaining Inventory', fontsize=12, fontweight='bold')
    ax2.set_title('Inventory Depletion', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Chart 3: Price Sequence
    ax3 = axes[1, 0]
    ax3.bar(periods, prices, color='steelblue', alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Market Price ($)', fontsize=12, fontweight='bold')
    ax3.set_title('Market Price Sequence', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    # Chart 4: Retrieval Comparison
    ax4 = axes[1, 1]
    key_algs = ["ALG-IR", "Myopic", "Offline"]
    width = 0.25
    x = np.array(list(periods))

    for i, alg_name in enumerate(key_algs):
        if alg_name in results:
            offset = (i - 1) * width
            ax4.bar(x + offset, results[alg_name].retrievals, width,
                    label=alg_name, alpha=0.8, edgecolor='black')

    ax4.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Retrieval Quantity', fontsize=12, fontweight='bold')
    ax4.set_title('Retrieval Decisions Comparison', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')

    # Chart 5: Period Revenue Heatmap
    ax5 = axes[2, 0]
    revenue_matrix = np.array([results[name].revenues for name in results.keys()])
    im = ax5.imshow(revenue_matrix, aspect='auto', cmap='YlOrRd')
    ax5.set_yticks(range(len(results)))
    ax5.set_yticklabels(results.keys())
    ax5.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax5.set_title('Revenue Heatmap by Period', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax5, label='Revenue ($)')

    # Chart 6: Final Summary Table
    ax6 = axes[2, 1]
    ax6.axis('off')

    summary_data = []
    for name, result in sorted(results.items(), key=lambda x: -x[1].total_revenue):
        summary_data.append([
            name,
            f"${result.total_revenue:,.0f}",
            f"{result.avg_retrieval:.1f}",
            f"{result.inventory[-1]}"
        ])

    table = ax6.table(cellText=summary_data,
                      colLabels=['Algorithm', 'Total Revenue', 'Avg Retrieval', 'Final Inv'],
                      cellLoc='center',
                      loc='center',
                      bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    for i in range(len(summary_data) + 1):
        if i == 0:
            table[(i, 0)].set_facecolor('#4CAF50')
            table[(i, 1)].set_facecolor('#4CAF50')
            table[(i, 2)].set_facecolor('#4CAF50')
            table[(i, 3)].set_facecolor('#4CAF50')
        else:
            color = plt.cm.viridis(i / len(summary_data))
            for j in range(4):
                table[(i, j)].set_facecolor(color)

    ax6.set_title('Summary Statistics', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {save_path}")