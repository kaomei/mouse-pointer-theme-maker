#!/usr/bin/env python3
"""Build a static HiDPI Mousecape cursor theme from a JSON manifest."""

from __future__ import annotations

import argparse
import base64
from io import BytesIO
import html
import json
import plistlib
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from prepare_cursor import CURSOR_SIZE, read_png_metadata, validate_cursor_png

REQUIRED_IDENTIFIERS = {
    "normal": "com.apple.coregraphics.Arrow",
    "text": "com.apple.coregraphics.IBeam",
    "action": "com.apple.cursor.13",
    "forbidden": "com.apple.cursor.3",
}
SUPPORTED_STATE_IDENTIFIERS = {
    **REQUIRED_IDENTIFIERS,
    "link": "com.apple.cursor.2",
    "busy": "com.apple.cursor.4",
    "wait": "com.apple.coregraphics.Wait",
    "copy": "com.apple.coregraphics.Copy",
    "alias": "com.apple.coregraphics.Alias",
    "move": "com.apple.coregraphics.Move",
    "open_hand": "com.apple.cursor.12",
    "closed_hand": "com.apple.cursor.11",
    "crosshair": "com.apple.cursor.7",
    "help": "com.apple.cursor.40",
    "context_menu": "com.apple.cursor.24",
    "camera": "com.apple.cursor.10",
    "zoom_in": "com.apple.cursor.42",
    "zoom_out": "com.apple.cursor.43",
    "resize_horizontal": "com.apple.cursor.19",
    "resize_vertical": "com.apple.cursor.23",
    "resize_ne_sw": "com.apple.cursor.30",
    "resize_nw_se": "com.apple.cursor.34",
    # Exact system variants. Apps request these identifiers independently, so a
    # generic horizontal or vertical resize image does not replace them.
    "normal_small": "com.apple.coregraphics.ArrowS",
    "normal_context": "com.apple.coregraphics.ArrowCtx",
    "text_small": "com.apple.coregraphics.IBeamS",
    "text_xor": "com.apple.coregraphics.IBeamXOR",
    "text_horizontal": "com.apple.cursor.26",
    "copy_drag": "com.apple.cursor.5",
    "resize_east": "com.apple.cursor.18",
    "resize_west": "com.apple.cursor.17",
    "resize_north": "com.apple.cursor.21",
    "resize_south": "com.apple.cursor.22",
    "count_up": "com.apple.cursor.14",
    "count_down": "com.apple.cursor.15",
    "count_up_down": "com.apple.cursor.16",
    "cell": "com.apple.cursor.41",
    "cell_xor": "com.apple.cursor.20",
    "camera_secondary": "com.apple.cursor.9",
    "crosshair_secondary": "com.apple.cursor.8",
    "poof": "com.apple.cursor.25",
    "empty": "com.apple.coregraphics.Empty",
    # Window-border cursors are distinct from the generic Resize variants.
    "window_east": "com.apple.cursor.27",
    "window_e_w": "com.apple.cursor.28",
    "window_ne": "com.apple.cursor.29",
    "window_ne_sw": "com.apple.cursor.30",
    "window_north": "com.apple.cursor.31",
    "window_n_s": "com.apple.cursor.32",
    "window_nw": "com.apple.cursor.33",
    "window_nw_se": "com.apple.cursor.34",
    "window_se": "com.apple.cursor.35",
    "window_south": "com.apple.cursor.36",
    "window_sw": "com.apple.cursor.37",
    "window_west": "com.apple.cursor.38",
}
REQUIRED_STATES = tuple(REQUIRED_IDENTIFIERS)
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]*$")
HIDPI_SCALES = (1, 2, 5, 10)
PREVIEW_STATE_ORDER = (
    "normal",
    "text",
    "action",
    "forbidden",
    "busy",
    "open_hand",
    "resize_horizontal",
    "resize_vertical",
)
PREVIEW_LABELS = {
    "normal": "正常选择",
    "text": "文字输入",
    "action": "链接 / 点击",
    "forbidden": "不可用",
    "busy": "忙碌中",
    "open_hand": "移动画布",
    "resize_horizontal": "左右调整",
    "resize_vertical": "上下调整",
}
PREVIEW_PALETTES = {
    "retro-pixel": {"background": "#EAF4FF", "ink": "#254A7A", "accent": "#4C84C4", "card": "#FFFFFF", "wash": "#CFE5FB"},
    "chibi-anime": {"background": "#FFF4F0", "ink": "#6D3B54", "accent": "#D47A98", "card": "#FFFDFD", "wash": "#F7D5DD"},
    "abstract-expression": {"background": "#FFF1E7", "ink": "#70261D", "accent": "#B95042", "card": "#FFFDFC", "wash": "#F4C7B4"},
}


