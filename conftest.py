"""Add src/ to sys.path so that `pomo.*` imports resolve."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
