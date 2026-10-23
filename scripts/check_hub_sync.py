#!/usr/bin/env python3
"""Offline (and optional live) Hub ↔ GitHub catalog sync check.

Hub is the design authority for pack CSVs. This repo vendors the runnable
subset under catalog/. CI runs the offline mode only so no network/token
is required.

Usage:
  python scripts/check_hub_sync.py              # offline: VERSION hashes
  python scripts/check_hub_sync.py --live       # also download Hub packs
  python scripts/check_hub_sync.py --write-hashes  # refresh sha256_* in VERSION
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
VERSION_PATH = CATALOG / "VERSION"

PACKS_IN_SCOPE_KEY = "packs_in_scope"
SHA_PREFIX = "sha256_"
HUB_DATASET_DEFAULT = "srinivaspadmanabhuni/agentic-ai-test-checklist-110"


def _parse_version(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        out[key.strip()] = val.strip()
    return out


def _packs(meta: dict[str, str]) -> list[str]:
    raw = meta.get(PACKS_IN_SCOPE_KEY, "")
    packs = [p.strip() for p in raw.split(",") if p.strip()]
    if not packs:
        raise SystemExit(f"missing {PACKS_IN_SCOPE_KEY} in {VERSION_PATH}")
    return packs


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_hashes(meta: dict[str, str], packs: list[str]) -> None:
    """Rewrite VERSION preserving order; upsert sha256_* lines after packs_in_scope."""
    original = VERSION_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    hashes = {f"{SHA_PREFIX}{p}": _sha256_file(CATALOG / f"{p}.csv") for p in packs}
    # Drop old sha256_* lines; insert fresh block after packs_in_scope
    kept: list[str] = []
    inserted = False
    for line in original:
        stripped = line.strip()
        if stripped.startswith(SHA_PREFIX) and ":" in stripped:
            continue
        kept.append(line)
        key = stripped.partition(":")[0].strip() if ":" in stripped else ""
        if key == PACKS_IN_SCOPE_KEY and not inserted:
            for name in packs:
                kept.append(f"{SHA_PREFIX}{name}: {hashes[f'{SHA_PREFIX}{name}']}\n")
            inserted = True
    if not inserted:
        for p in packs:
            kept.append(f"{SHA_PREFIX}{p}: {hashes[f'{SHA_PREFIX}{p}']}\n")
    VERSION_PATH.write_text("".join(kept), encoding="utf-8")
    print(f"updated {VERSION_PATH} with {len(packs)} sha256 lines")


def check_offline(meta: dict[str, str], packs: list[str]) -> list[str]:
    errors: list[str] = []
    for p in packs:
        path = CATALOG / f"{p}.csv"
        if not path.is_file():
            errors.append(f"missing catalog file: {path}")
            continue
        actual = _sha256_file(path)
        expected = meta.get(f"{SHA_PREFIX}{p}")
        if not expected:
            errors.append(f"missing {SHA_PREFIX}{p} in catalog/VERSION (run --write-hashes)")
            continue
        if actual != expected:
            errors.append(f"{p}.csv hash mismatch: expected {expected}, got {actual}")
        else:
            print(f"OK offline  {p}.csv  {actual[:12]}…")
    # VERSION itself must mention hub_revision
    if not meta.get("hub_revision"):
        errors.append("catalog/VERSION missing hub_revision")
    else:
        print(f"OK VERSION  hub_revision={meta['hub_revision']}")
    return errors


def check_live(meta: dict[str, str], packs: list[str]) -> list[str]:
    dataset = meta.get("hub_dataset", HUB_DATASET_DEFAULT)
    errors: list[str] = []
    base = f"https://huggingface.co/datasets/{dataset}/resolve/main/packs"
    with tempfile.TemporaryDirectory(prefix="agentest-hub-sync-") as tmp:
        tmp_path = Path(tmp)
        for p in packs:
            url = f"{base}/{p}.csv"
            dest = tmp_path / f"{p}.csv"
            try:
                urllib.request.urlretrieve(url, dest)  # noqa: S310 — public Hub URL
            except urllib.error.URLError as exc:
                errors.append(f"live download failed for {p}: {exc}")
                continue
            local = CATALOG / f"{p}.csv"
            hub_hash = _sha256_file(dest)
            local_hash = _sha256_file(local)
            if hub_hash != local_hash:
                errors.append(
                    f"live mismatch {p}.csv hub={hub_hash} local={local_hash}"
                )
            else:
                print(f"OK live     {p}.csv  matches Hub main")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Also download Hub packs/ and compare (needs network; never required in CI)",
    )
    parser.add_argument(
        "--write-hashes",
        action="store_true",
        help="Refresh sha256_* lines in catalog/VERSION from local CSVs and exit",
    )
    args = parser.parse_args(argv)

    if not VERSION_PATH.is_file():
        print(f"ERROR: {VERSION_PATH} missing", file=sys.stderr)
        return 2

    meta = _parse_version(VERSION_PATH.read_text(encoding="utf-8"))
    packs = _packs(meta)

    if args.write_hashes:
        _write_hashes(meta, packs)
        return 0

    errors = check_offline(meta, packs)
    if args.live:
        errors.extend(check_live(meta, packs))

    if errors:
        print("SYNC CHECK FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("sync check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
