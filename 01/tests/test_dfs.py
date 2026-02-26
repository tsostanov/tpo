from __future__ import annotations

from dfs import Step, dfs


def test_dfs_trace_and_order() -> None:
    graph = {
        "A": ["B", "C"],
        "B": ["A", "D"],
        "C": ["A", "D"],
        "D": ["B", "C"],
    }
    trace: list[Step] = []

    order = dfs(graph, "A", trace)

    assert order == ["A", "B", "D", "C"]
    assert trace == [
        Step.START,
        Step.ENTER,
        Step.CHECK_NEIGHBOR,
        Step.VISIT_NEIGHBOR,
        Step.ENTER,
        Step.CHECK_NEIGHBOR,
        Step.SKIP_VISITED,
        Step.CHECK_NEIGHBOR,
        Step.VISIT_NEIGHBOR,
        Step.ENTER,
        Step.CHECK_NEIGHBOR,
        Step.SKIP_VISITED,
        Step.CHECK_NEIGHBOR,
        Step.VISIT_NEIGHBOR,
        Step.ENTER,
        Step.CHECK_NEIGHBOR,
        Step.SKIP_VISITED,
        Step.CHECK_NEIGHBOR,
        Step.SKIP_VISITED,
        Step.EXIT,
        Step.EXIT,
        Step.EXIT,
        Step.CHECK_NEIGHBOR,
        Step.SKIP_VISITED,
        Step.EXIT,
        Step.FINISH,
    ]


def test_dfs_without_trace() -> None:
    order = dfs({}, "Z")
    assert order == ["Z"]
