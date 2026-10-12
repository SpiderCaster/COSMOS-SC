import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "_lib"))
from harness import run_item
sys.exit(run_item(__file__))
