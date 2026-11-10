#!/usr/bin/env python3
"""Build report inputs from saved machine-readable benchmark metrics."""

from __future__ import annotations


def main() -> None:
    """Refuse to synthesize report artifacts before metrics exist."""
    raise SystemExit(
        "Report synthesis is not implemented: no benchmark metrics are available."
    )


if __name__ == "__main__":
    main()

