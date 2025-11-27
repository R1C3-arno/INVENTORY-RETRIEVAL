# Inventory Management Simulation - ALG-IR Implementation

Hey there! This is our Inventory Management course project for VNU-IU. We're implementing and testing the ALG-IR algorithm (Online Inventory Retrieval Algorithm) along with a bunch of other strategies to see how they compare.

## What's this all about?

Imagine you have a warehouse full of products (say, 500 units) and you need to sell them over the next few months. The problem is:

- You don't know how long the selling season will last
- Prices keep changing randomly every day
- Higher prices mean fewer customers want to buy
- You can't restock once you start selling

So the question is: when should you sell, and how much?

This project simulates different selling strategies and shows you which ones make the most money. Spoiler alert: the "perfect" strategy (Offline) is impossible in real life because it assumes you know all future prices. But we use it as a benchmark.

## The Math Behind It

The paper we're implementing uses this setup:

- You start with Q units of inventory
- Prices bounce around between m (minimum) and M (maximum)
- When price is high, fewer people buy: demand = a - b * price
- Each period, you decide: sell some, or wait for better prices?

ALG-IR is smart because it uses a two-stage strategy:
- Stage 1 (lots of inventory left): Be aggressive, sell when prices are decent
- Stage 2 (running low): Be defensive, only sell when prices are really good

The cutoff point is Q / (1 + ln(M/m)). Before that threshold, you're in Stage 1. After, you're in Stage 2.

## Setup

You need Python 3.10 or higher.

First, install dependencies:
```bash
pip install -r requirements.txt
```

That's it. No database, no web server, just pure Python.

## Running Simulations

The simplest way:
```bash
python main.py
```

This runs the default scenario (500 units, prices between 50-150, 20 periods, 100 random scenarios).

Want to try specific test cases?
```bash
# See what test cases are available
python main.py --list-scenarios

# Run a specific one
python main.py --config "iPhone 16 - High Volatility"

# Use a fixed price pattern (like always increasing)
python main.py --prices "increasing_trend"

# Override specific parameters
python main.py --Q 1000 --scenarios 500

# Make it reproducible
python main.py --seed 42
```

## What You Get

After running, check the `output/` folder. You'll see three charts:

**1. Formula Proof** (01_formula_proof.png)
Shows that our implementation matches the math from the paper. You'll see:
- How the "reservation price" (minimum acceptable price) increases as you run out of inventory
- When the algorithm decides to SELL vs HOLD
- The two-stage strategy in action

**2. Algorithm Comparison** (02_comparison.png)
Bar charts comparing all strategies:
- Average revenue (higher is better)
- Competitive ratio (how close to the impossible-perfect Offline strategy)
- Revenue distribution (box plots showing consistency)
- Standard deviation (lower means more predictable)

**3. Detailed Analysis** (03_detailed_analysis.png)
Deep dive into what happened:
- Cumulative revenue over time
- How inventory depleted
- Exact prices each period
- Which algorithm sold when
- Period-by-period revenue heatmap
- Final statistics table

## The Algorithms We're Testing

**Offline** - Cheating algorithm that knows all future prices. Impossible in reality but useful as a benchmark. Competitive ratio = 1.0 by definition.

**ALG-IR** - Our main algorithm from the paper. Two-stage strategy with theoretical guarantees. Usually gets CR around 0.85-0.95.

