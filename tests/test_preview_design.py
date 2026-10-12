from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_cape
import preview_design
from test_build_cape import write_complete_manifest, write_padded_png


class PreviewDesignTests(unittest.TestCase):
    def test_hotspot_uses_actual_display_canvas_for_all_eight_cards(self):
        for i in range(8):
            x, y, size = preview_design.art_box(i)
            self.assertEqual(preview_design.hotspot_position(i, [16, 16]), (x+size/2, y+size/2))
            self.assertEqual(preview_design.hotspot_position(i, [0, 0]), (x, y))

    def test_long_chinese_title_shrinks_to_fit(self):
        path = preview_design.font_path(True)
        title = '一套包含很多不同角色的多巴胺主题鼠标皮肤'
        fitted = preview_design.fit_font(title, path, 101, 1620)
        self.assertLessEqual(fitted.getlength(title), 1620)
        self.assertLess(fitted.size, 101)

    def test_missing_cjk_font_has_actionable_error(self):
        with patch.object(Path, 'is_file', return_value=False):
            with self.assertRaisesRegex(ValueError, 'Noto Sans CJK'):
                preview_design.font_path(True)

    def test_windows_font_can_be_resolved_without_macos_fonts(self):
        with patch.object(Path, 'is_file', lambda p: p.name == 'msyhbd.ttc'), patch.object(preview_design.ImageFont, 'truetype'):
            self.assertEqual(preview_design.font_path(True).name, 'msyhbd.ttc')

    def test_large_source_preserves_hotspot_and_does_not_change_manifest(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = build_cape.load_manifest(write_complete_manifest(folder))
            source = write_padded_png(folder / 'master.png', 1024, (20, 180, 90, 255))
            cursor = manifest['cursors']['normal']
            cursor.update(preview_source=source.name, character_name='特别长的角色展示名称', hotspot=[16, 16])
            before = cursor.copy()
            path = build_cape.write_preview_png(manifest, folder, folder / 'preview.png')
            self.assertEqual(cursor, before)
            with Image.open(path) as image:
                self.assertEqual(image.size, (2440, 1600))
                hx, hy = preview_design.hotspot_position(0, cursor['hotspot'])
                self.assertEqual(image.getpixel((int(hx), int(hy)))[:3], (255, 69, 104))

    def test_preview_source_rejects_clipped_art(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = build_cape.load_manifest(write_complete_manifest(folder))
            Image.new('RGBA', (512, 512), 'red').save(folder / 'bad.png')
            manifest['cursors']['normal']['preview_source'] = 'bad.png'
            with self.assertRaisesRegex(ValueError, 'safe transparent border'):
                build_cape.write_preview_png(manifest, folder, folder / 'preview.png')


if __name__ == '__main__':
    unittest.main()
