from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Iterable, Optional


class CrowdState(Enum):
    CALM = auto()
    CHEERING = auto()
    ECSTATIC = auto()


class OratorState(Enum):
    SILENT = auto()
    ADDRESSING = auto()


class ArthurState(Enum):
    STANDING = auto()
    GLIDING = auto()
    AFRAID = auto()
    IN_ROOM = auto()
    REALIZES_PROJECTION = auto()


@dataclass(frozen=True)
class Window:
    name: str
    floor: int


@dataclass(frozen=True)
class Podium:
    window_name: str


@dataclass
class Room:
    is_projection: bool = True

    def reacts_to_intrusion(self) -> bool:
        return not self.is_projection


@dataclass
class Crowd:
    state: CrowdState = CrowdState.CALM

    def cheer(self) -> None:
        if self.state == CrowdState.ECSTATIC:
            return
        self.state = CrowdState.CHEERING

    def shout_hurrah(self) -> None:
        if self.state == CrowdState.CALM:
            raise ValueError("crowd must already be cheering")
        self.state = CrowdState.ECSTATIC


@dataclass
class Orator:
    state: OratorState = OratorState.SILENT

    def start(self, podium: Podium | None) -> None:
        if podium is None:
            raise ValueError("no podium for oration")
        if self.state == OratorState.ADDRESSING:
            return
        self.state = OratorState.ADDRESSING

    def continue_addressing(self, crowd: Crowd) -> None:
        if self.state != OratorState.ADDRESSING:
            raise ValueError("orator is not addressing the crowd")
        crowd.shout_hurrah()


@dataclass
class Arthur:
    state: ArthurState = ArthurState.STANDING
    target_window: Optional[str] = None
    feels_fear: bool = False
    understands_projection: bool = False

    def begin_glide(self, target_window: str) -> None:
        if self.state != ArthurState.STANDING:
            raise ValueError("arthur is not ready to glide")
        self.state = ArthurState.GLIDING
        self.target_window = target_window

    def approach_window(self) -> None:
        if self.state != ArthurState.GLIDING:
            raise ValueError("arthur is not gliding")
        if self.target_window is None:
            raise ValueError("no target window")
        self.state = ArthurState.AFRAID
        self.feels_fear = True

    def pass_through_glass(self) -> None:
        if self.state != ArthurState.AFRAID:
            raise ValueError("arthur is not approaching the window")
        self.state = ArthurState.IN_ROOM
        self.feels_fear = False

    def realize_projection(self, room: Room) -> None:
        if self.state != ArthurState.IN_ROOM:
            raise ValueError("arthur is not inside the room")
        if room.reacts_to_intrusion():
            raise ValueError("the room reacts to intrusion")
        self.state = ArthurState.REALIZES_PROJECTION
        self.understands_projection = True


class Scene:
    def __init__(self, windows: Iterable[Window], room: Room | None = None):
        self.windows: Dict[str, Window] = {window.name: window for window in windows}
        self.crowd = Crowd()
        self.orator = Orator()
        self.arthur = Arthur()
        self.podium: Podium | None = None
        self.room = Room() if room is None else room

    @property
    def crowd_state(self) -> CrowdState:
        return self.crowd.state

    @property
    def orator_state(self) -> OratorState:
        return self.orator.state

    @property
    def arthur_state(self) -> ArthurState:
        return self.arthur.state

    @property
    def target_window(self) -> Optional[str]:
        return self.arthur.target_window

    def crowd_cheers(self) -> None:
        self.crowd.cheer()

    def crowd_shouts_hurrah(self) -> None:
        self.crowd.shout_hurrah()

    def place_podium(self, window_name: str) -> None:
        if window_name not in self.windows:
            raise KeyError("unknown window")
        if self.windows[window_name].floor != 2:
            raise ValueError("podium must be at a second-floor window")
        self.podium = Podium(window_name)

    def start_oration(self) -> None:
        self.orator.start(self.podium)

    def continue_oration(self) -> None:
        self.orator.continue_addressing(self.crowd)

    def arthur_glides_to(self, window_name: str) -> None:
        if window_name not in self.windows:
            raise KeyError("unknown window")
        if self.podium is None or self.podium.window_name != window_name:
            raise ValueError("no podium at target window")
        if self.orator.state != OratorState.ADDRESSING:
            raise ValueError("orator is not addressing the crowd")
        if self.crowd.state != CrowdState.ECSTATIC:
            raise ValueError("crowd is not ecstatic")
        self.arthur.begin_glide(window_name)

    def arthur_approaches_window(self) -> None:
        self.arthur.approach_window()

    def arthur_passes_through_glass(self) -> None:
        self.arthur.pass_through_glass()

    def arthur_realizes_projection(self) -> None:
        self.arthur.realize_projection(self.room)


__all__ = [
    "Arthur",
    "ArthurState",
    "Crowd",
    "CrowdState",
    "Orator",
    "OratorState",
    "Podium",
    "Room",
    "Scene",
    "Window",
]
