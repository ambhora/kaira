#!/usr/bin/env python3
"""Copy the normative source into the ProperDocs input tree without editing it."""

from pathlib import Path
import shutil

root = Path(__file__).resolve().parent.parent
source = root / "src" / "SPECIFICATION.md"
destination = root / "docs" / "reference" / "specification.md"
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, destination)
