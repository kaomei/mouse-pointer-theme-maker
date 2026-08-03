#!/usr/bin/env python3
"""Validate that theme hotspots land on visible pixels and render a review sheet."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from PIL import Image


def validate_hotspots(manifest_path: Path) -> list[tuple[str, Path, tuple[int, int]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = []
    for state, cursor in manifest["cursors"].items():
        path = manifest_path.parent / cursor["path"]
        x, y = cursor["hotspot"]
        alpha = Image.open(path).convert("RGBA").getchannel("A")
        if alpha.getpixel((x, y)) == 0:
            raise ValueError(f"{state}: hotspot ({x}, {y}) lands on transparency")
        records.append((state, path, (x, y)))
    return records


def write_preview(records: list[tuple[str, Path, tuple[int, int]]], output: Path) -> None:
    columns = 4
    rows = (len(records) + columns - 1) // columns
    width, height = columns * 184 + 24, rows * 112 + 48
    tiles = []
    for index, (state, path, (hot_x, hot_y)) in enumerate(records):
        x, y = 24 + index % columns * 184, 24 + index // columns * 112
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        cross_x, cross_y = x + 16 + hot_x * 56 / 32, y + 16 + hot_y * 56 / 32
        tiles.append(f'<rect x="{x}" y="{y}" width="160" height="88" rx="12" fill="#f4f4f5"/><image x="{x+16}" y="{y+16}" width="56" height="56" href="data:image/png;base64,{encoded}"/><path d="M {cross_x-4} {cross_y} H {cross_x+4} M {cross_x} {cross_y-4} V {cross_x} {cross_y+4}" stroke="#ef4444" stroke-width="2"/><text x="{x+88}" y="{y+49}" font-family="sans-serif" font-size="14">{state}</text>')
    output.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/>'+"".join(tiles)+"</svg>", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--preview", type=Path, required=True)
    args = parser.parse_args()
    records = validate_hotspots(args.manifest)
    write_preview(records, args.preview)
    print(f"valid hotspots: {len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
