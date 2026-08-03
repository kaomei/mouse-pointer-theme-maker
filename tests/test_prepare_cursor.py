from __future__ import annotations

import struct
import sys
import unittest
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_cursor  # noqa: E402


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png(path: Path, width: int, height: int, color_type: int = 6) -> Path:
    channels = 4 if color_type == 6 else 3
    rows = b"".join(b"\x00" + (b"\x00" * width * channels) for _ in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    payload = b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header)
    payload += png_chunk(b"IDAT", zlib.compress(rows)) + png_chunk(b"IEND", b"")
    path.write_bytes(payload)
    return path


class PrepareCursorTests(unittest.TestCase):
    def test_validate_cursor_png_accepts_transparent_32_pixel_png(self) -> None:
        with TemporaryDirectory() as directory:
            path = write_png(Path(directory) / "normal.png", 32, 32)
            metadata = prepare_cursor.validate_cursor_png(path, "normal")
        self.assertEqual((metadata.width, metadata.height, metadata.has_alpha), (32, 32, True))

    def test_validate_cursor_png_accepts_a_64_pixel_2x_representation(self) -> None:
        with TemporaryDirectory() as directory:
            path = write_png(Path(directory) / "normal@2x.png", 64, 64)
            metadata = prepare_cursor.validate_cursor_png(path, "normal", scale=2)
        self.assertEqual((metadata.width, metadata.height, metadata.has_alpha), (64, 64, True))

    def test_validate_cursor_png_rejects_wrong_size_with_state_name(self) -> None:
        with TemporaryDirectory() as directory:
            path = write_png(Path(directory) / "text.png", 16, 16)
            with self.assertRaisesRegex(ValueError, r"text.*32 by 32"):
                prepare_cursor.validate_cursor_png(path, "text")

    def test_validate_cursor_png_rejects_opaque_png(self) -> None:
        with TemporaryDirectory() as directory:
            path = write_png(Path(directory) / "action.png", 32, 32, color_type=2)
            with self.assertRaisesRegex(ValueError, r"action.*alpha"):
                prepare_cursor.validate_cursor_png(path, "action")

    def test_prepare_cursor_copies_valid_image_without_resizing(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            source = write_png(folder / "source.png", 32, 32)
            destination = folder / "output.png"
            metadata = prepare_cursor.prepare_cursor(source, destination, "normal")
            self.assertEqual(metadata.width, 32)
            self.assertEqual(destination.read_bytes(), source.read_bytes())


if __name__ == "__main__":
    unittest.main()
