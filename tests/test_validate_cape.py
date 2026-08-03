from __future__ import annotations

import json
import plistlib
import struct
import sys
import unittest
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_cape  # noqa: E402
import validate_cape  # noqa: E402


def chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def write_png(path: Path, size: int = 32) -> None:
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    pixels = (b"\x00" + b"\x00" * size * 4) * size
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


def build_valid_package(folder: Path) -> Path:
    cursor_specs = {
        "normal": ("com.apple.coregraphics.Arrow", [4, 4]),
        "text": ("com.apple.coregraphics.IBeam", [16, 16]),
        "action": ("com.apple.cursor.13", [8, 4]),
        "forbidden": ("com.apple.cursor.3", [16, 16]),
    }
    cursors = {}
    for state, (identifier, hotspot) in cursor_specs.items():
        write_png(folder / f"{state}.png")
        cursors[state] = {"path": f"{state}.png", "identifier": identifier, "hotspot": hotspot}
    manifest = folder / "manifest.json"
    manifest.write_text(json.dumps({"theme": {"name": "Test theme", "identifier": "com.example.test", "author": "Tester", "version": 1}, "cursors": cursors}), encoding="utf-8")
    return build_cape.build_cape(manifest, folder / "theme.cape")


def build_valid_hidpi_package(folder: Path) -> Path:
    package = build_valid_package(folder)
    manifest = folder / "manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for state, cursor in data["cursors"].items():
        representations = [cursor["path"]]
        for scale in (2, 5, 10):
            path = folder / f"{state}@{scale}x.png"
            write_png(path, 32 * scale)
            representations.append(path.name)
        cursor["representations"] = representations
    manifest.write_text(json.dumps(data), encoding="utf-8")
    return build_cape.build_cape(manifest, folder / "hidpi.cape")


class ValidateCapeTests(unittest.TestCase):
    def test_validate_cape_accepts_package_from_builder(self) -> None:
        with TemporaryDirectory() as directory:
            result = validate_cape.validate_cape(build_valid_package(Path(directory)))
        self.assertEqual(result["theme_name"], "Test theme")
        self.assertEqual(result["states"], ["normal", "text", "action", "forbidden"])

    def test_validate_cape_accepts_hidpi_representations(self) -> None:
        with TemporaryDirectory() as directory:
            result = validate_cape.validate_cape(build_valid_hidpi_package(Path(directory)))
        self.assertEqual(result["theme_name"], "Test theme")

    def test_validate_cape_rejects_missing_ibeam_record(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            package = build_valid_package(folder)
            cape = plistlib.loads(package.read_bytes())
            del cape["Cursors"]["com.apple.coregraphics.IBeam"]
            package.write_bytes(plistlib.dumps(cape, fmt=plistlib.FMT_BINARY))
            with self.assertRaisesRegex(ValueError, r"text"):
                validate_cape.validate_cape(package)

    def test_validate_cape_rejects_embedded_wrong_size(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            package = build_valid_package(folder)
            cape = plistlib.loads(package.read_bytes())
            cape["Cursors"]["com.apple.cursor.3"]["PointsWide"] = 16
            package.write_bytes(plistlib.dumps(cape, fmt=plistlib.FMT_BINARY))
            with self.assertRaisesRegex(ValueError, r"forbidden.*32"):
                validate_cape.validate_cape(package)


if __name__ == "__main__":
    unittest.main()
