import numpy as np
from scipy.optimize import brentq
from .base import Algorithm


class ALG_IR_H(Algorithm):
    def __init__(self, Q, m, M, demand, h: float):
        super().__init__(Q, m, M, demand)
        self.h = h

    def name(self) -> str:
        return "ALG-IR-H"

    def inverse_cdf(self, u: float) -> float:
        return (1 - self.delta) + u * 2 * self.delta

    def cdf(self, z_val: float) -> float:
        lower = 1 - self.delta
        upper = 1 + self.delta
        if z_val < lower: return 0.0
        if z_val > upper: return 1.0
        return (z_val - lower) / (upper - lower)

    # Đạo hàm doanh thu biên ròng (Net Marginal Revenue) theo Eq 17
    def marginal_revenue_net(self, x: float, price: float, t: int) -> float:
        # Eq 17 dòng 2: p * [1 - F(...)] - (t-1)h
        # Đây là đạo hàm của doanh thu tại thời điểm t, trừ đi chi phí đã tốn để giữ hàng tới t
        mr_pure = price * (1 - self.cdf(x / self.demand.expected(price)))
        holding_cost_sunk = (t - 1) * self.h
        return mr_pure - holding_cost_sunk

    def phi_h(self, y: float, t: int, n: int) -> float:
        past_periods = t - 1
        m_t = self.m - past_periods * self.h
        M_t = self.M - past_periods * self.h

        # Nếu chi phí tồn kho ăn hết giá sàn -> Giá trị hàng về 0
        if m_t <= 1e-9:
            return 0.0

        theta_t = M_t / m_t
        # Threshold phụ thuộc vào t (Horizon)
        threshold_t = self.Q / (1 + np.log(theta_t))

        if y < threshold_t:
            return m_t

        exponent = (y * (1 + np.log(theta_t)) / self.Q) - 1
        return m_t * np.exp(exponent)

    def decide(self, t: int, n: int, price: float, inventory: float, cumulative: float) -> float:
        # Eq 9: Kỳ cuối bán hết
        if t == n:
            return inventory

        base_demand = self.demand.expected(price)
        if base_demand <= 0: return 0.0

        # Tính toán tham số động
        past_periods = t - 1
        m_t = self.m - past_periods * self.h
        M_t = self.M - past_periods * self.h

        if m_t <= 1e-9: return inventory  # Bán tháo nếu lỗ phí kho

        theta_t = M_t / m_t
        threshold_t = self.Q / (1 + np.log(theta_t))

        # --- GIAI ĐOẠN 1 (While Loop trong Paper) ---
        # Kiểm tra điều kiện ngưỡng
        # Tính x dự kiến (Stage 1 retrieval)
        p_net = price - past_periods * self.h

        # --- STAGE 1: Lines 3-11 (While Loop) ---


        if p_net <= m_t:
            x_candidate = 0.0
        else:
            quantile = 1 - (m_t / p_net)
            x_candidate = base_demand * self.inverse_cdf(quantile)

        # Nếu chưa vượt ngưỡng Threshold -> Stage 1
        if cumulative + x_candidate <= threshold_t:
            return max(0.0, min(x_candidate, inventory))

        # --- GIAI ĐOẠN 2 (Else / For Loop trong Paper) ---

        phi_val = self.phi_h(cumulative, t, n)

        # Line 14: Check điều kiện giá
        # Cực kỳ quan trọng: So sánh Net Price vs Net Opportunity Cost
        # Nếu p_net <= phi_val thì không bán
        if price <= phi_val:
            return 0.0
        else:
            # Line 17: Giải phương trình Pi'_t(x) = phi^h(y+x)
            def equation(x):
                lhs = self.marginal_revenue_net(x, price, t)
                rhs = self.phi_h(cumulative + x, t, n)
                return lhs - rhs

            try:
                # Kiểm tra biên
                if equation(0) < 0: return 0.0
                if equation(inventory) > 0: return inventory

                return brentq(equation, 0, inventory)
            except (ValueError, RuntimeError):
                return 0.0

    @property
    def delta(self):
        return self.demand.delta