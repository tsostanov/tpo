from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterable, Optional


class CrowdState(Enum):
    CALM = auto()
    CHEERING = auto()
    ECSTATIC = auto()


class OratorState(Enum):
    SILENT = auto()
    ADDRESSING = auto()


class OratorPosition(Enum):
    OFF_PODIUM = auto()
    ON_PODIUM = auto()


class ArthurState(Enum):
    STANDING = auto()
    GLIDING = auto()
    NEAR_WINDOW = auto()
    IN_ROOM = auto()
    REALIZES_PROJECTION = auto()


@dataclass(frozen=True)
class Window:
    direction: str
    floor: int


@dataclass(frozen=True)
class Podium:
    window: Window


@dataclass
class Room:
    is_projection: bool = True

    def reacts_to_intrusion(self) -> bool:
        return not self.is_projection


@dataclass
class Building:
    windows: tuple[Window, ...]
    room: Room

    @classmethod
    def from_windows(
        cls, windows: Iterable[Window], room: Room | None = None
    ) -> Building:
        return cls(
            windows=tuple(windows),
            room=Room() if room is None else room,
        )

    def require_window(self, window: Window) -> Window:
        for building_window in self.windows:
            if building_window.direction != window.direction:
                continue
            if building_window is not window:
                raise ValueError("window does not belong to this building")
            return building_window
        raise KeyError("unknown window")


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
    position: OratorPosition = OratorPosition.OFF_PODIUM

    def climb_podium(self, podium: Podium | None) -> None:
        if podium is None:
            raise ValueError("no podium to climb")
        if self.position == OratorPosition.ON_PODIUM:
            return
        self.position = OratorPosition.ON_PODIUM

    def step_down(self) -> None:
        if self.position == OratorPosition.OFF_PODIUM:
            return
        self.position = OratorPosition.OFF_PODIUM

    def start(self) -> None:
        if self.state == OratorState.ADDRESSING:
            return
        self.state = OratorState.ADDRESSING

    def continue_addressing(self, crowd: Crowd) -> None:
        if self.state != OratorState.ADDRESSING:
            raise ValueError("orator is not addressing the crowd")
        if self.position != OratorPosition.ON_PODIUM:
            return
        crowd.shout_hurrah()


@dataclass
class Arthur:
    state: ArthurState = ArthurState.STANDING
    target_window: Optional[Window] = None
    distance_to_target: Optional[float] = None
    feels_fear: bool = False
    understands_projection: bool = False

    @property
    def has_reached_window(self) -> bool:
        return self.state in {
            ArthurState.NEAR_WINDOW,
            ArthurState.IN_ROOM,
            ArthurState.REALIZES_PROJECTION,
        }

    def begin_glide(self, target_window: Window, distance_to_target: float) -> None:
        if self.state != ArthurState.STANDING:
            raise ValueError("arthur is not ready to glide")
        if distance_to_target <= 0:
            raise ValueError("distance to target must be positive")
        self.state = ArthurState.GLIDING
        self.target_window = target_window
        self.distance_to_target = distance_to_target

    def move_closer(self, distance: float) -> None:
        if self.state != ArthurState.GLIDING:
            raise ValueError("arthur is not gliding")
        if self.target_window is None:
            raise ValueError("no target window")
        if self.distance_to_target is None:
            raise ValueError("no distance to target")
        if distance <= 0:
            raise ValueError("distance step must be positive")

        remaining_distance = self.distance_to_target - distance
        if remaining_distance <= 0:
            self.distance_to_target = 0.0
            self.state = ArthurState.NEAR_WINDOW
            self.feels_fear = True
            return

        self.distance_to_target = remaining_distance

    def pass_through_glass(self) -> None:
        if self.state != ArthurState.NEAR_WINDOW:
            raise ValueError("arthur is not approaching the window")
        self.state = ArthurState.IN_ROOM
        self.distance_to_target = 0.0
        self.feels_fear = False

    def realize_projection(self, room: Room) -> None:
        if self.state != ArthurState.IN_ROOM:
            raise ValueError("arthur is not inside the room")
        if room.reacts_to_intrusion():
            raise ValueError("the room reacts to intrusion")
        self.state = ArthurState.REALIZES_PROJECTION
        self.understands_projection = True


class Scene:
    def __init__(self, building: Building):
        self.building = building
        self.crowd = Crowd()
        self.orator = Orator()
        self.arthur = Arthur()
        self.podium: Podium | None = None

    @property
    def windows(self) -> tuple[Window, ...]:
        return self.building.windows

    @property
    def room(self) -> Room:
        return self.building.room

    @property
    def crowd_state(self) -> CrowdState:
        return self.crowd.state

    @property
    def orator_state(self) -> OratorState:
        return self.orator.state

    @property
    def orator_position(self) -> OratorPosition:
        return self.orator.position

    @property
    def arthur_state(self) -> ArthurState:
        return self.arthur.state

    @property
    def target_window(self) -> Optional[Window]:
        return self.arthur.target_window

    @property
    def distance_to_target(self) -> Optional[float]:
        return self.arthur.distance_to_target

    @property
    def has_reached_window(self) -> bool:
        return self.arthur.has_reached_window

    def crowd_cheers(self) -> None:
        self.crowd.cheer()

    def crowd_shouts_hurrah(self) -> None:
        self.crowd.shout_hurrah()

    def place_podium(self, window: Window) -> None:
        building_window = self.building.require_window(window)
        if building_window.floor != 2:
            raise ValueError("podium must be at a second-floor window")
        self.podium = Podium(building_window)

    def orator_climbs_podium(self) -> None:
        self.orator.climb_podium(self.podium)

    def orator_steps_down(self) -> None:
        self.orator.step_down()

    def start_oration(self) -> None:
        self.orator.start()

    def continue_oration(self) -> None:
        self.orator.continue_addressing(self.crowd)

    def arthur_glides_to(
        self, window: Window, distance_to_target: float = 10.0
    ) -> None:
        building_window = self.building.require_window(window)
        if self.podium is None or self.podium.window is not building_window:
            raise ValueError("no podium at target window")
        if self.orator.state != OratorState.ADDRESSING:
            raise ValueError("orator is not addressing the crowd")
        if self.orator.position != OratorPosition.ON_PODIUM:
            raise ValueError("orator is not on the podium")
        if self.crowd.state != CrowdState.ECSTATIC:
            raise ValueError("crowd is not ecstatic")
        self.arthur.begin_glide(building_window, distance_to_target)

    def arthur_moves_closer(self, distance: float) -> None:
        self.arthur.move_closer(distance)

    def arthur_passes_through_glass(self) -> None:
        self.arthur.pass_through_glass()

    def arthur_realizes_projection(self) -> None:
        self.arthur.realize_projection(self.building.room)


__all__ = [
    "Arthur",
    "ArthurState",
    "Building",
    "Crowd",
    "CrowdState",
    "Orator",
    "OratorPosition",
    "OratorState",
    "Podium",
    "Room",
    "Scene",
    "Window",
]
