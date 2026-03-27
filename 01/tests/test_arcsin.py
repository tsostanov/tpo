from __future__ import annotations

import csv
import math

import pytest

import arcsin as arcsin_module
from arcsin import (
    TRANSFORM_THRESHOLD,
    _arcsin_series_sum,
    _arcsin_series_terms,
    arcsin,
)

REFERENCE_CASES_PATH = (
    __file__.replace("\\", "/").rsplit("/", 1)[0] + "/data/arcsin_reference.csv"
)


def _series_coefficient(n: int) -> float:
    return math.factorial(2 * n) / (4**n * math.factorial(n) ** 2 * (2 * n + 1))


def _reference_cases(group: str) -> list[pytest.ParameterSet]:
    with open(REFERENCE_CASES_PATH, newline="", encoding="utf-8") as reference_file:
        reader = csv.DictReader(reference_file)
        return [
            pytest.param(float(row["x"]), float(row["expected"]), id=row["case_id"])
            for row in reader
            if row["group"] == group
        ]


class TestArcsinSeriesInternals:
    def test_series_terms_match_coefficients(self) -> None:
        x = 0.5
        terms = _arcsin_series_terms(x, 4)
        expected = [
            _series_coefficient(n) * x ** (2 * n + 1) for n in range(len(terms))
        ]

        for term, exp in zip(terms, expected):
            assert term == pytest.approx(exp, abs=1e-15)

    def test_series_terms_count_zero(self) -> None:
        assert not _arcsin_series_terms(0.25, 0)

    @pytest.mark.parametrize(
        "count",
        [
            pytest.param(-1, id="minus-one"),
            pytest.param(-2, id="minus-two"),
        ],
    )
    def test_series_terms_negative_count(self, count: int) -> None:
        with pytest.raises(ValueError, match="count must be non-negative"):
            _arcsin_series_terms(0.25, count)

    @pytest.mark.parametrize(
        "eps",
        [
            pytest.param(0.0, id="zero"),
            pytest.param(-1e-12, id="negative-tiny"),
            pytest.param(-1.0, id="negative-one"),
        ],
    )
    def test_series_sum_rejects_non_positive_eps(self, eps: float) -> None:
        with pytest.raises(ValueError, match="eps must be positive"):
            _arcsin_series_sum(0.1, eps, 10)

    @pytest.mark.parametrize(
        "max_terms",
        [
            pytest.param(0, id="zero"),
            pytest.param(-1, id="minus-one"),
            pytest.param(-100, id="minus-hundred"),
        ],
    )
    def test_series_sum_rejects_non_positive_max_terms(self, max_terms: int) -> None:
        with pytest.raises(ValueError, match="max_terms must be positive"):
            _arcsin_series_sum(0.1, 1e-8, max_terms)

    def test_series_sum_no_convergence(self) -> None:
        with pytest.raises(
            RuntimeError, match="series did not converge within max_terms"
        ):
            _arcsin_series_sum(0.5, 1e-20, 1)


@pytest.mark.parametrize(
    "sign",
    [
        pytest.param(1.0, id="positive"),
        pytest.param(-1.0, id="negative"),
    ],
)
class TestArcsinSymmetryAndKnownValues:
    @pytest.mark.parametrize(
        "base, expected",
        [
            pytest.param(0.0, 0.0, id="zero"),
            pytest.param(0.5, math.pi / 6.0, id="half"),
            pytest.param(1.0, math.pi / 2.0, id="one"),
        ],
    )
    def test_known_values(self, sign: float, base: float, expected: float) -> None:
        x = sign * base
        assert arcsin(x) == pytest.approx(sign * expected, abs=1e-10)

    @pytest.mark.parametrize("base, expected", _reference_cases("match"))
    def test_matches_reference_data(
        self, sign: float, base: float, expected: float
    ) -> None:
        x = sign * base
        assert arcsin(x, eps=1e-12) == pytest.approx(sign * expected, abs=1e-10)

    @pytest.mark.parametrize(
        "base",
        [
            pytest.param(0.1, id="one-tenth"),
            pytest.param(0.5, id="half"),
            pytest.param(0.9, id="near-one"),
        ],
    )
    def test_is_odd_function(self, sign: float, base: float) -> None:
        x = sign * base
        assert arcsin(-x) == pytest.approx(-arcsin(x), abs=1e-12)


class TestArcsinDomainErrors:
    @pytest.mark.parametrize(
        "x",
        [
            pytest.param(1.000001, id="above-one"),
            pytest.param(2.0, id="far-above-one"),
            pytest.param(-1.000001, id="below-minus-one"),
            pytest.param(-5.0, id="far-below-minus-one"),
        ],
    )
    def test_rejects_values_outside_domain(self, x: float) -> None:
        with pytest.raises(ValueError, match=r"x must be within \[-1, 1\]"):
            arcsin(x)

    @pytest.mark.parametrize(
        "eps",
        [
            pytest.param(0.0, id="zero"),
            pytest.param(-1e-12, id="negative-tiny"),
            pytest.param(-1.0, id="negative-one"),
        ],
    )
    def test_rejects_non_positive_eps(self, eps: float) -> None:
        with pytest.raises(ValueError, match="eps must be positive"):
            arcsin(0.5, eps=eps)

    @pytest.mark.parametrize(
        "max_terms",
        [
            pytest.param(0, id="zero"),
            pytest.param(-1, id="minus-one"),
            pytest.param(-100, id="minus-hundred"),
        ],
    )
    def test_rejects_non_positive_max_terms(self, max_terms: int) -> None:
        with pytest.raises(ValueError, match="max_terms must be positive"):
            arcsin(0.5, max_terms=max_terms)


class TestArcsinNearBounds:
    @pytest.mark.parametrize(
        "x",
        [
            pytest.param(-0.9, id="minus-0.9"),
            pytest.param(0.9, id="plus-0.9"),
        ],
    )
    def test_near_one_matches_sine_inverse(self, x: float) -> None:
        result = arcsin(x, eps=1e-12)
        assert math.sin(result) == pytest.approx(x, abs=1e-8)

    @pytest.mark.parametrize("x, expected", _reference_cases("threshold"))
    def test_threshold_boundary_values(self, x: float, expected: float) -> None:
        assert arcsin(x) == pytest.approx(expected, abs=1e-10)

    def test_threshold_switching_rule(self, monkeypatch: pytest.MonkeyPatch) -> None:
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
