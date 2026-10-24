"""Offline catalog sync check must pass against vendored VERSION hashes.

What this module verifies: the vendored catalogue CSVs/VERSION pins match the Hugging Face
Hub release (offline hash check), so runner IDs never drift from the design authority. Hub catalogue doi:10.5281/zenodo.23587407.
Full bibliography: docs/REFERENCES.md.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_hub_sync.py"


def test_offline_hub_sync_check_passes() -> None:
    """scripts/check_hub_sync.py offline mode: pinned catalogue CSVs/VERSION match the Hub snapshot."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "sync check passed" in proc.stdout
