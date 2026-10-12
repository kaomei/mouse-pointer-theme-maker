#!/usr/bin/env python3
"""Build static Windows `.cur` files from 32×32 RGBA PNG cursor artwork."""

from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path
from typing import Any

from prepare_cursor import CURSOR_SIZE, PNG_SIGNATURE, read_png_metadata


WINDOWS_CURSOR_ROLES = {
    "Arrow": "normal",
    "Help": "normal",
    "AppStarting": "busy",
    "Wait": "busy",
    "Crosshair": "normal",
    "IBeam": "text",
    "NWPen": "action",
    "No": "forbidden",
    "SizeNS": "resize_vertical",
    "SizeWE": "resize_horizontal",
    "SizeNWSE": "resize_vertical",
    "SizeNESW": "resize_horizontal",
    "SizeAll": "open_hand",
    "UpArrow": "normal",
    "Hand": "action",
}


def _paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    distances = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
    return (left, above, upper_left)[distances.index(min(distances))]


def read_rgba_png(path: Path, expected_size: int = CURSOR_SIZE) -> tuple[int, bytes]:
    """Decode an 8-bit RGBA PNG into top-down rows of RGBA pixels."""
    data = path.read_bytes()
    position = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = None
    compressed = bytearray()
    while position < len(data):
        if position + 12 > len(data):
            raise ValueError("truncated PNG chunk")
        length = struct.unpack(">I", data[position : position + 4])[0]
        kind = data[position + 4 : position + 8]
        end = position + 12 + length
        if end > len(data):
            raise ValueError("truncated PNG payload")
        payload = data[position + 8 : position + 8 + length]
        if kind == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if (width, height, bit_depth, color_type, compression, filtering, interlace) != (width, height, 8, 6, 0, 0, 0):
                raise ValueError("Windows cursor PNG must be a non-interlaced 8-bit RGBA PNG")
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
        position = end
    if width is None or not compressed:
        raise ValueError("PNG is missing IHDR or IDAT data")
    try:
        filtered = zlib.decompress(compressed)
    except zlib.error as error:
        raise ValueError(f"invalid PNG compressed data: {error}") from error

    if width != height or width != expected_size:
        raise ValueError(f"Windows cursor PNG must be {expected_size}×{expected_size} pixels")
    stride = expected_size * 4
    expected = (stride + 1) * expected_size
    if len(filtered) != expected:
        raise ValueError("PNG scanline data has an unexpected length")
    decoded = bytearray(expected_size * stride)
    previous = bytearray(stride)
    offset = 0
    for row_index in range(expected_size):
        filter_type = filtered[offset]
        offset += 1
        raw = filtered[offset : offset + stride]
        offset += stride
        row = bytearray(stride)
        for index, value in enumerate(raw):
            left = row[index - 4] if index >= 4 else 0
            above = previous[index]
            upper_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 0:
                decoded_value = value
            elif filter_type == 1:
                decoded_value = (value + left) & 0xFF
            elif filter_type == 2:
                decoded_value = (value + above) & 0xFF
            elif filter_type == 3:
                decoded_value = (value + ((left + above) // 2)) & 0xFF
            elif filter_type == 4:
                decoded_value = (value + _paeth(left, above, upper_left)) & 0xFF
            else:
                raise ValueError(f"unsupported PNG filter type: {filter_type}")
            row[index] = decoded_value
        decoded[row_index * stride : (row_index + 1) * stride] = row
        previous = row
    return expected_size, bytes(decoded)


def write_cur(source_png: Path | list[Path], output_cur: Path, hotspot: tuple[int, int]) -> Path:
    """Write a 32-bit Windows cursor with available 32px/64px images."""
    if len(hotspot) != 2 or not all(isinstance(value, int) and 0 <= value < CURSOR_SIZE for value in hotspot):
        raise ValueError("hotspot must be two integers inside the 32×32 cursor")
    sources = source_png if isinstance(source_png, list) else [source_png]
    if not 1 <= len(sources) <= 2:
        raise ValueError("Windows CUR supports one 32×32 image or a 32×32 plus 64×64 pair")
    images: list[tuple[int, bytes]] = []
    for source in sources:
        size, rgba = read_rgba_png(source, expected_size=CURSOR_SIZE if len(images) == 0 else 64)
        images.append((size, rgba))

    dibs: list[bytes] = []
    for size, rgba in images:
        xor = bytearray()
        for row_index in reversed(range(size)):
            row = rgba[row_index * size * 4 : (row_index + 1) * size * 4]
            for index in range(0, len(row), 4):
                red, green, blue, alpha = row[index : index + 4]
                xor.extend((blue, green, red, alpha))
        mask_row_bytes = ((size + 31) // 32) * 4
        and_mask = bytes(size * mask_row_bytes)
        dibs.append(struct.pack(
            "<IiiHHIIiiII",
            40,
            size,
            size * 2,
            1,
            32,
            0,
            len(xor),
            0,
            0,
            0,
            0,
        ) + bytes(xor) + and_mask)

    header_size = 6 + len(dibs) * 16
    entries = []
    offset = header_size
    for (size, _rgba), dib in zip(images, dibs):
        factor = size / CURSOR_SIZE
        entries.append(struct.pack(
            "<BBBBHHII",
            size if size < 256 else 0,
            size if size < 256 else 0,
            0,
            0,
            round(hotspot[0] * factor),
            round(hotspot[1] * factor),
            len(dib),
            offset,
        ))
        offset += len(dib)
    header = struct.pack("<HHH", 0, 2, len(dibs))
    output_cur.parent.mkdir(parents=True, exist_ok=True)
    output_cur.write_bytes(header + b"".join(entries) + b"".join(dibs))
    return output_cur


def parse_cur(data: bytes) -> dict[str, Any]:
    """Return structural fields needed to validate a Windows CUR."""
    if len(data) < 62:
        raise ValueError("CUR file is too small")
    reserved, cursor_type, count = struct.unpack("<HHH", data[:6])
    if reserved != 0 or cursor_type != 2 or count < 1:
        raise ValueError("not a Windows cursor")
    if len(data) < 6 + count * 16:
        raise ValueError("CUR directory is truncated")
    entries = []
    for index in range(count):
        start = 6 + index * 16
        width, height, color_count, entry_reserved, hotspot_x, hotspot_y, image_size, image_offset = struct.unpack("<BBBBHHII", data[start : start + 16])
        if color_count != 0 or entry_reserved != 0 or image_offset + image_size > len(data):
            raise ValueError("invalid CUR image entry")
        dib_size, dib_width, dib_height, planes, bit_count, compression, size_image, *_rest = struct.unpack("<IiiHHIIiiII", data[image_offset : image_offset + 40])
        actual_width = width or 256
        if (dib_size, dib_width, planes, bit_count, compression) != (40, actual_width, 1, 32, 0):
            raise ValueError("unsupported CUR bitmap")
        xor_length = actual_width * actual_width * 4
        and_mask_length = image_size - 40 - xor_length
        if and_mask_length < 0:
            raise ValueError("CUR bitmap is truncated")
        entries.append({
            "size": (actual_width, height or 256),
            "hotspot": (hotspot_x, hotspot_y),
            "size_image": size_image,
            "and_mask_length": and_mask_length,
            "first_pixel_bgra": tuple(data[image_offset + 40 : image_offset + 44]),
        })
    first = entries[0]
    return {
        "type": cursor_type,
        "count": count,
        "size": first["size"],
        "sizes": [entry["size"] for entry in entries],
        "hotspot": first["hotspot"],
        "bit_count": bit_count,
        "dib_height": dib_height,
        "size_image": first["size_image"],
        "first_pixel_bgra": first["first_pixel_bgra"],
        "and_mask_length": first["and_mask_length"],
    }


def _load_windows_manifest(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read manifest {path}: {error}") from error
    if not isinstance(manifest, dict) or not isinstance(manifest.get("theme"), dict) or not isinstance(manifest.get("cursors"), dict):
        raise ValueError("manifest must contain theme and cursors objects")
    missing = set(WINDOWS_CURSOR_ROLES.values()) - set(manifest["cursors"])
    if missing:
        raise ValueError(f"manifest is missing Windows source artwork: {', '.join(sorted(missing))}")
    return manifest, manifest["cursors"]


def _install_script() -> str:
    role_lines = "\n".join(f"    '{role}' = '{role}.cur'" for role in WINDOWS_CURSOR_ROLES)
    return f"""# Generated by mouse-pointer-theme-maker. Run only after extracting this folder.
$ErrorActionPreference = 'Stop'
$cursorKey = 'HKCU:\\Control Panel\\Cursors'
$files = @{{
{role_lines}
}}
New-Item -Path $cursorKey -Force | Out-Null
foreach ($entry in $files.GetEnumerator()) {{
    Set-ItemProperty -Path $cursorKey -Name $entry.Key -Value (Join-Path $PSScriptRoot $entry.Value)
}}
Set-ItemProperty -Path $cursorKey -Name 'Scheme Source' -Value 1
& rundll32.exe user32.dll,UpdatePerUserSystemParameters
Write-Host 'Cursor theme applied. If Windows does not refresh immediately, sign out and sign in again.'
"""


def _restore_script() -> str:
    names = ", ".join(f"'{role}'" for role in WINDOWS_CURSOR_ROLES)
    return f"""# Removes only the cursor values installed by this package.
$ErrorActionPreference = 'Stop'
$cursorKey = 'HKCU:\\Control Panel\\Cursors'
@({names}) | ForEach-Object {{
    Remove-ItemProperty -Path $cursorKey -Name $_ -ErrorAction SilentlyContinue
}}
Remove-ItemProperty -Path $cursorKey -Name 'Scheme Source' -ErrorAction SilentlyContinue
& rundll32.exe user32.dll,UpdatePerUserSystemParameters
Write-Host 'Windows default cursor values restored. If needed, select a scheme in Mouse Properties > Pointers.'
"""


def _windows_readme(theme_name: str, has_hidpi: bool = True) -> str:
    hidpi_note = (
        "Each `.cur` includes validated 32×32 and 64×64 resources so Windows can choose a sharper image at high display scaling."
        if has_hidpi
        else
        "The package uses the validated 32×32 resources. A valid 64×64 source was not available, so Windows high-DPI selection is limited."
    )
    return f"""# {theme_name} — Windows 10/11 cursor theme

## Install

1. Extract this entire folder somewhere you will keep it. Do not move or delete the `.cur` files after installing.
2. Right-click `install-current-user.ps1` and choose **Run with PowerShell**.
3. If Windows asks for confirmation, approve only after confirming this is the package you extracted.
4. If the cursor does not refresh immediately, sign out and sign back in.

The installer changes only the current user's cursor-role values under `HKCU\\Control Panel\\Cursors`; it does not need administrator permission and does not copy files into Windows system folders.

{hidpi_note}

## Restore

Run `restore-default.ps1` from this folder, then sign out/in if necessary. It removes only the role values this package installs.

## Expected behaviour

Arrow, text, links and resize states are common. Windows applications choose whether to request working, busy, unavailable or handwriting cursor roles, so those designs may not appear frequently.
"""


def build_windows_theme(manifest_path: Path, output_dir: Path, force: bool = False) -> Path:
    """Create a user-scoped Windows cursor package from the eight approved artworks."""
    if output_dir.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing Windows package: {output_dir}")
    manifest, cursors = _load_windows_manifest(manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    has_hidpi = True
    for role, state in WINDOWS_CURSOR_ROLES.items():
        cursor = cursors[state]
        if not isinstance(cursor, dict) or not isinstance(cursor.get("path"), str):
            raise ValueError(f"{state} must define a cursor PNG path")
        hotspot = cursor.get("hotspot")
        if not isinstance(hotspot, list) or len(hotspot) != 2 or not all(isinstance(value, int) for value in hotspot):
            raise ValueError(f"{state} must define a two-integer hotspot")
        source_paths = [manifest_path.parent / cursor["path"]]
        representations = cursor.get("representations")
        if isinstance(representations, list) and len(representations) >= 2:
            candidate = manifest_path.parent / representations[1]
            if candidate.is_file():
                try:
                    metadata = read_png_metadata(candidate)
                except ValueError:
                    metadata = None
                if metadata and metadata.width == 64 and metadata.height == 64 and metadata.has_alpha:
                    source_paths.append(candidate)
                else:
                    has_hidpi = False
            else:
                has_hidpi = False
        else:
            has_hidpi = False
        write_cur(source_paths, output_dir / f"{role}.cur", (hotspot[0], hotspot[1]))
    theme_name = str(manifest["theme"].get("name") or "Custom Cursor Theme")
    (output_dir / "install-current-user.ps1").write_text(_install_script(), encoding="utf-8")
    (output_dir / "restore-default.ps1").write_text(_restore_script(), encoding="utf-8")
    (output_dir / "README-Windows.md").write_text(_windows_readme(theme_name, has_hidpi), encoding="utf-8")
    return output_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        package = build_windows_theme(args.manifest, args.output, args.force)
    except (ValueError, FileExistsError) as error:
        parser.error(str(error))
    print(f"Windows package: {package} ({len(WINDOWS_CURSOR_ROLES)} cursor roles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
