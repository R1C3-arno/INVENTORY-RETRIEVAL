from dataclasses import dataclass
from typing import List


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]


class DataValidator:
    @staticmethod
    def validate_config(config) -> ValidationResult:
        errors = []

        if config.Q <= 0:
            errors.append("Q must be positive")

        if config.m <= 0:
            errors.append("m must be positive")

        if config.M <= config.m:
            errors.append("M must be greater than m")

        if config.n <= 0:
            errors.append("n must be positive")

        if config.a <= 0:
            errors.append("a must be positive")

        if config.b <= 0:
            errors.append("b must be positive")

        if not (0 <= config.delta < 1):
            errors.append("delta must be in [0, 1)")

        if config.h < 0:
            errors.append("h must be non-negative")

        return ValidationResult(len(errors) == 0, errors)

    @staticmethod
    def validate_prices(prices: List[float], m: float, M: float) -> ValidationResult:
        errors = []

        for i, price in enumerate(prices):
            if not (m <= price <= M):
                errors.append(f"Price at period {i} ({price}) out of range [{m}, {M}]")

        return ValidationResult(len(errors) == 0, errors)