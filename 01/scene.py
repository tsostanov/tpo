from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Iterable, Optional


class CrowdState(Enum):
    CALM = auto()
    CHEERING = auto()


class OratorState(Enum):
    SILENT = auto()
    ADDRESSING = auto()


class ArthurState(Enum):
    STANDING = auto()
    GLIDING = auto()
    AT_WINDOW = auto()


@dataclass(frozen=True)
class Window:
    name: str
    floor: int


class Scene:
    def __init__(self, windows: Iterable[Window]):
        self.windows: Dict[str, Window] = {window.name: window for window in windows}
        self.crowd_state = CrowdState.CALM
        self.orator_state = OratorState.SILENT
        self.arthur_state = ArthurState.STANDING
        self.scaffold_window: Optional[str] = None
        self.target_window: Optional[str] = None

    def crowd_cheers(self) -> None:
        if self.crowd_state == CrowdState.CHEERING:
            return
        self.crowd_state = CrowdState.CHEERING

    def start_oration(self) -> None:
        if self.scaffold_window is None:
            raise ValueError("no scaffold for oration")
        if self.orator_state == OratorState.ADDRESSING:
            return
        self.orator_state = OratorState.ADDRESSING

    def place_scaffold(self, window_name: str) -> None:
        if window_name not in self.windows:
            raise KeyError("unknown window")
        if self.windows[window_name].floor != 2:
            raise ValueError("scaffold must be at a second-floor window")
        self.scaffold_window = window_name

    def arthur_glides_to(self, window_name: str) -> None:
        if window_name not in self.windows:
            raise KeyError("unknown window")
        if self.arthur_state != ArthurState.STANDING:
            raise ValueError("arthur is not ready to glide")
        if self.scaffold_window != window_name:
            raise ValueError("no scaffold at target window")
        if self.orator_state != OratorState.ADDRESSING:
            raise ValueError("orator is not addressing the crowd")
        self.arthur_state = ArthurState.GLIDING
        self.target_window = window_name

    def arthur_reaches_window(self) -> None:
        if self.arthur_state != ArthurState.GLIDING:
            raise ValueError("arthur is not gliding")
        if self.target_window is None:
            raise ValueError("no target window")
        self.arthur_state = ArthurState.AT_WINDOW


__all__ = [
    "ArthurState",
    "CrowdState",
    "OratorState",
    "Scene",
    "Window",
]
