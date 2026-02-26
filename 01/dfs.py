from __future__ import annotations

from enum import Enum, auto
from typing import Dict, Iterable, List, MutableSequence, Set, TypeVar

T = TypeVar("T")


class Step(Enum):
    START = auto()
    ENTER = auto()
    CHECK_NEIGHBOR = auto()
    VISIT_NEIGHBOR = auto()
    SKIP_VISITED = auto()
    EXIT = auto()
    FINISH = auto()


Graph = Dict[T, Iterable[T]]


def dfs(
    graph: Graph[T], start: T, trace: MutableSequence[Step] | None = None
) -> List[T]:
    if trace is None:
        trace = []

    order: List[T] = []
    visited: Set[T] = set()

    trace.append(Step.START)

    def visit(vertex: T) -> None:
        trace.append(Step.ENTER)
        visited.add(vertex)
        order.append(vertex)

        for neighbor in graph.get(vertex, []):
            trace.append(Step.CHECK_NEIGHBOR)
            if neighbor in visited:
                trace.append(Step.SKIP_VISITED)
                continue
            trace.append(Step.VISIT_NEIGHBOR)
            visit(neighbor)

        trace.append(Step.EXIT)

    visit(start)
    trace.append(Step.FINISH)

    return order


__all__ = ["Step", "dfs"]
