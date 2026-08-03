from __future__ import annotations

import struct
import sys
import unittest
import zlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_windows_cursor  # noqa: E402


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def write_rgba_png(path: Path) -> Path:
    width = height = 32
    rows = []
    for y in range(height):
        pixels = bytearray()
        for x in range(width):
            pixels.extend((x, y, 255 - x, 255 if (x + y) % 2 else 0))
        rows.append(b"\x00" + bytes(pixels))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    content = b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header)
    content += png_chunk(b"IDAT", zlib.compress(b"".join(rows))) + png_chunk(b"IEND", b"")
    path.write_bytes(content)
    return path


class BuildWindowsCursorTests(unittest.TestCase):
    def test_write_cur_encodes_a_32_bit_cursor_with_requested_hotspot_and_bgra_pixels(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            source = write_rgba_png(folder / "source.png")
            output = build_windows_cursor.write_cur(source, folder / "Arrow.cur", (2, 3))
            parsed = build_windows_cursor.parse_cur(output.read_bytes())

        self.assertEqual(parsed["type"], 2)
        self.assertEqual(parsed["size"], (32, 32))
        self.assertEqual(parsed["hotspot"], (2, 3))
        self.assertEqual(parsed["bit_count"], 32)
        self.assertEqual(parsed["dib_height"], 64)
        self.assertEqual(parsed["first_pixel_bgra"], (255, 31, 0, 255))
        self.assertEqual(parsed["and_mask_length"], 128)

    def test_build_windows_theme_writes_all_roles_and_user_scoped_scripts(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            states = {
                "normal": ("com.apple.coregraphics.Arrow", [2, 2]),
                "text": ("com.apple.coregraphics.IBeam", [16, 16]),
                "action": ("com.apple.cursor.13", [20, 5]),
                "forbidden": ("com.apple.cursor.3", [16, 16]),
                "busy": ("com.apple.cursor.4", [16, 16]),
                "open_hand": ("com.apple.cursor.12", [16, 16]),
                "resize_horizontal": ("com.apple.cursor.19", [16, 16]),
                "resize_vertical": ("com.apple.cursor.23", [16, 16]),
            }
            cursors = {}
            for state, (identifier, hotspot) in states.items():
                write_rgba_png(folder / f"{state}.png")
                cursors[state] = {"path": f"{state}.png", "identifier": identifier, "hotspot": hotspot}
            manifest = folder / "manifest.json"
            manifest.write_text(json.dumps({"theme": {"name": "Test Theme"}, "cursors": cursors}), encoding="utf-8")
            package = build_windows_cursor.build_windows_theme(manifest, folder / "windows")
            generated_names = sorted(path.name for path in package.glob("*.cur"))
            install = (package / "install-current-user.ps1").read_text(encoding="utf-8")
            restore = (package / "restore-default.ps1").read_text(encoding="utf-8")

        self.assertEqual(generated_names, [
            "AppStarting.cur", "Arrow.cur", "Crosshair.cur", "Hand.cur", "Help.cur", "IBeam.cur", "NWPen.cur", "No.cur",
            "SizeAll.cur", "SizeNESW.cur", "SizeNS.cur", "SizeNWSE.cur", "SizeWE.cur", "UpArrow.cur", "Wait.cur",
        ])
        self.assertIn("HKCU:\\Control Panel\\Cursors", install)
        self.assertIn("$PSScriptRoot", install)
        self.assertIn("UpdatePerUserSystemParameters", install)
        self.assertIn("Remove-ItemProperty", restore)


if __name__ == "__main__":
    unittest.main()
