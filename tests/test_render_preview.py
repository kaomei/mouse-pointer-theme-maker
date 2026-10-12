from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import render_preview  # noqa: E402


class RenderPreviewTests(unittest.TestCase):
    def test_verify_preview_png_accepts_readable_large_png(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "preview.png"
            Image.new("RGBA", (2440, 1388), "white").save(path)
            render_preview.verify_preview_png(path)

    def test_verify_preview_png_rejects_missing_or_empty_file(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "preview.png"
            with self.assertRaisesRegex(ValueError, "not written"):
                render_preview.verify_preview_png(path)
            path.touch()
            with self.assertRaisesRegex(ValueError, "empty"):
                render_preview.verify_preview_png(path)

    def test_verify_preview_png_rejects_small_png(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "preview.png"
            Image.new("RGBA", (2440, 856), "white").save(path)
            with self.assertRaisesRegex(ValueError, "too small"):
                render_preview.verify_preview_png(path)

    def test_verify_preview_png_rejects_invalid_png_bytes(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "preview.png"
            path.write_bytes(b"\x89PNG\r\n\x1a\nnot-a-real-png")
            with self.assertRaisesRegex(ValueError, "cannot be decoded"):
                render_preview.verify_preview_png(path)


if __name__ == "__main__":
    unittest.main()
