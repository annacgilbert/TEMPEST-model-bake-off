"""Scaffold checks for the planned model-family namespaces."""

from tempest_bakeoff import (
    baselines,
    learned_closure,
    neural_ode,
    neural_operator,
    pinn,
    pino,
    world_model,
)


def test_model_family_scaffolds_are_importable() -> None:
    modules = (
        baselines,
        pinn,
        neural_operator,
        pino,
        learned_closure,
        neural_ode,
        world_model,
    )
    assert all(module.__doc__ for module in modules)

