#!/usr/bin/env python3
"""Validate and normalize one static Mousecape cursor image."""

from __future__ import annotations

import argparse
import shutil
import struct
from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CURSOR_SIZE = 32


@dataclass(frozen=True)
class PngMetadata:
    width: int
    height: int
    has_alpha: bool


def read_png_metadata_bytes(data: bytes) -> PngMetadata:
    """Read the PNG dimensions and alpha-channel availability without decoding pixels."""
    if len(data) < 29 or data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
        raise ValueError("input is not a PNG with an IHDR header")
    width, height, _bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
    if width <= 0 or height <= 0:
        raise ValueError("PNG dimensions must be positive")
    return PngMetadata(width=width, height=height, has_alpha=color_type in {4, 6})


def read_png_metadata(path: Path) -> PngMetadata:
    """Read metadata from a PNG file."""
    try:
        return read_png_metadata_bytes(path.read_bytes())
    except OSError as error:
        raise ValueError(f"cannot read {path}: {error}") from error


def validate_cursor_png(path: Path, state: str, scale: int = 1) -> PngMetadata:
    """Require a transparent cursor PNG at one of the supported scale factors."""
    if scale not in {1, 2, 5, 10}:
        raise ValueError("scale must be one of: 1, 2, 5, 10")
    metadata = read_png_metadata(path)
    if not metadata.has_alpha:
        raise ValueError(f"{state} must use a PNG with an alpha channel")
    expected_size = CURSOR_SIZE * scale
    if (metadata.width, metadata.height) != (expected_size, expected_size):
        raise ValueError(
            f"{state} must be {expected_size} by {expected_size} pixels; "
            f"received {metadata.width} by {metadata.height}"
        )
    return metadata


def prepare_cursor(source: Path, destination: Path, state: str, resize: bool = False, scale: int = 1) -> PngMetadata:
    """Copy a validated cursor or resample it portably with Pillow."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if resize:
        try:
            from PIL import Image

            with Image.open(source) as image:
                if "A" not in image.getbands() and "transparency" not in image.info:
                    raise ValueError(f"{state} source must have transparency")
                image.convert("RGBA").resize(
                    (CURSOR_SIZE * scale, CURSOR_SIZE * scale), Image.Resampling.LANCZOS
                ).save(destination, format="PNG")
        except ImportError as error:
            raise ValueError("Pillow is required: install with python -m pip install Pillow") from error
        except OSError as error:
            raise ValueError(f"could not resize {state}: {error}") from error
    else:
        shutil.copy2(source, destination)
    return validate_cursor_png(destination, state, scale)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--resize", action="store_true")
    parser.add_argument("--scale", type=int, choices=(1, 2, 5, 10), default=1)
    args = parser.parse_args()
    try:
        metadata = prepare_cursor(args.source, args.output, args.state, args.resize, args.scale)
    except ValueError as error:
        parser.error(str(error))
    print(f"{args.output}: {metadata.width}x{metadata.height}, alpha={metadata.has_alpha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
