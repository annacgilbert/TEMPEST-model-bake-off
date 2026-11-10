"""Scaffold checks for shared dataset modules."""

from tempest_bakeoff.data import datasets, generation, splits


def test_data_scaffold_is_importable() -> None:
    assert datasets.__doc__
    assert generation.__doc__
    assert splits.__doc__

