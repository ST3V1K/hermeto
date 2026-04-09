# SPDX-License-Identifier: GPL-3.0-only
"""Mkdocs-macros hook that generates the exit-codes table from the ExitError enum."""

from typing import Any

from hermeto.core.errors import ErrorRegistryMeta


def define_env(env: Any) -> None:
    """Register mkdocs-macros variables."""
    lines = [
        "| Code | Category | Meaning |",
        "| ---: | -------- | ------- |",
    ]

    for exit_error, cls in sorted(ErrorRegistryMeta.registry.items(), key=lambda x: x[0].value):
        lines.append(f"| {exit_error.value} | {cls.category.value} | {cls.meaning} |")

    env.variables["exit_codes_table"] = "\n".join(lines)
