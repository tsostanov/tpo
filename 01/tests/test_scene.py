from __future__ import annotations

import pytest

from scene import ArthurState, CrowdState, OratorState, Scene, Window


def _scene() -> Scene:
    return Scene([Window("north", 2), Window("south", 2)])


def test_scene_happy_path() -> None:
    scene = _scene()

    assert scene.crowd_state == CrowdState.CALM
    assert scene.crowd_cheers() is True
    assert scene.crowd_state == CrowdState.CHEERING

    assert scene.start_oration() is True
    scene.place_scaffold("north")

    scene.arthur_glides_to("north")
    assert scene.arthur_state == ArthurState.GLIDING
    assert scene.target_window == "north"

    scene.arthur_reaches_window()
    assert scene.arthur_state == ArthurState.AT_WINDOW


def test_crowd_cheers_idempotent() -> None:
    scene = _scene()
    assert scene.crowd_cheers() is True
    assert scene.crowd_cheers() is False


def test_orator_start_idempotent() -> None:
    scene = _scene()
    assert scene.start_oration() is True
    assert scene.start_oration() is False


def test_place_scaffold_unknown_window() -> None:
    scene = _scene()
    with pytest.raises(KeyError):
        scene.place_scaffold("east")


def test_glide_unknown_window() -> None:
    scene = _scene()
    with pytest.raises(KeyError):
        scene.arthur_glides_to("east")


def test_glide_not_standing() -> None:
    scene = _scene()
    scene.start_oration()
    scene.place_scaffold("north")
    scene.arthur_glides_to("north")
    with pytest.raises(ValueError):
        scene.arthur_glides_to("north")


def test_glide_without_scaffold() -> None:
    scene = _scene()
    with pytest.raises(ValueError):
        scene.arthur_glides_to("north")


def test_glide_without_oration() -> None:
    scene = _scene()
    scene.place_scaffold("north")
    with pytest.raises(ValueError):
        scene.arthur_glides_to("north")


def test_reach_without_glide() -> None:
    scene = _scene()
    with pytest.raises(ValueError):
        scene.arthur_reaches_window()


def test_states_enums() -> None:
    assert ArthurState.STANDING != ArthurState.AT_WINDOW
    assert CrowdState.CALM != CrowdState.CHEERING
    assert OratorState.SILENT != OratorState.ADDRESSING
