#!/usr/bin/env python3
"""Validate a static four-state Mousecape `.cape` package."""

from __future__ import annotations

import argparse
import plistlib
from pathlib import Path
from typing import Any

from build_cape import HIDPI_SCALES, REQUIRED_IDENTIFIERS, REQUIRED_STATES
from prepare_cursor import CURSOR_SIZE, read_png_metadata_bytes


def _validate_record(state: str, record: Any, hidpi: bool) -> None:
    if not isinstance(record, dict):
        raise ValueError(f"{state} record is not a dictionary")
    if record.get("FrameCount") != 1:
        raise ValueError(f"{state} must contain one static frame")
    if (record.get("PointsWide"), record.get("PointsHigh")) != (CURSOR_SIZE, CURSOR_SIZE):
        raise ValueError(f"{state} must be {CURSOR_SIZE} by {CURSOR_SIZE} points")
    hotspot = (record.get("HotSpotX"), record.get("HotSpotY"))
    if not all(isinstance(value, int) and 0 <= value < CURSOR_SIZE for value in hotspot):
        raise ValueError(f"{state} hotspot must be inside the {CURSOR_SIZE} by {CURSOR_SIZE} canvas")
    representations = record.get("Representations")
    scales = HIDPI_SCALES if hidpi else (1,)
    if not isinstance(representations, list) or len(representations) != len(scales) or not all(isinstance(image, bytes) for image in representations):
        label = "1x, 2x, 5x, and 10x" if hidpi else "one"
        raise ValueError(f"{state} must contain {label} PNG representation{'s' if hidpi else ''}")
    for scale, image in zip(scales, representations):
        metadata = read_png_metadata_bytes(image)
        expected_size = CURSOR_SIZE * scale
        if not metadata.has_alpha:
            raise ValueError(f"{state} {scale}x representation must have an alpha channel")
        if (metadata.width, metadata.height) != (expected_size, expected_size):
            raise ValueError(f"{state} {scale}x representation must be {expected_size} by {expected_size} pixels")


def validate_cape(path: Path) -> dict[str, Any]:
    """Return a compact summary after proving all four expected records are valid."""
    try:
        payload = plistlib.loads(path.read_bytes())
    except (OSError, plistlib.InvalidFileException) as error:
        raise ValueError(f"cannot read .cape file {path}: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError("cape root must be a dictionary")
    if payload.get("Version") != 2 or payload.get("MinimumVersion") != 2:
        raise ValueError("cape must use Mousecape format version 2")
    if not isinstance(payload.get("CapeName"), str) or not payload["CapeName"]:
        raise ValueError("cape is missing CapeName")
    hidpi = payload.get("HiDPI")
    if not isinstance(hidpi, bool):
        raise ValueError("cape HiDPI must be true or false")
    cursors = payload.get("Cursors")
    if not isinstance(cursors, dict):
        raise ValueError("cape is missing its Cursors dictionary")
    for state in REQUIRED_STATES:
        identifier = REQUIRED_IDENTIFIERS[state]
        if identifier not in cursors:
            raise ValueError(f"cape is missing required {state} cursor: {identifier}")
        _validate_record(state, cursors[identifier], hidpi)
    return {"theme_name": payload["CapeName"], "states": list(REQUIRED_STATES)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cape", type=Path)
    args = parser.parse_args()
    try:
        summary = validate_cape(args.cape)
    except ValueError as error:
        parser.error(str(error))
    print(f"valid: {summary['theme_name']} ({', '.join(summary['states'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
