import numpy as np
from typing import List
from scipy.optimize import brentq
from scipy.stats import norm
from algorithms.base import Algorithm
from models import AlgorithmResult



class Offline(Algorithm):
    def name(self) -> str:
        return "Offline"

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        raise NotImplementedError("Offline requires all prices upfront")

    def _inv_cdf_delta(self, u: float) -> float:
        """Inverse CDF of δ (the fluctuation factor) at probability u (0..1)"""
        if self.demand.distribution == "truncnorm":
            return float(self.demand.truncnorm.ppf(u))
        else:
            # uniform on [1-Δ, 1+Δ]
            delta = self.demand.delta
            return (1 - delta) + u * (2 * delta)

    def _cdf_delta(self, z: float) -> float:
        if self.demand.distribution == "truncnorm":
            return float(self.demand.truncnorm.cdf(z))
        else:
            lower = 1 - self.demand.delta
            upper = 1 + self.demand.delta
            if z < lower: return 0.0
            if z > upper: return 1.0
            return (z - lower) / (upper - lower)

    def _x_of_lambda_for_period(self, lam: float, price: float, base_demand: float) -> float:
        if base_demand <= 0:
            return 0.0

        # Marginal revenue at x=0 is p (since F(0)=0 as support δ>0)
        if lam >= price:
            return 0.0

        # Solve p * (1 - F(z)) = lam  => F(z) = 1 - lam/p  => z = F^{-1}(1 - lam/p)
        u = 1.0 - (lam / price)
        # safety clamp
        u = min(max(u, 0.0), 1.0)
        z_star = self._inv_cdf_delta(u)
        x = base_demand * z_star

        # ensure non-neg and finite
        return float(max(0.0, x))

    def _max_possible_sum(self, prices: List[float], base_demands: List[float]) -> float:
        """Maximum sum achievable if lambda -> 0: sum base_demand * (1+Δ)"""
        delta = self.demand.delta
        return sum(b * (1 + delta) for b in base_demands)

    def _sum_x_given_lambda(self, lam: float, prices: List[float], base_demands: List[float]) -> float:
        s = 0.0
        for p, b in zip(prices, base_demands):
            s += self._x_of_lambda_for_period(lam, p, b)
        return s

    def _allocations_for_lambda(self, lam: float, prices: List[float], base_demands: List[float]) -> List[float]:
        return [self._x_of_lambda_for_period(lam, p, b) for p, b in zip(prices, base_demands)]

    def _compute_expected_revenue_from_alloc(self, allocations: List[float], prices: List[float]) -> float:
        """Compute expected revenue Σ π_t(x_t) using same formula as before (uses demand model cdf/pdf where needed)"""
        total = 0.0
        delta = self.demand.delta
        for x_t, p in zip(allocations, prices):
            b = self.demand.expected(p)
            if b <= 0:
                continue
            lower = b * (1 - delta)
            upper = b * (1 + delta)

            if x_t <= lower:
                total += p * x_t
            elif x_t >= upper:
                total += p * b
            else:
                z = x_t / b
                # integral term: ∫_{z}^{1+Δ} δ * f(δ) dδ   (we'll compute via cdf/pdf if truncnorm)
                if self.demand.distribution == "truncnorm":
                    # compute via norm's cdf/pdf using truncnorm parameters
                    # re-use truncnorm.cdf and pdf
                    # integral = ∫_{z}^{1+Δ} δ * f_trunc(δ) dδ
                    # but easier: compute using numerical identity: E[δ * 1_{δ>=z}] under truncated pdf
                    # We'll compute integral_term = ∫_{z}^{1+Δ} δ * f_trunc(δ) dδ
                    # Using truncnorm object:
                    dist = self.demand.truncnorm
                    # dist.pdf accepts scalar
                    def integrand_val(v):
                        return v * dist.pdf(v)
                    # approximate integral with small quad if needed; but here it's used only for expected revenue final calc;
                    # use simple numeric integration with a few points for speed
                    xs = np.linspace(z, 1 + delta, 40)
                    ys = xs * dist.pdf(xs)
                    integral_term = np.trapz(ys, xs)
                else:
                    # uniform: f(δ)=1/(2Δ) on [1-Δ,1+Δ]
                    integral_term = ((1 + delta) ** 2 - z ** 2) / (4 * delta)

                prob_excess = self._cdf_delta(z)
                total += p * b * integral_term + p * x_t * (1 - prob_excess)
        return float(total)

    def run(self, prices: List[float]) -> AlgorithmResult:
        n = len(prices)

        # Precompute base demands
        base_demands = [self.demand.expected(p) for p in prices]

        # Quick: if all base_demands <= 0
        if sum(base_demands) <= 0:
            # no demand at all
            allocations = [0.0] * n
            retrievals = []
            revenues = []
            inventory_levels = [self.Q]
            cumulative = 0.0
            for p, alloc in zip(prices, allocations):
                actual_d = self.demand.actual(p)
                sold = min(alloc, actual_d)
                revenues.append(p * sold)
                retrievals.append(alloc)
                cumulative += alloc
                inventory_levels.append(int(self.Q - cumulative))
            return AlgorithmResult(self.name(), total_revenue=sum(revenues), retrievals=retrievals, revenues=revenues, inventory=inventory_levels)

        # If total possible (selling at max z=1+Δ) is < Q, allocate all maxima and put leftover in last period
        max_sum = self._max_possible_sum(prices, base_demands)
        if max_sum <= 0:
            allocations = [0.0] * n
        elif max_sum < self.Q:
            # allocate full upper bound
            delta = self.demand.delta
            allocations = [b * (1 + delta) for b in base_demands]
            # put remaining into last period (it won't change expected revenue because revenue flat beyond upper)
            remaining = self.Q - sum(allocations)
            if remaining > 0:
                allocations[-1] += remaining
        else:
            # Standard case: there exists lambda in (0, max_price) with S(lambda)=Q
            # Build function S(lambda) - Q
            def f_lam(lam):
                return self._sum_x_given_lambda(lam, prices, base_demands) - self.Q

            # bounds: lam_low -> tiny positive (approach 0), lam_high -> max_price (gives sum=0)
            lam_low = 1e-12
            lam_high = max(prices)  # if lam >= max price => zero allocation

            # ensure signs for brentq
            s_low = f_lam(lam_low)
            s_high = f_lam(lam_high)
            # s_low should be >= 0 (since lam_low ~0 => allocations ~ upper bounds => sum >= Q)
            # s_high should be <= 0 (since lam_high >= max price => sum = 0 <= Q)
            # numerical safety:
            if s_low < 0:
                # weird: fallback to greedy
                lam_star = lam_low
            else:
                # find root
                try:
                    lam_star = brentq(f_lam, lam_low, lam_high, xtol=1e-9, rtol=1e-9, maxiter=200)
                except ValueError:
                    # numerical fallback: if brentq fails, pick lam that gives closest sum via simple search
                    lams = np.linspace(lam_low, lam_high, 200)
                    sums = [self._sum_x_given_lambda(l, prices, base_demands) for l in lams]
                    idx = np.argmin(np.abs(np.array(sums) - self.Q))
                    lam_star = lams[idx]

            allocations = self._allocations_for_lambda(lam_star, prices, base_demands)

            # small numerical renormalization to enforce exact sum Q
            total_alloc = sum(allocations)
            if total_alloc > 0:
                allocations = [a * (self.Q / total_alloc) for a in allocations]

        # Simulate with allocations (sample actual demand per period)
        retrievals = []
        revenues = []
        inventory_levels = [self.Q]
        cumulative = 0.0

        for p, alloc in zip(prices, allocations):
            actual_d = self.demand.actual(p)
            sold = min(alloc, actual_d)
            revenue = p * sold

            cumulative += alloc
            retrievals.append(alloc)
            revenues.append(revenue)
            inventory_levels.append(int(self.Q - cumulative))

        return AlgorithmResult(
            name=self.name(),
            total_revenue=sum(revenues),
            retrievals=retrievals,
            revenues=revenues,
            inventory=inventory_levels
        )