def load_manifest(path: Path) -> dict[str, Any]:
    """Read the theme manifest and reject malformed JSON."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read manifest {path}: {error}") from error
    if not isinstance(manifest, dict):
        raise ValueError("manifest root must be an object")
    return manifest


def _read_hidpi_representations(cursor: dict[str, Any], state: str, manifest_dir: Path) -> list[bytes]:
    paths = cursor.get("representations")
    if paths is None:
        return [(manifest_dir / cursor["path"]).read_bytes()]
    if not isinstance(paths, list) or len(paths) != len(HIDPI_SCALES) or not all(isinstance(path, str) for path in paths):
        raise ValueError(f"{state} representations must list 1x, 2x, 5x, and 10x PNG paths")
    if paths[0] != cursor["path"]:
        raise ValueError(f"{state} path must match its 1x representation")

    images: list[bytes] = []
    for scale, path in zip(HIDPI_SCALES, paths):
        image_path = manifest_dir / path
        metadata = read_png_metadata(image_path)
        expected_size = CURSOR_SIZE * scale
        if not metadata.has_alpha:
            raise ValueError(f"{state} {scale}x representation must use a PNG with an alpha channel")
        if (metadata.width, metadata.height) != (expected_size, expected_size):
            raise ValueError(
                f"{state} {scale}x representation must be {expected_size} by {expected_size} pixels; "
                f"received {metadata.width} by {metadata.height}"
            )
        images.append(image_path.read_bytes())
    return images


def _validate_manifest(manifest: dict[str, Any], manifest_dir: Path) -> list[tuple[str, dict[str, Any], list[bytes]]]:
    theme = manifest.get("theme")
    cursors = manifest.get("cursors")
    if not isinstance(theme, dict) or not isinstance(cursors, dict):
        raise ValueError("manifest must contain theme and cursors objects")
    for field in ("name", "identifier", "author", "version"):
        if field not in theme or not theme[field]:
            raise ValueError(f"theme.{field} is required")
    if not isinstance(theme["name"], str) or not isinstance(theme["author"], str):
        raise ValueError("theme name and author must be strings")
    if not isinstance(theme["version"], int) or theme["version"] < 1:
        raise ValueError("theme.version must be a positive integer")
    if not isinstance(theme["identifier"], str) or not IDENTIFIER_RE.fullmatch(theme["identifier"]):
        raise ValueError("theme.identifier must use letters, numbers, periods, and hyphens")
    missing = set(REQUIRED_STATES) - set(cursors)
    unsupported = set(cursors) - set(SUPPORTED_STATE_IDENTIFIERS)
    if missing:
        raise ValueError(f"cursors must include: {', '.join(REQUIRED_STATES)}")
    if unsupported:
        raise ValueError(f"unsupported cursor states: {', '.join(sorted(unsupported))}")

    seen_identifiers: set[str] = set()
    records: list[tuple[str, dict[str, Any], list[bytes]]] = []
    for state in SUPPORTED_STATE_IDENTIFIERS:
        if state not in cursors:
            continue
        cursor = cursors[state]
        if not isinstance(cursor, dict):
            raise ValueError(f"{state} cursor must be an object")
        if cursor.get("identifier") != SUPPORTED_STATE_IDENTIFIERS[state]:
            raise ValueError(f"{state} must use identifier {SUPPORTED_STATE_IDENTIFIERS[state]}")
        identifier = cursor["identifier"]
        if identifier in seen_identifiers:
            raise ValueError(f"duplicate cursor identifier: {identifier}")
        seen_identifiers.add(identifier)
        if not isinstance(cursor.get("path"), str):
            raise ValueError(f"{state} path is required")
        hotspot = cursor.get("hotspot")
        if not isinstance(hotspot, list) or len(hotspot) != 2 or not all(isinstance(value, int) for value in hotspot):
            raise ValueError(f"{state} hotspot must be a two-integer array")
        if not all(0 <= value < CURSOR_SIZE for value in hotspot):
            raise ValueError(f"{state} hotspot must be inside the {CURSOR_SIZE} by {CURSOR_SIZE} canvas")
        image_path = manifest_dir / cursor["path"]
        validate_cursor_png(image_path, state)
        records.append((state, cursor, _read_hidpi_representations(cursor, state, manifest_dir)))
    return records


def _cape_payload(manifest: dict[str, Any], records: list[tuple[str, dict[str, Any], list[bytes]]]) -> dict[str, Any]:
    theme = manifest["theme"]
    cursors: dict[str, Any] = {}
    hidpi_records = [len(images) == len(HIDPI_SCALES) for _state, _cursor, images in records]
    if any(hidpi_records) and not all(hidpi_records):
        raise ValueError("all cursors must include HiDPI representations when any cursor includes them")
    for _state, cursor, image_data in records:
        cursors[cursor["identifier"]] = {
            "FrameCount": 1,
            "FrameDuration": 1.0,
            "HotSpotX": cursor["hotspot"][0],
            "HotSpotY": cursor["hotspot"][1],
            "PointsWide": CURSOR_SIZE,
            "PointsHigh": CURSOR_SIZE,
            "Representations": image_data,
        }
    return {
        "Author": theme["author"],
        "CapeName": theme["name"],
        "CapeVersion": theme["version"],
        "Cloud": False,
        "HiDPI": bool(hidpi_records and all(hidpi_records)),
        "Identifier": theme["identifier"],
        "MinimumVersion": 2,
        "Version": 2,
        "Cursors": cursors,
    }


def _validate_preview_safe_borders(records: list[tuple[str, dict[str, Any], list[bytes]]]) -> None:
    """Reject cropped artwork before it can become a user preview or package.

    A visible mark on a canvas edge is almost always a cut-off hat, arrow, or
    residue from a neighbouring image cell. The smallest representation gets a
    one-pixel safety border; 10x resources get a six-pixel border.
    """
    for state, _cursor, image_data in records:
        image = Image.open(BytesIO(image_data[-1])).convert("RGBA")
        bbox = image.getchannel("A").getbbox()
        if bbox is None:
            continue
        left, top, right, bottom = bbox
        margin = max(1, image.width // 48)
        if min(left, top, image.width - right, image.height - bottom) < margin:
            raise ValueError(
                f"{state} artwork violates the safe transparent border; "
                "recrop the original artwork with clear space on all four edges"
            )


def build_cape(manifest_path: Path, output_path: Path, force: bool = False) -> Path:
    """Write a binary Mousecape property list without overwriting by default."""
    if output_path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing package: {output_path}")
    manifest = load_manifest(manifest_path)
    records = _validate_manifest(manifest, manifest_path.parent)
    _validate_preview_safe_borders(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(plistlib.dumps(_cape_payload(manifest, records), fmt=plistlib.FMT_BINARY, sort_keys=True))
    return output_path


def write_preview(manifest: dict[str, Any], manifest_dir: Path, output_path: Path) -> Path:
    """Write a themed card preview for the eight user-facing cursor states."""
    all_records = _validate_manifest(manifest, manifest_dir)
    by_state = {state: (cursor, image_data) for state, cursor, image_data in all_records}
    records = [(state, *by_state[state]) for state in PREVIEW_STATE_ORDER if state in by_state]
    if not records:
        raise ValueError("manifest does not contain previewable cursor states")
    _validate_preview_safe_borders(records)

    preview_style = manifest["theme"].get("preview_style", "chibi-anime")
    palette = PREVIEW_PALETTES.get(str(preview_style), PREVIEW_PALETTES["chibi-anime"])
    tiles: list[str] = []
    columns = 4
    rows = max(1, (len(records) + columns - 1) // columns)
    margin, gap, card_width, card_height, header_height = 48, 28, 260, 238, 142
    image_size = 132
    for index, (state, cursor, image_data) in enumerate(records):
        column = index % columns
        row = index // columns
        x = margin + column * (card_width + gap)
        y = header_height + row * (card_height + gap)
        # A card is a product preview, not a magnified 1x cursor. Use the
        # same approved artwork's largest Retina representation so users can
        # judge linework and character detail without artificial pixelation.
        encoded = base64.b64encode(image_data[-1]).decode("ascii")
        image_x, image_y = x + (card_width - image_size) // 2, y + 42
        hotspot_x = image_x + cursor["hotspot"][0] * image_size / CURSOR_SIZE
        hotspot_y = image_y + cursor["hotspot"][1] * image_size / CURSOR_SIZE
        label = PREVIEW_LABELS.get(state, state.replace("_", " "))
        tiles.append(
            f'<g class="cursor-card">'
            f'<rect class="card-shadow" x="{x + 3}" y="{y + 5}" width="{card_width}" height="{card_height}" rx="24" fill="#4A24201A"/>'
            f'<rect class="card" x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="24" fill="{palette["card"]}" stroke="{palette["accent"]}" stroke-opacity="0.28"/>'
            f'<rect x="{x + 18}" y="{y + 16}" width="40" height="28" rx="14" fill="{palette["wash"]}"/>'
            f'<text x="{x + 38}" y="{y + 35}" text-anchor="middle" class="card-number">{index + 1:02}</text>'
            f'<text x="{x + 76}" y="{y + 35}" class="state-code">{html.escape(state)}</text>'
            f'<circle cx="{x + card_width - 35}" cy="{y + 31}" r="9" fill="{palette["accent"]}" opacity="0.22"/>'
            f'<image class="cursor-art" x="{image_x}" y="{image_y}" width="{image_size}" height="{image_size}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{encoded}"/>'
            f'<g class="hotspot" aria-label="hotspot"><circle cx="{hotspot_x:.2f}" cy="{hotspot_y:.2f}" r="7" fill="#E44A55" fill-opacity="0.12" stroke="#E44A55" stroke-width="1.7"/><path d="M {hotspot_x - 11:.2f} {hotspot_y:.2f} H {hotspot_x + 11:.2f} M {hotspot_x:.2f} {hotspot_y - 11:.2f} V {hotspot_y + 11:.2f}" stroke="#E44A55" stroke-width="1.7" stroke-linecap="round"/></g>'
            f'<text x="{x + card_width / 2}" y="{y + 201}" text-anchor="middle" class="state-label">{html.escape(label)}</text>'
            f'<text x="{x + card_width / 2}" y="{y + 220}" text-anchor="middle" class="state-note">红色十字为实际点击位置</text>'
            f'</g>'
        )
    title = html.escape(str(manifest["theme"]["name"]))
    width = margin * 2 + columns * card_width + (columns - 1) * gap
    height = header_height + rows * card_height + max(0, rows - 1) * gap + 48
    content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title} 鼠标皮肤状态预览">'
        '<style>.title{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;font-weight:800}.subtitle,.state-code,.state-note,.card-number,.state-label{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}.state-code{font-size:13px;letter-spacing:.2px;fill:#7A5260}.card-number{font-size:12px;font-weight:800;fill:#6D3B54}.state-label{font-size:20px;font-weight:760;fill:#321F2B}.state-note{font-size:11px;fill:#A27B85}.cursor-art{image-rendering:auto}</style>'
        f'<rect width="{width}" height="{height}" fill="{palette["background"]}"/>'
        f'<circle cx="{width - 84}" cy="58" r="76" fill="{palette["wash"]}" opacity="0.55"/>'
        f'<circle cx="84" cy="{height - 64}" r="112" fill="{palette["wash"]}" opacity="0.3"/>'
        f'<text x="{margin}" y="59" class="title" font-size="35" fill="{palette["ink"]}">{title} 鼠标皮肤</text>'
        f'<text x="{margin}" y="91" class="subtitle" font-size="16" fill="{palette["ink"]}" opacity="0.72">状态预览 · {len(records)} 个常用状态 · 红色十字为热点</text>'
        f'<rect x="{width - margin - 132}" y="42" width="132" height="42" rx="21" fill="{palette["accent"]}"/>'
        f'<text x="{width - margin - 66}" y="69" text-anchor="middle" class="subtitle" font-size="14" font-weight="700" fill="#FFFFFF">请确认后打包</text>'
        + "".join(tiles)
        + "</svg>"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def _preview_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Resolve a readable cross-platform CJK preview font."""
    from preview_design import font_path

    return ImageFont.truetype(str(font_path(bold)), size)


def write_preview_png(manifest: dict[str, Any], manifest_dir: Path, output_path: Path) -> Path:
    """Render the typography-led card layout from validated cursor resources."""
    from preview_design import render

    all_records = _validate_manifest(manifest, manifest_dir)
    by_state = {state: (cursor, image_data) for state, cursor, image_data in all_records}
    records = [(state, *by_state[state]) for state in PREVIEW_STATE_ORDER if state in by_state]
    if not records:
        raise ValueError("manifest does not contain previewable cursor states")
    _validate_preview_safe_borders(records)
    return render(manifest, manifest_dir, records, output_path, PREVIEW_LABELS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        package = build_cape(args.manifest, args.output, args.force)
        preview_path = args.preview or args.output.with_name("preview.svg")
        preview = write_preview(load_manifest(args.manifest), args.manifest.parent, preview_path)
    except (ValueError, FileExistsError) as error:
        parser.error(str(error))
    print(f"package: {package}")
    print(f"preview: {preview}")
    print(f"manifest: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
