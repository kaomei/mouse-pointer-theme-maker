from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_hotspots  # noqa: E402


class ValidateHotspotsTests(unittest.TestCase):
    def test_preview_uses_a_valid_vertical_path_and_writes_output(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            cursor = folder / "normal.png"
            image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
            image.putpixel((2, 3), (255, 255, 255, 255))
            image.save(cursor)
            manifest = folder / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "cursors": {
                            "normal": {"path": cursor.name, "hotspot": [2, 3]},
                        }
                    }
                ),
                encoding="utf-8",
            )
            records = validate_hotspots.validate_hotspots(manifest)
            output = folder / "hotspot-preview.svg"
            validate_hotspots.write_preview(records, output)
            self.assertTrue(output.is_file())
            content = output.read_text(encoding="utf-8")

        self.assertRegex(content, r'M 39\.5 45\.25 H 47\.5 M 43\.5 41\.25 V 49\.25')
        self.assertNotRegex(content, r'V 43\.5 49\.25')


if __name__ == "__main__":
    unittest.main()
