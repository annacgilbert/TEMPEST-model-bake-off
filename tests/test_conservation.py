"""Conservation tests to implement with the reference simulator."""

import pytest


@pytest.mark.skip(reason="Reference equations and conserved quantities are undecided")
def test_reference_solver_conservation() -> None:
    """Measure conservation error against an approved tolerance."""

