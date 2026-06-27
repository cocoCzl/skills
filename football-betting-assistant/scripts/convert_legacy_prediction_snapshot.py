#!/usr/bin/env python3
"""Convert legacy football prediction JSON into a standard prediction_snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from prediction_snapshot_tools import normalize_prediction_snapshot


def write_unique(path: Path, document: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    target = path
    for index in range(2, 1000):
        if not target.exists():
            break
        target = path.with_name(f"{path.stem}-{index}{path.suffix}")
    target.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a legacy football prediction JSON file.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--out", type=Path, help="Output path. Defaults to stdout.")
    args = parser.parse_args()

    document = json.loads(args.path.read_text(encoding="utf-8"))
    normalized = normalize_prediction_snapshot(document, str(args.path))
    if not normalized:
        parser.error("input is neither a prediction_snapshot nor a supported legacy prediction")
        return 2
    if args.out:
        path = write_unique(args.out, normalized)
        print(str(path))
    else:
        print(json.dumps(normalized, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
