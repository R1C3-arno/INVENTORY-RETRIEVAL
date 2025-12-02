import numpy as np
from scipy.optimize import brentq
from .base import Algorithm


class ALG_IR(Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Threshold tĩnh: Q / (1 + ln(theta))
        self.threshold = self.Q / (1 + np.log(self.theta))

    def name(self) -> str:
        return "ALG-IR"

    # --- CÁC HÀM PHỤ TRỢ TOÁN HỌC ---

    # Hàm F^-1(u) cho phân phối Uniform [1-delta, 1+delta]
    def inverse_cdf(self, u: float) -> float:
        if self.demand.distribution == "truncnorm":
            return self.demand.truncnorm.ppf(u)
        else:
            # u nằm trong [0, 1]
            # Với Uniform: F^-1(u) = (1 - delta) + u * 2 * delta
            return (1 - self.delta) + u * 2 * self.delta

    # Hàm F(z) cho phân phối Uniform
    def cdf(self, z_val: float) -> float:
        if self.demand.distribution == "truncnorm":
            return self.demand.truncnorm.cdf(z_val)
        else:
                # z_val là hệ số dao động demand (delta_t)
                lower = 1 - self.delta
                upper = 1 + self.delta
                if z_val < lower: return 0.0
                if z_val > upper: return 1.0
                return (z_val - lower) / (upper - lower)

    # Đạo hàm doanh thu biên: pi'(x)
    # Theo công thức (4) trong paper (Page 5): pi'(x) = p * [1 - F( x / (a-bp) )]
    def marginal_revenue(self, x: float, price: float) -> float:
        base_demand = self.demand.expected(price)  # a - b*p
        if base_demand <= 0: return 0

        # z = x / base_demand. Đây chính là delta_t tương ứng
        z = x / base_demand

        # F(z)
        prob_F = self.cdf(z)

        return price * (1 - prob_F)

    # Giá sàn kỳ vọng phi(y)
    def phi(self, y: float) -> float:
        if y < self.threshold:
            return self.m
        # Công thức (7) trong paper
        # phi(y) = m * exp( (y * (1+ln(theta))/Q) - 1 )
        exponent = (y * (1 + np.log(self.theta)) / self.Q) - 1
        return self.m * np.exp(exponent)

    # --- LOGIC CHÍNH ---

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        # 1. Nếu là kỳ cuối cùng, bán hết (Paper Eq 9)
        if t == n:
            return inventory

        # Tính demand cơ sở (a - bp)
        base_demand = self.demand.expected(price)
        if base_demand <= 0: return 0.0

        # --- GIAI ĐOẠN 1: CHECK ĐIỀU KIỆN (Line 3 Algorithm 1) ---
        # Tính lượng hàng tối ưu nếu ở Stage 1: x_1 = (a-bp) * F^-1(1 - m/p)
        # Lưu ý: Nếu price < m thì không bán (vì 1 - m/p < 0)
        if price <= self.m:
            x_candidate = 0.0
        else:
            quantile = 1 - (self.m / price)
            factor = self.inverse_cdf(quantile)  # F^-1
            x_candidate = base_demand * factor

        # Điều kiện chuyển stage: y + x_candidate <= Threshold
        is_stage_1 = (cumulative + x_candidate) <= self.threshold

        if is_stage_1:
            # === STAGE 1: ABUNDANT ===
            # Line 4: Bán x_candidate
            retrieval = x_candidate

        else:
            # === STAGE 2: SCARCE ===
            phi_val = self.phi(cumulative)

            # Line 14: Check luật phòng thủ
            if price <= phi_val:
                retrieval = 0.0
            else:
                # Line 17: Giải phương trình pi'(x) = phi(y + x)
                # Tìm x sao cho: marginal_revenue(x) - phi(cumulative + x) = 0

                def equation(x):
                    lhs = self.marginal_revenue(x, price)
                    rhs = self.phi(cumulative + x)
                    return lhs - rhs

                # Tìm nghiệm trong khoảng [0, inventory]
                # Kiểm tra dấu 2 đầu mút để đảm bảo có nghiệm (Root finding)
                try:
                    # Nếu tại x=0 mà MR < MC -> Không nên bán gì cả
                    if equation(0) < 0:
                        retrieval = 0.0
                    # Nếu tại x=inventory mà MR > MC -> Bán hết sạch
                    elif equation(inventory) > 0:
                        retrieval = inventory
                    else:
                        # Nghiệm nằm giữa 0 và inventory
                        retrieval = brentq(equation, 0, inventory)
                except ValueError:
                    # Fallback an toàn nếu brentq lỗi
                    retrieval = 0.0

        # Đảm bảo không bán quá tồn kho
        return max(0.0, min(retrieval, inventory))

    # Cần thêm property delta vào Algorithm base hoặc lấy từ demand model
    @property
    def delta(self):
        return self.demand.delta
