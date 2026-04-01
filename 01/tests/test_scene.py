from __future__ import annotations

import pytest

from scene import (
    ArthurState,
    Building,
    CrowdState,
    OratorPosition,
    OratorState,
    Room,
    Scene,
    Window,
)


def _scene() -> Scene:
    return Scene(Building.from_windows([Window("north", 2), Window("south", 2)]))


def _scene_with_ground_floor() -> Scene:
    return Scene(Building.from_windows([Window("north", 1), Window("south", 2)]))


def _reactive_room_scene() -> Scene:
    return Scene(
        Building.from_windows([Window("north", 2)], room=Room(is_projection=False))
    )


def _window(scene: Scene, direction: str) -> Window:
    return next(window for window in scene.windows if window.direction == direction)


def test_scene_happy_path() -> None:
    scene = _scene()
    north = _window(scene, "north")

    assert scene.crowd_state == CrowdState.CALM
    assert scene.orator_state == OratorState.SILENT
    assert scene.orator_position == OratorPosition.OFF_PODIUM
    assert scene.arthur_state == ArthurState.STANDING
    assert scene.target_window is None
    assert scene.has_reached_window is False

    scene.crowd_cheers()
    assert scene.crowd_state == CrowdState.CHEERING

    scene.place_podium(north)
    scene.orator_climbs_podium()
    scene.start_oration()
    scene.continue_oration()
    assert scene.orator_state == OratorState.ADDRESSING
    assert scene.orator_position == OratorPosition.ON_PODIUM
    assert scene.crowd_state == CrowdState.ECSTATIC

    scene.arthur_glides_to(north, distance_to_target=5.0)
    assert scene.arthur_state == ArthurState.GLIDING
    assert scene.target_window is north
    assert scene.distance_to_target == pytest.approx(5.0)
    assert scene.has_reached_window is False

    scene.arthur_moves_closer(3.0)
    assert scene.arthur_state == ArthurState.GLIDING
    assert scene.distance_to_target == pytest.approx(2.0)
    assert scene.arthur.feels_fear is False
    assert scene.has_reached_window is False

    scene.arthur_moves_closer(2.0)
    assert scene.arthur_state == ArthurState.NEAR_WINDOW
    assert scene.distance_to_target == pytest.approx(0.0)
    assert scene.arthur.feels_fear is True
    assert scene.has_reached_window is True

    scene.arthur_passes_through_glass()
    assert scene.arthur_state == ArthurState.IN_ROOM
    assert scene.arthur.feels_fear is False
    assert scene.room.reacts_to_intrusion() is False
    assert scene.has_reached_window is True

    scene.arthur_realizes_projection()
    assert scene.arthur_state == ArthurState.REALIZES_PROJECTION
    assert scene.arthur.understands_projection is True
    assert scene.has_reached_window is True


def test_crowd_cheers_idempotent() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.crowd_cheers()
    assert scene.crowd_state == CrowdState.CHEERING


def test_crowd_cheers_keeps_ecstatic_state() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.crowd_shouts_hurrah()

    scene.crowd_cheers()

    assert scene.crowd_state == CrowdState.ECSTATIC


def test_crowd_shouts_hurrah_requires_cheering() -> None:
    scene = _scene()
    with pytest.raises(ValueError, match="crowd must already be cheering"):
        scene.crowd_shouts_hurrah()


def test_orator_start_idempotent() -> None:
    scene = _scene()
    scene.start_oration()
    scene.start_oration()
    assert scene.orator_state == OratorState.ADDRESSING


def test_orator_climbs_podium_idempotent() -> None:
    scene = _scene()
    scene.place_podium(_window(scene, "north"))
    scene.orator_climbs_podium()
    scene.orator_climbs_podium()
    assert scene.orator_position == OratorPosition.ON_PODIUM


def test_orator_can_address_without_podium_but_crowd_stays_cheering() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.start_oration()

    scene.continue_oration()

    assert scene.orator_state == OratorState.ADDRESSING
    assert scene.orator_position == OratorPosition.OFF_PODIUM
    assert scene.crowd_state == CrowdState.CHEERING


def test_continue_oration_requires_active_speech() -> None:
    scene = _scene()
    with pytest.raises(ValueError, match="orator is not addressing the crowd"):
        scene.continue_oration()


def test_continue_oration_pushes_crowd_to_ecstasy() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.place_podium(_window(scene, "north"))
    scene.orator_climbs_podium()
    scene.start_oration()

    scene.continue_oration()

    assert scene.crowd_state == CrowdState.ECSTATIC


def test_orator_climbs_without_podium() -> None:
    scene = _scene()
    with pytest.raises(ValueError, match="no podium to climb"):
        scene.orator_climbs_podium()


def test_orator_steps_down_from_podium() -> None:
    scene = _scene()
    scene.place_podium(_window(scene, "north"))
    scene.orator_climbs_podium()

    scene.orator_steps_down()

    assert scene.orator_position == OratorPosition.OFF_PODIUM


def test_orator_steps_down_idempotent() -> None:
    scene = _scene()

    scene.orator_steps_down()

    assert scene.orator_position == OratorPosition.OFF_PODIUM


def test_place_podium_unknown_window() -> None:
    scene = _scene()
    with pytest.raises(KeyError, match="unknown window"):
        scene.place_podium(Window("east", 2))


def test_place_podium_window_from_another_scene() -> None:
    scene = _scene()
    foreign_window = _window(_scene(), "north")

    with pytest.raises(ValueError, match="window does not belong to this building"):
        scene.place_podium(foreign_window)


def test_place_podium_wrong_floor() -> None:
    scene = _scene_with_ground_floor()
    with pytest.raises(ValueError, match="podium must be at a second-floor window"):
        scene.place_podium(_window(scene, "north"))


