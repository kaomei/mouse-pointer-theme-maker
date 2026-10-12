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


MIN_PREVIEW_WIDTH = 2440
MIN_PREVIEW_HEIGHT = 1388


def verify_preview_png(path: Path) -> None:
    """Fail closed unless the user-facing preview is a real, readable PNG."""
    if not path.is_file():
        raise ValueError(f"preview PNG was not written: {path.resolve()}")
    if path.stat().st_size <= 0:
        raise ValueError(f"preview PNG is empty: {path.resolve()}")
    if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"preview is not a PNG: {path.resolve()}")
    try:
        from PIL import Image

        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
    except Exception as error:  # Pillow raises several format-specific errors.
        raise ValueError(f"preview PNG cannot be decoded: {path.resolve()}: {error}") from error
    if width < MIN_PREVIEW_WIDTH or height < MIN_PREVIEW_HEIGHT:
        raise ValueError(
            f"preview PNG is too small ({width}x{height}); "
            f"need at least {MIN_PREVIEW_WIDTH}x{MIN_PREVIEW_HEIGHT}: {path.resolve()}"
        )


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
    verify_preview_png(args.output)
    print(f"preview_png: {args.output.resolve()}")
    print(f"preview_svg_internal: {svg_output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
