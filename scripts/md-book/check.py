#!/usr/bin/env python3
"""Compatibility entry point for the renamed mdBook checker."""

from pathlib import Path
import runpy
import sys

BUILDER = Path(__file__).resolve().parent.parent / "md-book-builder"

if __name__ == "__main__":
    sys.path.insert(0, str(BUILDER))
    runpy.run_path(str(BUILDER / "check.py"), run_name="__main__")
