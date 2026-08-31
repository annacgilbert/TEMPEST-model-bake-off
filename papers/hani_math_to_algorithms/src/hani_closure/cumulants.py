"""Dependency-free joint cumulants for small estimator tests.

Production estimators will need streaming, bias-corrected, and array-oriented
implementations. This module exists to make the partition convention exact.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from math import factorial


def _partitions(items: tuple[int, ...]) -> Iterator[tuple[tuple[int, ...], ...]]:
    """Yield every set partition of ``items`` exactly once."""

    if not items:
        yield ()
        return

    first, rest = items[0], items[1:]
    for partition in _partitions(rest):
        yield ((first,),) + partition
        for index in range(len(partition)):
            block = partition[index]
            yield partition[:index] + ((first,) + block,) + partition[index + 1 :]


def _moment(samples: Sequence[Sequence[float]], indices: tuple[int, ...]) -> float:
    total = 0.0
    for sample in samples:
        product = 1.0
        for index in indices:
            product *= float(sample[index])
        total += product
    return total / len(samples)


def joint_cumulant(samples: Sequence[Sequence[float]]) -> float:
    """Return the empirical joint cumulant of the columns in ``samples``.

    The estimator is the plug-in moment-to-cumulant formula. It is not an
    unbiased finite-sample k-statistic.
    """

    if not samples:
        raise ValueError("samples must be non-empty")
    order = len(samples[0])
    if order == 0:
        raise ValueError("samples must contain at least one variable")
    if any(len(sample) != order for sample in samples):
        raise ValueError("all samples must have the same number of variables")

    result = 0.0
    for partition in _partitions(tuple(range(order))):
        blocks = len(partition)
        coefficient = factorial(blocks - 1) * (-1) ** (blocks - 1)
        product = 1.0
        for block in partition:
            product *= _moment(samples, block)
        result += coefficient * product
    return result

