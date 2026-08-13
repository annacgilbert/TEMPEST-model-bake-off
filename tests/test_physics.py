"""Scaffold checks for the physical-model package."""

from tempest_bakeoff.physics import diagnostics, discretization, equations, simulator


def test_physics_scaffold_is_importable() -> None:
    assert equations.__doc__
    assert discretization.__doc__
    assert simulator.__doc__
    assert diagnostics.__doc__

