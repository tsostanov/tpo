from __future__ import annotations

import math
import pytest

import arcsin as arcsin_module
from arcsin import (
    TRANSFORM_THRESHOLD,
    _arcsin_series_sum,
    _arcsin_series_terms,
    arcsin,
)


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


@pytest.mark.parametrize("x", [1.01, -1.01])
def test_arcsin_invalid_domain(x: float) -> None:
    with pytest.raises(ValueError):
        arcsin(x)


def test_series_sum_invalid_eps() -> None:
    with pytest.raises(ValueError):
        _arcsin_series_sum(0.1, 0.0, 10)


def test_series_sum_invalid_max_terms() -> None:
    with pytest.raises(ValueError):
        _arcsin_series_sum(0.1, 1e-8, 0)


def test_series_sum_no_convergence() -> None:
    with pytest.raises(RuntimeError):
        _arcsin_series_sum(0.5, 1e-20, 1)


@pytest.mark.parametrize(
    "x",
    [
        -TRANSFORM_THRESHOLD - 1e-12,
        -TRANSFORM_THRESHOLD,
        -TRANSFORM_THRESHOLD + 1e-12,
        TRANSFORM_THRESHOLD - 1e-12,
        TRANSFORM_THRESHOLD,
        TRANSFORM_THRESHOLD + 1e-12,
    ],
)
def test_arcsin_threshold_boundary_values(x: float) -> None:
    assert math.isclose(arcsin(x), math.asin(x), rel_tol=0.0, abs_tol=1e-10)


def test_arcsin_threshold_switching_rule(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[float] = []

    def fake_series_sum(value: float, eps: float, max_terms: int) -> float:
        del eps, max_terms
        calls.append(value)
        return value

    monkeypatch.setattr(arcsin_module, "_arcsin_series_sum", fake_series_sum)

    direct = arcsin(TRANSFORM_THRESHOLD)
    assert direct == pytest.approx(TRANSFORM_THRESHOLD)
    assert calls[-1] == pytest.approx(TRANSFORM_THRESHOLD)

    x = TRANSFORM_THRESHOLD + 1e-12
    transformed = arcsin(x)
    inner = math.sqrt(1.0 - x * x)
    assert transformed == pytest.approx(math.pi / 2.0 - inner)
    assert calls[-1] == pytest.approx(inner)
