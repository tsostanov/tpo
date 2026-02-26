from __future__ import annotations

import math
from typing import List

DEFAULT_EPS = 1e-12
DEFAULT_MAX_TERMS = 100000
TRANSFORM_THRESHOLD = 0.7


def _arcsin_series_terms(x: float, count: int) -> List[float]:
    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0:
        return []

    terms: List[float] = []
    term = x
    n = 0
    while n < count:
        terms.append(term)
        ratio = ((2 * n + 1) ** 2) / (2 * (n + 1) * (2 * n + 3))
        term *= ratio * x * x
        n += 1
    return terms


def _arcsin_series_sum(x: float, eps: float, max_terms: int) -> float:
    if eps <= 0:
        raise ValueError("eps must be positive")
    if max_terms <= 0:
        raise ValueError("max_terms must be positive")

    term = x
    total = term
    n = 0
    while abs(term) > eps and n < max_terms:
        ratio = ((2 * n + 1) ** 2) / (2 * (n + 1) * (2 * n + 3))
        term *= ratio * x * x
        total += term
        n += 1

    if n >= max_terms:
        raise RuntimeError("series did not converge within max_terms")

    return total


def arcsin(
    x: float,
    eps: float = DEFAULT_EPS,
    max_terms: int = DEFAULT_MAX_TERMS,
) -> float:
    if abs(x) > 1:
        raise ValueError("x must be within [-1, 1]")
    if x == 1.0:
        return math.pi / 2.0
    if x == -1.0:
        return -math.pi / 2.0

    sign = 1.0 if x >= 0 else -1.0
    y = abs(x)

    if y > TRANSFORM_THRESHOLD:
        inner = math.sqrt(1.0 - y * y)
        return sign * (math.pi / 2.0 - _arcsin_series_sum(inner, eps, max_terms))

    return sign * _arcsin_series_sum(y, eps, max_terms)


__all__ = ["arcsin", "_arcsin_series_terms"]