def test_glide_unknown_window() -> None:
    scene = _scene()
    with pytest.raises(KeyError, match="unknown window"):
        scene.arthur_glides_to(Window("east", 2))


def test_glide_window_from_another_scene() -> None:
    scene = _scene()
    foreign_window = _window(_scene(), "north")

    with pytest.raises(ValueError, match="window does not belong to this building"):
        scene.arthur_glides_to(foreign_window)


def test_glide_not_standing() -> None:
    scene = _scene()
    north = _window(scene, "north")
    scene.crowd_cheers()
    scene.place_podium(north)
    scene.orator_climbs_podium()
    scene.start_oration()
    scene.continue_oration()
    scene.arthur_glides_to(north)

    with pytest.raises(ValueError, match="arthur is not ready to glide"):
        scene.arthur_glides_to(north)


def test_glide_requires_positive_initial_distance() -> None:
    scene = _scene()
    north = _window(scene, "north")
    scene.crowd_cheers()
    scene.place_podium(north)
    scene.orator_climbs_podium()
    scene.start_oration()
    scene.continue_oration()

    with pytest.raises(ValueError, match="distance to target must be positive"):
        scene.arthur_glides_to(north, distance_to_target=0.0)


def test_glide_without_podium() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.orator.state = OratorState.ADDRESSING
    scene.orator.position = OratorPosition.ON_PODIUM
    scene.crowd.state = CrowdState.ECSTATIC

    with pytest.raises(ValueError, match="no podium at target window"):
        scene.arthur_glides_to(_window(scene, "north"))


def test_glide_without_oration() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.crowd_shouts_hurrah()
    scene.place_podium(_window(scene, "north"))
    scene.orator_climbs_podium()

    with pytest.raises(ValueError, match="orator is not addressing the crowd"):
        scene.arthur_glides_to(_window(scene, "north"))


def test_glide_requires_orator_on_podium() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.crowd_shouts_hurrah()
    scene.place_podium(_window(scene, "north"))
    scene.start_oration()

    with pytest.raises(ValueError, match="orator is not on the podium"):
        scene.arthur_glides_to(_window(scene, "north"))


def test_glide_requires_ecstatic_crowd() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.place_podium(_window(scene, "north"))
    scene.orator_climbs_podium()
    scene.start_oration()

    with pytest.raises(ValueError, match="crowd is not ecstatic"):
        scene.arthur_glides_to(_window(scene, "north"))


def test_move_closer_without_glide() -> None:
    scene = _scene()
    with pytest.raises(ValueError, match="arthur is not gliding"):
        scene.arthur_moves_closer(1.0)


def test_move_closer_without_target_window_in_gliding_state() -> None:
    scene = _scene()
    scene.arthur.state = ArthurState.GLIDING
    scene.arthur.target_window = None

    with pytest.raises(ValueError, match="no target window"):
        scene.arthur_moves_closer(1.0)


def test_move_closer_without_distance_in_gliding_state() -> None:
    scene = _scene()
    scene.arthur.state = ArthurState.GLIDING
    scene.arthur.target_window = _window(scene, "north")
    scene.arthur.distance_to_target = None

    with pytest.raises(ValueError, match="no distance to target"):
        scene.arthur_moves_closer(1.0)


def test_move_closer_requires_positive_step() -> None:
    scene = _scene()
    north = _window(scene, "north")
    scene.crowd_cheers()
    scene.place_podium(north)
    scene.orator_climbs_podium()
    scene.start_oration()
    scene.continue_oration()
    scene.arthur_glides_to(north)

    with pytest.raises(ValueError, match="distance step must be positive"):
        scene.arthur_moves_closer(0.0)


def test_has_reached_window_changes_after_arrival() -> None:
    scene = _scene()
    north = _window(scene, "north")
    scene.crowd_cheers()
    scene.place_podium(north)
    scene.orator_climbs_podium()
    scene.start_oration()
    scene.continue_oration()
    scene.arthur_glides_to(north, distance_to_target=3.0)

    assert scene.has_reached_window is False

    scene.arthur_moves_closer(2.0)
    assert scene.has_reached_window is False

    scene.arthur_moves_closer(1.0)
    assert scene.has_reached_window is True


def test_pass_through_glass_requires_approach() -> None:
    scene = _scene()
    with pytest.raises(ValueError, match="arthur is not approaching the window"):
        scene.arthur_passes_through_glass()


def test_realize_projection_requires_in_room() -> None:
    scene = _scene()
    with pytest.raises(ValueError, match="arthur is not inside the room"):
        scene.arthur_realizes_projection()


def test_realize_projection_fails_when_room_reacts() -> None:
    scene = _reactive_room_scene()
    north = _window(scene, "north")
    scene.crowd_cheers()
    scene.place_podium(north)
    scene.orator_climbs_podium()
    scene.start_oration()
    scene.continue_oration()
    scene.arthur_glides_to(north)
    scene.arthur_moves_closer(10.0)
    scene.arthur_passes_through_glass()

    with pytest.raises(ValueError, match="the room reacts to intrusion"):
        scene.arthur_realizes_projection()


def test_enum_values_are_unique() -> None:
    assert len({state.value for state in ArthurState}) == len(ArthurState)
    assert len({state.value for state in CrowdState}) == len(CrowdState)
    assert len({state.value for state in OratorPosition}) == len(OratorPosition)
    assert len({state.value for state in OratorState}) == len(OratorState)


def test_building_require_window_returns_same_object() -> None:
    building = Building.from_windows([Window("north", 2)])
    north = building.windows[0]

    assert building.require_window(north) is north


def test_building_uses_default_projection_room() -> None:
    building = Building.from_windows([Window("north", 2)])

    assert building.room.is_projection is True
