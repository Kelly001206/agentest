"""Offline catalog sync check must pass against vendored VERSION hashes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_hub_sync.py"


def test_offline_hub_sync_check_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "sync check passed" in proc.stdout
