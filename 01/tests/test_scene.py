from __future__ import annotations

import pytest

from scene import ArthurState, CrowdState, OratorState, Room, Scene, Window


def _scene() -> Scene:
    return Scene([Window("north", 2), Window("south", 2)])


def _scene_with_ground_floor() -> Scene:
    return Scene([Window("north", 1), Window("south", 2)])


def _reactive_room_scene() -> Scene:
    return Scene([Window("north", 2)], room=Room(is_projection=False))


def test_scene_happy_path() -> None:
    scene = _scene()

    assert scene.crowd_state == CrowdState.CALM
    assert scene.orator_state == OratorState.SILENT
    assert scene.arthur_state == ArthurState.STANDING
    assert scene.target_window is None

    scene.crowd_cheers()
    assert scene.crowd_state == CrowdState.CHEERING

    scene.place_podium("north")
    scene.start_oration()
    scene.continue_oration()
    assert scene.orator_state == OratorState.ADDRESSING
    assert scene.crowd_state == CrowdState.ECSTATIC

    scene.arthur_glides_to("north")
    assert scene.arthur_state == ArthurState.GLIDING
    assert scene.target_window == "north"

    scene.arthur_approaches_window()
    assert scene.arthur_state == ArthurState.AFRAID
    assert scene.arthur.feels_fear is True

    scene.arthur_passes_through_glass()
    assert scene.arthur_state == ArthurState.IN_ROOM
    assert scene.arthur.feels_fear is False
    assert scene.room.reacts_to_intrusion() is False

    scene.arthur_realizes_projection()
    assert scene.arthur_state == ArthurState.REALIZES_PROJECTION
    assert scene.arthur.understands_projection is True


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
    scene.place_podium("north")
    scene.start_oration()
    scene.start_oration()
    assert scene.orator_state == OratorState.ADDRESSING


def test_continue_oration_requires_active_speech() -> None:
    scene = _scene()
    with pytest.raises(ValueError, match="orator is not addressing the crowd"):
        scene.continue_oration()


def test_continue_oration_pushes_crowd_to_ecstasy() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.place_podium("north")
    scene.start_oration()

    scene.continue_oration()

    assert scene.crowd_state == CrowdState.ECSTATIC


def test_start_oration_without_podium() -> None:
    scene = _scene()
    with pytest.raises(ValueError, match="no podium for oration"):
        scene.start_oration()


def test_place_podium_unknown_window() -> None:
    scene = _scene()
    with pytest.raises(KeyError, match="unknown window"):
        scene.place_podium("east")


def test_place_podium_wrong_floor() -> None:
    scene = _scene_with_ground_floor()
    with pytest.raises(ValueError, match="podium must be at a second-floor window"):
        scene.place_podium("north")


def test_glide_unknown_window() -> None:
    scene = _scene()
    with pytest.raises(KeyError, match="unknown window"):
        scene.arthur_glides_to("east")


def test_glide_not_standing() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.place_podium("north")
    scene.start_oration()
    scene.continue_oration()
    scene.arthur_glides_to("north")

    with pytest.raises(ValueError, match="arthur is not ready to glide"):
        scene.arthur_glides_to("north")


def test_glide_without_podium() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.orator.state = OratorState.ADDRESSING
    scene.crowd.state = CrowdState.ECSTATIC

    with pytest.raises(ValueError, match="no podium at target window"):
        scene.arthur_glides_to("north")


def test_glide_without_oration() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.crowd_shouts_hurrah()
    scene.place_podium("north")

    with pytest.raises(ValueError, match="orator is not addressing the crowd"):
        scene.arthur_glides_to("north")


def test_glide_requires_ecstatic_crowd() -> None:
    scene = _scene()
    scene.crowd_cheers()
    scene.place_podium("north")
    scene.start_oration()

    with pytest.raises(ValueError, match="crowd is not ecstatic"):
        scene.arthur_glides_to("north")


def test_approach_without_glide() -> None:
    scene = _scene()
    with pytest.raises(ValueError, match="arthur is not gliding"):
        scene.arthur_approaches_window()


def test_approach_without_target_window_in_gliding_state() -> None:
    scene = _scene()
    scene.arthur.state = ArthurState.GLIDING
    scene.arthur.target_window = None

    with pytest.raises(ValueError, match="no target window"):
        scene.arthur_approaches_window()


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
    scene.crowd_cheers()
    scene.place_podium("north")
    scene.start_oration()
    scene.continue_oration()
    scene.arthur_glides_to("north")
    scene.arthur_approaches_window()
    scene.arthur_passes_through_glass()

    with pytest.raises(ValueError, match="the room reacts to intrusion"):
        scene.arthur_realizes_projection()


def test_enum_values_are_unique() -> None:
    assert len({state.value for state in ArthurState}) == len(ArthurState)
    assert len({state.value for state in CrowdState}) == len(CrowdState)
    assert len({state.value for state in OratorState}) == len(OratorState)
