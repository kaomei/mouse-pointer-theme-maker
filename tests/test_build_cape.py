from __future__ import annotations

import base64
import json
import plistlib
import struct
import sys
import unittest
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_cape  # noqa: E402


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def write_png(path: Path, size: int = 32, pixel: bytes = b"\x00\x00\x00\x00") -> Path:
    row = b"\x00" + pixel * size
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    content = b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header)
    path.write_bytes(content + png_chunk(b"IDAT", zlib.compress(row * size)) + png_chunk(b"IEND", b""))
    return path


def write_padded_png(path: Path, size: int, pixel: tuple[int, int, int, int]) -> Path:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    inset = max(1, size // 8)
    image.paste(pixel, (inset, inset, size - inset, size - inset))
    image.save(path)
    return path


def write_complete_manifest(folder: Path) -> Path:
    states = {
        "normal": ("com.apple.coregraphics.Arrow", [4, 4]),
        "text": ("com.apple.coregraphics.IBeam", [16, 16]),
        "action": ("com.apple.cursor.13", [8, 4]),
        "forbidden": ("com.apple.cursor.3", [16, 16]),
    }
    cursors = {}
    for state, (identifier, hotspot) in states.items():
        write_png(folder / f"{state}.png")
        cursors[state] = {"path": f"{state}.png", "identifier": identifier, "hotspot": hotspot}
    manifest = {"theme": {"name": "Test theme", "identifier": "com.example.test-theme", "author": "Tester", "version": 1}, "cursors": cursors}
    path = folder / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


class BuildCapeTests(unittest.TestCase):
    def test_build_cape_writes_binary_plist_with_four_png_representations(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = write_complete_manifest(folder)
            output = build_cape.build_cape(manifest, folder / "theme.cape")
            cape = plistlib.loads(output.read_bytes())
        self.assertEqual(cape["CapeName"], "Test theme")
        self.assertEqual(set(cape["Cursors"]), set(build_cape.REQUIRED_IDENTIFIERS.values()))
        arrow = cape["Cursors"]["com.apple.coregraphics.Arrow"]
        self.assertEqual((arrow["PointsWide"], arrow["PointsHigh"], arrow["FrameCount"]), (32, 32, 1))
        self.assertTrue(arrow["Representations"][0].startswith(b"\x89PNG"))

    def test_build_cape_writes_retina_representations_for_hidpi_manifest(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = write_complete_manifest(folder)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            for state, cursor in data["cursors"].items():
                paths = [cursor["path"]]
                for scale in (2, 5, 10):
                    path = folder / f"{state}@{scale}x.png"
                    write_png(path, 32 * scale)
                    paths.append(path.name)
                cursor["representations"] = paths
            manifest.write_text(json.dumps(data), encoding="utf-8")
            cape = plistlib.loads(build_cape.build_cape(manifest, folder / "theme.cape").read_bytes())

        arrow = cape["Cursors"]["com.apple.coregraphics.Arrow"]
        dimensions = [struct.unpack(">II", image[16:24]) for image in arrow["Representations"]]
        self.assertTrue(cape["HiDPI"])
        self.assertEqual(dimensions, [(32, 32), (64, 64), (160, 160), (320, 320)])

    def test_build_cape_refuses_to_overwrite(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = write_complete_manifest(folder)
            output = folder / "theme.cape"
            build_cape.build_cape(manifest, output)
            with self.assertRaises(FileExistsError):
                build_cape.build_cape(manifest, output)

    def test_build_cape_rejects_hotspot_outside_canvas(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = write_complete_manifest(folder)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["cursors"]["action"]["hotspot"] = [32, 0]
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"action.*hotspot"):
                build_cape.build_cape(manifest, folder / "theme.cape")

    def test_write_preview_embeds_each_state(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest_path = write_complete_manifest(folder)
            manifest = build_cape.load_manifest(manifest_path)
            preview = build_cape.write_preview(manifest, folder, folder / "preview.svg")
            content = preview.read_text(encoding="utf-8")
        self.assertIn("normal", content)
        self.assertEqual(content.count("data:image/png;base64,"), 4)
        self.assertIn('class="cursor-card"', content)
        self.assertIn('class="hotspot"', content)
        self.assertIn("鼠标皮肤", content)
        self.assertIn("状态预览", content)

    def test_write_preview_png_is_a_raster_card_with_expected_dimensions(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest_path = write_complete_manifest(folder)
            output = build_cape.write_preview_png(
                build_cape.load_manifest(manifest_path), folder, folder / "preview.png"
            )
            png = output.read_bytes()

        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual(struct.unpack(">II", png[16:24]), (2440, 856))


    def test_write_preview_uses_the_largest_retina_artwork_instead_of_upscaling_1x(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest_path = write_complete_manifest(folder)
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            for state, cursor in data["cursors"].items():
                paths = [cursor["path"]]
                for scale in (2, 5, 10):
                    path = folder / f"{state}@{scale}x.png"
                    pixel = b"\x00\x00\x00\x00"
                    if state == "normal" and scale == 10:
                        write_padded_png(path, 32 * scale, (211, 74, 105, 255))
                    else:
                        write_png(path, 32 * scale, pixel)
                    paths.append(path.name)
                cursor["representations"] = paths
            manifest_path.write_text(json.dumps(data), encoding="utf-8")

            preview = build_cape.write_preview(build_cape.load_manifest(manifest_path), folder, folder / "preview.svg")
            content = preview.read_text(encoding="utf-8")
            largest_normal = base64.b64encode((folder / "normal@10x.png").read_bytes()).decode("ascii")

        self.assertIn(largest_normal, content)

    def test_preview_rejects_artwork_that_touches_the_crop_edge(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest_path = write_complete_manifest(folder)
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            for state, cursor in data["cursors"].items():
                paths = [cursor["path"]]
                for scale in (2, 5, 10):
                    path = folder / f"{state}@{scale}x.png"
                    pixel = b"\x00\x00\x00\x00"
                    if state == "normal" and scale == 10:
                        pixel = b"\x22\x22\x22\xFF"
                    write_png(path, 32 * scale, pixel)
                    paths.append(path.name)
                cursor["representations"] = paths
            manifest_path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, r"normal.*safe transparent border"):
                build_cape.write_preview(build_cape.load_manifest(manifest_path), folder, folder / "preview.svg")

    def test_write_preview_hides_implementation_aliases_from_the_user_card_grid(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest_path = write_complete_manifest(folder)
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            for state in ("busy", "open_hand", "resize_horizontal", "resize_vertical", "window_e_w"):
                write_png(folder / f"{state}.png")
                data["cursors"][state] = {
                    "path": f"{state}.png",
                    "identifier": build_cape.SUPPORTED_STATE_IDENTIFIERS[state],
                    "hotspot": [16, 16],
                }
            manifest_path.write_text(json.dumps(data), encoding="utf-8")
            preview = build_cape.write_preview(build_cape.load_manifest(manifest_path), folder, folder / "preview.svg")
            content = preview.read_text(encoding="utf-8")

        self.assertEqual(content.count('class="cursor-card"'), 8)
        self.assertNotIn('class="state-code">window_e_w</text>', content)

    def test_build_cape_accepts_supported_extended_states(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = write_complete_manifest(folder)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            for state in ("link", "busy", "wait", "zoom_in", "resize_horizontal"):
                write_png(folder / f"{state}.png")
                data["cursors"][state] = {
                    "path": f"{state}.png",
                    "identifier": build_cape.SUPPORTED_STATE_IDENTIFIERS[state],
                    "hotspot": [16, 16],
                }
            manifest.write_text(json.dumps(data), encoding="utf-8")
            cape = plistlib.loads(build_cape.build_cape(manifest, folder / "theme.cape").read_bytes())
        self.assertIn("com.apple.cursor.42", cape["Cursors"])
        self.assertIn("com.apple.cursor.19", cape["Cursors"])

    def test_build_cape_accepts_exact_directional_and_busy_aliases(self) -> None:
        """Apps request these IDs separately; one generic resize cursor is insufficient."""
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = write_complete_manifest(folder)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            for state in ("resize_east", "resize_west", "resize_north", "resize_south", "wait"):
                write_png(folder / f"{state}.png")
                data["cursors"][state] = {
                    "path": f"{state}.png",
                    "identifier": build_cape.SUPPORTED_STATE_IDENTIFIERS[state],
                    "hotspot": [16, 16],
                }
            manifest.write_text(json.dumps(data), encoding="utf-8")
            cape = plistlib.loads(build_cape.build_cape(manifest, folder / "theme.cape").read_bytes())

        self.assertEqual(cape["Cursors"]["com.apple.cursor.18"]["HotSpotX"], 16)
        self.assertIn("com.apple.coregraphics.Wait", cape["Cursors"])


if __name__ == "__main__":
    unittest.main()
