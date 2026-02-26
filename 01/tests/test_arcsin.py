from __future__ import annotations

import math
import pytest

from arcsin import _arcsin_series_sum, _arcsin_series_terms, arcsin


def _series_coefficient(n: int) -> float:
    return math.factorial(2 * n) / (4**n * math.factorial(n) ** 2 * (2 * n + 1))


def test_series_terms_match_coefficients() -> None:
    x = 0.5
    terms = _arcsin_series_terms(x, 4)
    expected = [_series_coefficient(n) * x ** (2 * n + 1) for n in range(len(terms))]
    for term, exp in zip(terms, expected):
        assert math.isclose(term, exp, rel_tol=0.0, abs_tol=1e-15)


def test_series_terms_count_zero() -> None:
    assert not _arcsin_series_terms(0.25, 0)


def test_series_terms_negative_count() -> None:
    with pytest.raises(ValueError):
        _arcsin_series_terms(0.25, -1)


@pytest.mark.parametrize("x", [0.0, 0.2, -0.2, 0.5, -0.5])
def test_arcsin_sin_inverse(x: float) -> None:
    result = arcsin(x, eps=1e-12)
    assert math.isclose(math.sin(result), x, rel_tol=0.0, abs_tol=1e-10)


@pytest.mark.parametrize(
    "x, expected",
    [
        (-1.0, -math.pi / 2.0),
        (-0.5, -math.pi / 6.0),
        (0.0, 0.0),
        (0.5, math.pi / 6.0),
        (1.0, math.pi / 2.0),
    ],
)
def test_arcsin_known_values(x: float, expected: float) -> None:
    assert math.isclose(arcsin(x), expected, rel_tol=0.0, abs_tol=1e-10)


@pytest.mark.parametrize("x", [0.9, -0.9])
def test_arcsin_near_one(x: float) -> None:
    result = arcsin(x, eps=1e-12)
    assert math.isclose(math.sin(result), x, rel_tol=0.0, abs_tol=1e-8)


def test_arcsin_invalid_domain() -> None:
    with pytest.raises(ValueError):
        arcsin(1.01)


def test_series_sum_invalid_eps() -> None:
    with pytest.raises(ValueError):
        _arcsin_series_sum(0.1, 0.0, 10)


def test_series_sum_invalid_max_terms() -> None:
    with pytest.raises(ValueError):
        _arcsin_series_sum(0.1, 1e-8, 0)


def test_series_sum_no_convergence() -> None:
    with pytest.raises(RuntimeError):
        _arcsin_series_sum(0.5, 1e-20, 1)
