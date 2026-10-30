from __future__ import annotations

import struct
import shutil
import subprocess
import re
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


def write_rgba_png_size(path: Path, size: int) -> Path:
    rows = []
    for y in range(size):
        pixels = bytearray()
        for x in range(size):
            pixels.extend((x % 256, y % 256, 255 - x % 256, 255 if (x + y) % 2 else 0))
        rows.append(b"\x00" + bytes(pixels))
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    content = b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header)
    content += png_chunk(b"IDAT", zlib.compress(b"".join(rows))) + png_chunk(b"IEND", b"")
    path.write_bytes(content)
    return path


def write_high_resolution_theme(folder: Path) -> Path:
    states = {
        "normal": ("com.apple.coregraphics.Arrow", [26, 10]),
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
        write_rgba_png_size(folder / f"{state}@2x.png", 64)
        write_rgba_png_size(folder / f"{state}@5x.png", 160)
        source = write_rgba_png_size(folder / f"{state}-normalized.png", 320)
        write_rgba_png_size(folder / f"{state}@10x.png", 320)
        cursors[state] = {
            "path": f"{state}.png",
            "representations": [f"{state}.png", f"{state}@2x.png", f"{state}@5x.png", f"{state}@10x.png"],
            "preview_source": source.name,
            "identifier": identifier,
            "hotspot": hotspot,
        }
    manifest = folder / "manifest.json"
    manifest.write_text(json.dumps({"theme": {"name": "Test Theme"}, "cursors": cursors}), encoding="utf-8")
    return manifest


class BuildWindowsCursorTests(unittest.TestCase):
    def test_theme_install_slug_is_stable_and_distinguishes_sanitized_collisions(self) -> None:
        first = build_windows_cursor._safe_theme_slug("A/B")
        second = build_windows_cursor._safe_theme_slug("A B")

        self.assertEqual(first, build_windows_cursor._safe_theme_slug("A/B"))
        self.assertNotEqual(first, second)

    def test_generated_powershell_scripts_have_utf8_bom_and_compile(self) -> None:
        powershell = shutil.which("powershell.exe") or shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            self.skipTest("PowerShell is required to parse generated Windows scripts")

        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = write_high_resolution_theme(folder)
            package = build_windows_cursor.build_windows_theme(manifest, folder / "windows")

            scripts = list(package.glob("*.ps1"))
            self.assertEqual(len(scripts), 4)
            for script in scripts:
                self.assertTrue(script.read_bytes().startswith(b"\xef\xbb\xbf"), script.name)
                ps_path = str(script.resolve()).replace("'", "''")
                command = (
                    "$tokens=$null; $errors=$null; "
                    f"[System.Management.Automation.Language.Parser]::ParseFile('{ps_path}',[ref]$tokens,[ref]$errors) | Out-Null; "
                    "if($errors.Count){$errors | ForEach-Object { Write-Error $_ }; exit 1}"
                )
                result = subprocess.run(
                    [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                script_text = script.read_text(encoding="utf-8-sig")
                signature = re.search(r"\$signature = @'\r?\n(.*?)\r?\n'@", script_text, re.DOTALL)
                if signature is not None:
                    source = folder / f"{script.stem}.cs"
                    source.write_text(signature.group(1), encoding="ascii")
                    compile_command = f"Add-Type -Path '{str(source.resolve()).replace(chr(39), chr(39) * 2)}' -ReferencedAssemblies 'System.Drawing','System.dll'"
                    result = subprocess.run(
                        [powershell, "-NoProfile", "-NonInteractive", "-Command", compile_command],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_write_cur_embeds_32_and_64_pixel_representations(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            source_32 = write_rgba_png(folder / "source.png")
            source_64 = write_rgba_png_size(folder / "source@2x.png", 64)
            output = build_windows_cursor.write_cur([source_32, source_64], folder / "Arrow.cur", (2, 3))
            parsed = build_windows_cursor.parse_cur(output.read_bytes())

        self.assertEqual(parsed["count"], 2)
        self.assertEqual(parsed["sizes"], [(32, 32), (64, 64)])
        self.assertEqual(parsed["hotspot"], (2, 3))

    def test_parse_cur_rejects_out_of_bounds_hotspots_and_inconsistent_bitmap_height(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            source = write_rgba_png(folder / "source.png")
            cursor = build_windows_cursor.write_cur(source, folder / "Arrow.cur", (2, 3)).read_bytes()

        invalid_hotspot = bytearray(cursor)
        struct.pack_into("<H", invalid_hotspot, 6 + 4, 32)
        with self.assertRaisesRegex(ValueError, "unsupported CUR bitmap"):
            build_windows_cursor.parse_cur(bytes(invalid_hotspot))

        invalid_height = bytearray(cursor)
        image_offset = struct.unpack_from("<I", invalid_height, 6 + 12)[0]
        struct.pack_into("<i", invalid_height, image_offset + 8, 32)
        with self.assertRaisesRegex(ValueError, "unsupported CUR bitmap"):
            build_windows_cursor.parse_cur(bytes(invalid_height))

    def test_write_cur_embeds_four_native_sizes_and_scaled_hotspots(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            sources = [write_rgba_png(folder / "normal-32.png")]
            sources.extend(write_rgba_png_size(folder / f"normal-{size}.png", size) for size in (64, 96, 128))
            output = build_windows_cursor.write_cur(sources, folder / "Arrow.cur", (26, 10))
            parsed = build_windows_cursor.parse_cur(output.read_bytes())

        self.assertEqual(parsed["sizes"], [(32, 32), (64, 64), (96, 96), (128, 128)])
        self.assertEqual(parsed["hotspots"], [(26, 10), (52, 20), (78, 30), (104, 40)])

    def test_write_cur_rejects_unsorted_sizes(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            source_32 = write_rgba_png(folder / "source.png")
            source_64 = write_rgba_png_size(folder / "source@2x.png", 64)
            with self.assertRaisesRegex(ValueError, "ascending size order"):
                build_windows_cursor.write_cur([source_32, source_64, source_64], folder / "Arrow.cur", (2, 3))

    def test_build_windows_theme_rejects_missing_high_resolution_source(self) -> None:
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
                invalid_2x = folder / f"{state}@2x.png"
                invalid_2x.write_bytes(b"not a png")
                cursors[state] = {
                    "path": f"{state}.png",
                    "representations": [f"{state}.png", invalid_2x.name],
                    "identifier": identifier,
                    "hotspot": hotspot,
                }
            manifest = folder / "manifest.json"
            manifest.write_text(json.dumps({"theme": {"name": "Fallback Theme"}, "cursors": cursors}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "needs a transparent square preview_source or 10x PNG"):
                build_windows_cursor.build_windows_theme(manifest, folder / "windows")

    def test_build_windows_theme_uses_high_resolution_source_for_native_sizes_and_hotspots(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = write_high_resolution_theme(folder)
            package = build_windows_cursor.build_windows_theme(manifest, folder / "windows")
            arrow = build_windows_cursor.parse_cur((package / "Arrow.cur").read_bytes())
            install = (package / "install-current-user-大.ps1").read_text(encoding="utf-8-sig")
            install_small = (package / "install-current-user-小.ps1").read_text(encoding="utf-8-sig")
            install_medium = (package / "install-current-user-中.ps1").read_text(encoding="utf-8-sig")
            runtime_sizes = {
                size: build_windows_cursor.read_rgba_png(package / "runtime" / str(size) / "normal.png", size)[0]
                for size in (64, 96, 128)
            }

            from PIL import Image, ImageChops

            runtime = Image.open(package / "runtime" / "128" / "normal.png").convert("RGBA")
            source = Image.open(folder / "normal-normalized.png").convert("RGBA")
            low_res = Image.open(folder / "normal.png").convert("RGBA").resize((128, 128), Image.Resampling.LANCZOS)
            expected = source.resize((128, 128), Image.Resampling.LANCZOS)

        self.assertEqual(arrow["sizes"], [(32, 32), (64, 64), (96, 96), (128, 128)])
        self.assertEqual(arrow["hotspots"], [(26, 10), (52, 20), (78, 30), (104, 40)])
        self.assertEqual(runtime_sizes, {64: 64, 96: 96, 128: 128})
        self.assertIsNone(ImageChops.difference(runtime, expected).getbbox())
        self.assertIsNotNone(ImageChops.difference(runtime, low_res).getbbox())
        self.assertIn("CreateIconIndirect", install)
        self.assertIn("SetSystemCursor", install)
        self.assertIn("'Arrow' = @('normal', 104, 40, 32512)", install)
        self.assertIn("'Arrow' = @('normal', 52, 20, 32512)", install_small)
        self.assertIn("'Arrow' = @('normal', 78, 30, 32512)", install_medium)

    def test_build_windows_theme_writes_three_size_scripts_and_user_scoped_persistence(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = write_high_resolution_theme(folder)
            package = build_windows_cursor.build_windows_theme(manifest, folder / "windows")
            generated_names = sorted(path.name for path in package.glob("*.cur"))
            generated_install_names = sorted(path.name for path in package.glob("install-current-user-*.ps1"))
            legacy_install_exists = (package / "install-current-user.ps1").exists()
            install_scripts = {
                label: (package / f"install-current-user-{label}.ps1").read_text(encoding="utf-8-sig")
                for label in ("小", "中", "大")
            }
            install_bytes = {
                label: (package / f"install-current-user-{label}.ps1").read_bytes()
                for label in ("小", "中", "大")
            }
            restore = (package / "restore-default.ps1").read_text(encoding="utf-8")
            restore_bytes = (package / "restore-default.ps1").read_bytes()

        self.assertEqual(generated_names, [
            "AppStarting.cur", "Arrow.cur", "Crosshair.cur", "Hand.cur", "Help.cur", "IBeam.cur", "NWPen.cur", "No.cur",
            "SizeAll.cur", "SizeNESW.cur", "SizeNS.cur", "SizeNWSE.cur", "SizeWE.cur", "UpArrow.cur", "Wait.cur",
        ])
        self.assertEqual(generated_install_names, [
            "install-current-user-中.ps1", "install-current-user-大.ps1", "install-current-user-小.ps1",
        ])
        self.assertFalse(legacy_install_exists)
        self.assertIn("HKCU:\\Control Panel\\Cursors", install_scripts["小"])
        self.assertIn("$PSScriptRoot", install_scripts["小"])
        self.assertIn("CreateIconIndirect", install_scripts["小"])
        self.assertIn("SetSystemCursor", install_scripts["小"])
        self.assertIn("Windows\\CurrentVersion\\Run", install_scripts["小"])
        self.assertIn("$size = 64", install_scripts["小"])
        self.assertIn("$size = 96", install_scripts["中"])
        self.assertIn("$size = 128", install_scripts["大"])
        self.assertNotIn("UpdatePerUserSystemParameters", install_scripts["小"])
        self.assertIn("Remove-ItemProperty", restore)
        self.assertIn("cursor-backup.json", restore)
        self.assertIn("SystemParametersInfo", restore)
        for script_bytes in (*install_bytes.values(), restore_bytes):
            self.assertTrue(script_bytes.startswith(b"\xef\xbb\xbf"))
            self.assertTrue(script_bytes[3:].isascii())


if __name__ == "__main__":
    unittest.main()
