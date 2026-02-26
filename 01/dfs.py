from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Iterable, List, MutableSequence, Set, TypeVar, Generic

T = TypeVar("T")


class Step(Enum):
    START = auto()
    ENTER = auto()
    CHECK_NEIGHBOR = auto()
    VISIT_NEIGHBOR = auto()
    SKIP_VISITED = auto()
    EXIT = auto()
    FINISH = auto()


@dataclass(frozen=True)
class Event(Generic[T]):
    step: Step
    vertex: T | None = None
    neighbor: T | None = None


Graph = Dict[T, Iterable[T]]


def dfs(
    graph: Graph[T], start: T, trace: MutableSequence[Event[T]] | None = None
) -> List[T]:
    if trace is None:
        trace = []

    order: List[T] = []
    visited: Set[T] = set()

    trace.append(Event(Step.START, vertex=start))

    def visit(vertex: T) -> None:
        trace.append(Event(Step.ENTER, vertex=vertex))
        visited.add(vertex)
        order.append(vertex)

        neighbors_iter = graph.get(vertex, [])
        neighbors = list(neighbors_iter)
        if not isinstance(neighbors_iter, (list, tuple)):
            try:
                neighbors.sort()
            except TypeError:
                pass

        for neighbor in neighbors:
            trace.append(Event(Step.CHECK_NEIGHBOR, vertex=vertex, neighbor=neighbor))
            if neighbor in visited:
                trace.append(Event(Step.SKIP_VISITED, vertex=vertex, neighbor=neighbor))
                continue
            trace.append(Event(Step.VISIT_NEIGHBOR, vertex=vertex, neighbor=neighbor))
            visit(neighbor)

        trace.append(Event(Step.EXIT, vertex=vertex))

    visit(start)
    trace.append(Event(Step.FINISH, vertex=start))

    return order


__all__ = ["Event", "Step", "dfs"]
