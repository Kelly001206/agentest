"""The vendored catalogue CSVs must match the sha256 pins in catalog/VERSION (offline)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_pins_pass() -> None:
    """scripts/check_catalog_pins.py exits 0 on the committed catalogue."""
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_catalog_pins.py")], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "pin check passed" in p.stdout
