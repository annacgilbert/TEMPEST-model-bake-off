#!/usr/bin/env python3
"""Generate benchmark data after the physical specification is approved."""

from __future__ import annotations


def main() -> None:
    """Refuse to generate data while the benchmark remains unspecified."""
    raise SystemExit(
        "Data generation is not implemented: approve the benchmark specification first."
    )


if __name__ == "__main__":
    main()