**ALG-IR-H** - Same as ALG-IR but accounts for holding costs (warehousing isn't free). Slightly lower revenue but more realistic.

**Myopic** - Greedy strategy: always sell when price looks good right now. No planning ahead. Simple but often decent.

**Moving-Average** - Only sells when current price is above the recent average. Tries to ride trends.

**Adaptive-Myopic** - Enhanced Myopic that adjusts based on how much time is left and how much inventory you have. More aggressive near the end.

**Percentile-Threshold** - Only sells when price is in the top 25% historically. Conservative approach.

**Early-Aggressive** - Sells 70% of inventory in the first 30% of time. Good for perishable goods or seasonal products.

**Late-Liquidation** - Holds inventory until 70% of time passes, then liquidates aggressively. Bets on prices rising later.

**Optimistic-Threshold** - Risk-seeking: waits for high prices early, accepts lower prices late. High reward but risky.

**Conservative-Threshold** - Risk-averse: accepts decent prices early to ensure coverage. Lower revenue but safer.

**Fixed-Threshold** - Dumb strategy: only sells when price > (min+max)/2. Doesn't adapt at all.

**Constant-Rate** - Sells exactly Q/n units per period regardless of price. Completely ignores market signals.

**Random** - Does random stuff. Worst possible baseline. If your algorithm loses to this, something's very wrong.

## File Structure
```
inventory_simulation/
├── data/
│   ├── default_config.json          # Default parameters
│   ├── test_scenarios.json          # Predefined test cases
│   ├── vietnam_stores.json          # Store location data
│   └── benchmark_cases.json         # Cases to verify formulas
│
├── fixtures/
│   ├── config_loader.py             # Loads configs from JSON
│   ├── scenario_generator.py       # Generates random price sequences
│   └── data_validator.py           # Validates input parameters
│
├── algorithms/
│   ├── base.py                      # Abstract base class
│   ├── alg_ir.py                    # Main ALG-IR implementation
│   ├── alg_ir_h.py                  # ALG-IR with holding costs
│   ├── myopic.py                    # Greedy strategy
│   ├── offline.py                   # Perfect foresight (benchmark)
│   ├── moving_average.py            # Trend-following strategy
│   ├── adaptive_myopic.py           # Enhanced myopic
│   └── ... (7 more algorithms)
│
├── visualization/
│   ├── formula_proof.py             # Verify math is correct
│   ├── comparison.py                # Compare all algorithms
│   └── detailed_analysis.py         # Deep dive metrics
│
├── models.py                        # Data classes
├── runner.py                        # Simulation orchestrator
├── main.py                          # CLI entry point
└── requirements.txt
```

## Adding Your Own Algorithm

Want to try a new strategy? Easy.

1. Create a new file in `algorithms/`, say `my_strategy.py`

2. Copy this template:
```python
from algorithms.base import Algorithm

class MyStrategyAlgorithm(Algorithm):
    def __init__(self):
        super().__init__("My-Strategy")
    
    def decide(self, t, p_t, I_t, params):
        """
        t: current period (1 to n)
        p_t: current price
        I_t: remaining inventory
        params: simulation parameters (Q, m, M, a, b, etc.)
        
        Return: how many units to retrieve (0 to I_t)
        """
        # Your logic here
        # Example: only sell when price is really high
        if p_t > params.M * 0.9:
            expected_demand = params.a - params.b * p_t
            return min(expected_demand, I_t)
        else:
            return 0
```

3. Add it to `runner.py`:
```python
from algorithms.my_strategy import MyStrategyAlgorithm

class SimulationRunner:
    def __init__(self, params):
        self.algorithms = [
            # ... existing algorithms ...
            MyStrategyAlgorithm(),  # Add this line
        ]
```

4. Run the simulation. Your algorithm will automatically be included in all comparisons.

## Customizing Test Scenarios

Edit `data/test_scenarios.json` to add your own scenarios. For example:
```json
{
  "My Custom Test": {
    "Q": 1000,
    "m": 100.0,
    "M": 200.0,
    "n": 30,
    "a": 500.0,
    "b": 2.0,
    "delta": 0.15,
    "h": 3.0,
    "num_scenarios": 200
  }
}
```

Then run it:
```bash
python main.py --config "My Custom Test"
```

You can also define fixed price sequences in the same file if you want to test specific patterns (like always increasing, or extremely volatile).

## Interpreting Results

**Competitive Ratio (CR)**: This is the key metric. It's your algorithm's revenue divided by the Offline (perfect) revenue. 
- CR = 1.0: Impossible (you'd need to predict the future)
- CR > 0.9: Excellent
- CR = 0.8-0.9: Good
- CR = 0.7-0.8: Decent
- CR < 0.7: Needs improvement

**Standard Deviation**: Lower is better. Shows how consistent the algorithm is across different random scenarios.

**Revenue Distribution**: Box plots show the spread. Narrow box = consistent performance. Wide box = unpredictable.

From the paper, ALG-IR has a theoretical guarantee of CR ≥ 1/(1+ln(θ)) where θ = M/m. For default params (θ=3), that's CR ≥ 0.477. In practice, it usually does way better (0.85-0.95).

## Common Issues

**"Import error"**: Make sure you're running from the `inventory_simulation/` directory and installed all requirements.

**Weird results**: Check that your parameters make sense:
- Q > 0 (can't sell negative inventory)
- m < M (min price must be less than max)
- 0 ≤ delta < 1 (fluctuation range)
- a > b*M (demand must be positive at max price)

**Graphs look wrong**: Compare against the benchmark cases in `data/benchmark_cases.json`. The formula proof chart should match the expected values.

**Too slow**: Reduce `num_scenarios` in the config. 100 scenarios is usually enough. 1000+ scenarios is overkill unless you need publication-quality stats.

## For the Report

When writing up results, focus on:

1. **Formula validation**: Show that your implementation matches the paper's equations (use the formula proof chart)

2. **Competitive analysis**: Compare ALG-IR against baselines (use the comparison chart)

3. **Robustness**: Test on different scenarios (iPhone, seasonal products, commodities) and show ALG-IR works well across all of them

4. **Practical insights**: When does ALG-IR beat Myopic? When does it struggle? What's the value of the two-stage strategy?

5. **Limitations**: Be honest about when simpler strategies (like Myopic) are "good enough" vs when you need the sophistication of ALG-IR

## Backend Code (Optional)

There's also a full FastAPI backend in the `backend/` folder if you want to build a web interface later. It includes:
- REST API endpoints
- PostgreSQL database for storing results
- Store location management
- Batch simulation endpoints

But for the course project, the standalone simulation is probably enough.

## Credits

Lê Hoàng Quốc Anh


![Demo](https://i1.sndcdn.com/avatars-yIkw1Uu90iewrz1u-SUlZPw-t1080x1080.jpg)


## Questions?

If something's not working or you're confused about the results, check:
1. The visualization outputs - they're pretty self-explanatory
2. The data files in `data/` - make sure your parameters make sense
3. The algorithm implementations - they're commented

Good luck with the presentation!