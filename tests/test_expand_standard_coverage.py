from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import expand_standard_coverage  # noqa: E402


class ExpandStandardCoverageTests(unittest.TestCase):
    def test_expand_adds_exact_directional_and_wait_identifiers(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / "manifest.json"
            source.write_text(
                json.dumps(
                    {
                        "theme": {"name": "Test", "identifier": "com.example.test", "author": "Tester", "version": 1},
                        "cursors": {
                            state: {"path": f"{state}.png", "representations": [f"{state}.png"] * 4, "identifier": identifier, "hotspot": [16, 16]}
                            for state, identifier in expand_standard_coverage.CANONICAL_IDENTIFIERS.items()
                        },
                    }
                ),
                encoding="utf-8",
            )
            output = folder / "expanded.json"
            expand_standard_coverage.expand_manifest(source, output)
            expanded = json.loads(output.read_text(encoding="utf-8"))

        cursors = expanded["cursors"]
        self.assertEqual(cursors["resize_east"]["identifier"], "com.apple.cursor.18")
        self.assertEqual(cursors["resize_west"]["path"], "resize_horizontal.png")
        self.assertEqual(cursors["resize_north"]["path"], "resize_vertical.png")
        self.assertEqual(cursors["wait"]["identifier"], "com.apple.coregraphics.Wait")
        self.assertEqual(cursors["normal_context"]["identifier"], "com.apple.coregraphics.ArrowCtx")
        self.assertEqual(len(cursors), len(expand_standard_coverage.STANDARD_COVERAGE))

    def test_expand_includes_window_edge_resize_ids_used_by_macos_windows(self) -> None:
        """Window borders request Window E-W / N-S, not only generic Resize IDs."""
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / "manifest.json"
            source.write_text(
                json.dumps(
                    {
                        "theme": {"name": "Test", "identifier": "com.example.test", "author": "Tester", "version": 1},
                        "cursors": {
                            state: {"path": f"{state}.png", "representations": [f"{state}.png"] * 4, "identifier": identifier, "hotspot": [16, 16]}
                            for state, identifier in expand_standard_coverage.CANONICAL_IDENTIFIERS.items()
                        },
                    }
                ),
                encoding="utf-8",
            )
            output = folder / "expanded.json"
            expand_standard_coverage.expand_manifest(source, output)
            cursors = json.loads(output.read_text(encoding="utf-8"))["cursors"]

        self.assertEqual(cursors["window_e_w"]["identifier"], "com.apple.cursor.28")
        self.assertEqual(cursors["window_e_w"]["path"], "resize_horizontal.png")
        self.assertEqual(cursors["window_n_s"]["identifier"], "com.apple.cursor.32")
        self.assertEqual(cursors["window_n_s"]["path"], "resize_vertical.png")


if __name__ == "__main__":
    unittest.main()
