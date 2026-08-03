#!/usr/bin/env python3
"""Expand an eight-artwork manifest into the exact macOS cursor IDs Mousecape can replace."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


CANONICAL_IDENTIFIERS = {
    "normal": "com.apple.coregraphics.Arrow",
    "text": "com.apple.coregraphics.IBeam",
    "action": "com.apple.cursor.13",
    "forbidden": "com.apple.cursor.3",
    "busy": "com.apple.cursor.4",
    "open_hand": "com.apple.cursor.12",
    "resize_horizontal": "com.apple.cursor.19",
    "resize_vertical": "com.apple.cursor.23",
}

# (exact Mousecape/macOS identifier, canonical artwork to reuse)
# The application selects a concrete ID: horizontal resize alone cannot catch
# east/west resize, and `.4` alone cannot catch the system Wait cursor.
STANDARD_COVERAGE = {
    "normal": ("com.apple.coregraphics.Arrow", "normal"),
    "normal_small": ("com.apple.coregraphics.ArrowS", "normal"),
    "normal_context": ("com.apple.coregraphics.ArrowCtx", "normal"),
    "text": ("com.apple.coregraphics.IBeam", "text"),
    "text_small": ("com.apple.coregraphics.IBeamS", "text"),
    "text_xor": ("com.apple.coregraphics.IBeamXOR", "text"),
    "text_horizontal": ("com.apple.cursor.26", "text"),
    "action": ("com.apple.cursor.13", "action"),
    "link": ("com.apple.cursor.2", "action"),
    "context_menu": ("com.apple.cursor.24", "action"),
    "copy": ("com.apple.coregraphics.Copy", "action"),
    "copy_drag": ("com.apple.cursor.5", "action"),
    "alias": ("com.apple.coregraphics.Alias", "action"),
    "forbidden": ("com.apple.cursor.3", "forbidden"),
    "poof": ("com.apple.cursor.25", "forbidden"),
    "busy": ("com.apple.cursor.4", "busy"),
    "wait": ("com.apple.coregraphics.Wait", "busy"),
    "open_hand": ("com.apple.cursor.12", "open_hand"),
    "closed_hand": ("com.apple.cursor.11", "open_hand"),
    "move": ("com.apple.coregraphics.Move", "open_hand"),
    "resize_horizontal": ("com.apple.cursor.19", "resize_horizontal"),
    "resize_east": ("com.apple.cursor.18", "resize_horizontal"),
    "resize_west": ("com.apple.cursor.17", "resize_horizontal"),
    "resize_vertical": ("com.apple.cursor.23", "resize_vertical"),
    "resize_north": ("com.apple.cursor.21", "resize_vertical"),
    "resize_south": ("com.apple.cursor.22", "resize_vertical"),
    # The Window family is what macOS requests at native window borders.
    "window_east": ("com.apple.cursor.27", "resize_horizontal"),
    "window_e_w": ("com.apple.cursor.28", "resize_horizontal"),
    "window_ne": ("com.apple.cursor.29", "resize_horizontal"),
    "window_ne_sw": ("com.apple.cursor.30", "resize_horizontal"),
    "window_north": ("com.apple.cursor.31", "resize_vertical"),
    "window_n_s": ("com.apple.cursor.32", "resize_vertical"),
    "window_nw": ("com.apple.cursor.33", "resize_vertical"),
    "window_nw_se": ("com.apple.cursor.34", "resize_vertical"),
    "window_se": ("com.apple.cursor.35", "resize_vertical"),
    "window_south": ("com.apple.cursor.36", "resize_vertical"),
    "window_sw": ("com.apple.cursor.37", "resize_horizontal"),
    "window_west": ("com.apple.cursor.38", "resize_horizontal"),
    "zoom_in": ("com.apple.cursor.42", "normal"),
    "zoom_out": ("com.apple.cursor.43", "normal"),
    "help": ("com.apple.cursor.40", "normal"),
    "crosshair": ("com.apple.cursor.7", "normal"),
    "crosshair_secondary": ("com.apple.cursor.8", "normal"),
    "cell": ("com.apple.cursor.41", "normal"),
    "cell_xor": ("com.apple.cursor.20", "normal"),
    "camera": ("com.apple.cursor.10", "normal"),
    "camera_secondary": ("com.apple.cursor.9", "normal"),
    "count_up": ("com.apple.cursor.14", "resize_vertical"),
    "count_down": ("com.apple.cursor.15", "resize_vertical"),
    "count_up_down": ("com.apple.cursor.16", "resize_vertical"),
    "empty": ("com.apple.coregraphics.Empty", "normal"),
}


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read manifest {path}: {error}") from error
    if not isinstance(data, dict) or not isinstance(data.get("cursors"), dict):
        raise ValueError("manifest must contain a cursors object")
    return data


def expand_manifest(source_path: Path, output_path: Path, force: bool = False) -> Path:
    """Expand canonical art records without altering their files or hotspots."""
    if output_path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite manifest: {output_path}")
    manifest = load_manifest(source_path)
    source_cursors = manifest["cursors"]
    missing = set(CANONICAL_IDENTIFIERS) - set(source_cursors)
    if missing:
        raise ValueError(f"source manifest must include canonical artwork: {', '.join(sorted(missing))}")
    for state, identifier in CANONICAL_IDENTIFIERS.items():
        if source_cursors[state].get("identifier") != identifier:
            raise ValueError(f"{state} must use identifier {identifier}")

    manifest["cursors"] = {}
    for state, (identifier, source_state) in STANDARD_COVERAGE.items():
        record = copy.deepcopy(source_cursors[source_state])
        record["identifier"] = identifier
        manifest["cursors"][state] = record
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="Eight-artwork source manifest")
    parser.add_argument("--output", type=Path, required=True, help="Expanded manifest path")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        output = expand_manifest(args.manifest, args.output, args.force)
    except (ValueError, FileExistsError) as error:
        parser.error(str(error))
    print(f"expanded manifest: {output} ({len(STANDARD_COVERAGE)} exact cursor IDs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
