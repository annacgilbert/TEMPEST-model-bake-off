"""Minimal package provenance checks."""

import tempest_bakeoff


def test_package_exposes_version() -> None:
    assert tempest_bakeoff.__version__ == "0.0.1"

