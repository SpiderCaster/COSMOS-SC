#!/usr/bin/env python3
"""Compat shim - the CLI is spidercaster.py now. This file only forwards."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("spidercaster.py")), run_name="__main__")
