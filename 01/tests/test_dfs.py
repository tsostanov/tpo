from __future__ import annotations

import pytest

from dfs import Event, Step, dfs


def test_dfs_trace_and_order() -> None:
    graph = {
        "A": ["B", "C"],
        "B": ["A", "D"],
        "C": ["A", "D"],
        "D": ["B", "C"],
    }
    trace: list[Event[str]] = []

    order = dfs(graph, "A", trace)

    assert order == ["A", "B", "D", "C"]
    assert trace[0].step == Step.START
    assert trace[0].vertex == "A"
    assert trace[-1].step == Step.FINISH
    assert trace[-1].vertex == "A"

    enter_vertices = [event.vertex for event in trace if event.step == Step.ENTER]
    exit_vertices = [event.vertex for event in trace if event.step == Step.EXIT]

    assert enter_vertices == order
    assert sorted(exit_vertices) == sorted(order)
    assert len(enter_vertices) == len(exit_vertices) == len(order)

    assert any(event.step == Step.SKIP_VISITED for event in trace)

    for event in trace:
        if event.step in {Step.CHECK_NEIGHBOR, Step.VISIT_NEIGHBOR, Step.SKIP_VISITED}:
            assert event.vertex in graph
            assert event.neighbor in graph[event.vertex]

    for index, event in enumerate(trace):
        if event.step == Step.VISIT_NEIGHBOR:
            next_event = trace[index + 1]
            assert next_event.step == Step.ENTER
            assert next_event.vertex == event.neighbor


def test_dfs_exact_trace() -> None:
    graph = {"A": ["B"], "B": ["A"]}
    trace: list[Event[str]] = []

    order = dfs(graph, "A", trace)

    assert order == ["A", "B"]
    assert trace == [
        Event(Step.START, vertex="A"),
        Event(Step.ENTER, vertex="A"),
        Event(Step.CHECK_NEIGHBOR, vertex="A", neighbor="B"),
        Event(Step.VISIT_NEIGHBOR, vertex="A", neighbor="B"),
        Event(Step.ENTER, vertex="B"),
        Event(Step.CHECK_NEIGHBOR, vertex="B", neighbor="A"),
        Event(Step.SKIP_VISITED, vertex="B", neighbor="A"),
        Event(Step.EXIT, vertex="B"),
        Event(Step.EXIT, vertex="A"),
        Event(Step.FINISH, vertex="A"),
    ]


def test_dfs_without_trace() -> None:
    order = dfs({}, "Z")
    assert order == ["Z"]


def test_dfs_sorts_neighbors_deterministically() -> None:
    graph = {"A": ["C", "B"], "B": [], "C": []}
    order = dfs(graph, "A")
    assert order == ["A", "B", "C"]


def test_dfs_sorts_set_neighbors() -> None:
    graph = {"A": {"C", "B"}, "B": [], "C": []}
    order = dfs(graph, "A")
    assert order == ["A", "B", "C"]


def test_dfs_unsortable_neighbors_raise_error() -> None:
    first = object()
    second = object()
    graph = {"A": [first, second], first: [], second: []}

    with pytest.raises(TypeError):
        dfs(graph, "A")
