"""Access to the Kaira specification, declaration schema, and conformance vectors.

Language implementations such as pykaira depend on this package to obtain the
normative test data without vendoring it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = [
    "conformance_path",
    "load_conformance",
    "schema_path",
    "specification_path",
]

_PACKAGE = Path(__file__).resolve().parent


def _resolve(installed: str, source: str) -> Path:
    # A wheel bundles the files under data/; an editable or source checkout
    # reads them from the repository root.
    candidate = _PACKAGE / "data" / installed
    if candidate.exists():
        return candidate
    candidate = _PACKAGE.parent.parent / source
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Kaira specification file not found: {installed}")


def specification_path() -> Path:
    """Return the path to the normative SPECIFICATION.md."""
    return _resolve("SPECIFICATION.md", "src/SPECIFICATION.md")


def schema_path(version: str = "v1") -> Path:
    """Return the path to the KORML command-declaration schema."""
    name = f"kaira.command-declaration.{version}.korml"
    return _resolve(f"schema/{name}", f"schema/{name}")


def conformance_path(version: str = "v1") -> Path:
    """Return the path to the conformance vectors for a specification version."""
    name = f"{version}.json"
    return _resolve(f"conformance/{name}", f"tests/conformance/{name}")


def load_conformance(version: str = "v1") -> dict[str, Any]:
    """Load the conformance vectors for a specification version."""
    with conformance_path(version).open(encoding="utf-8") as stream:
        return json.load(stream)
