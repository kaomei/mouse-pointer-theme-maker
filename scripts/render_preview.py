#!/usr/bin/env python3
"""Render the user-facing cursor card preview before package creation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_cape import load_manifest, write_preview, write_preview_png  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="user-facing PNG preview")
    parser.add_argument("--svg-output", type=Path, help="optional internal editable SVG source")
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    svg_output = args.svg_output or args.output.with_suffix(".svg")
    write_preview(manifest, args.manifest.parent, svg_output)
    write_preview_png(manifest, args.manifest.parent, args.output)
    print(f"preview_png: {args.output}")
    print(f"preview_svg_internal: {svg_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
