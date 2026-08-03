from __future__ import annotations

import unittest
from pathlib import Path


SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"
AGENT_PATH = Path(__file__).resolve().parents[1] / "agents" / "openai.yaml"
INSTALLATION_PATH = Path(__file__).resolve().parents[1] / "references" / "installation.md"
STYLES_PATH = Path(__file__).resolve().parents[1] / "references" / "styles.md"
WINDOWS_BUILDER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_windows_cursor.py"
ESSENTIAL_MANIFEST_PATH = Path(__file__).resolve().parents[1] / "assets" / "essential-theme-manifest.json"
WINDOWS_INSTALLATION_PATH = Path(__file__).resolve().parents[1] / "references" / "windows-installation.md"
COMPLETE_TUTORIAL_PATH = Path(__file__).resolve().parents[1] / "references" / "complete-tutorial.md"


class SkillContractTests(unittest.TestCase):
    def test_skill_declares_mouse_pointer_theme_trigger_and_four_states(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("name: mouse-pointer-theme-maker", content)
        self.assertIn("Use when", content)
        self.assertIn("Mousecape", content)
        for state in ("normal", "text", "action", "forbidden"):
            self.assertIn(f"`{state}`", content)

    def test_skill_requires_packaging_and_validation(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("prepare_cursor.py", content)
        self.assertIn("build_cape.py", content)
        self.assertIn("validate_cape.py", content)
        self.assertIn("32×32", content)

    def test_agent_metadata_exposes_a_default_invocation_prompt(self) -> None:
        content = AGENT_PATH.read_text(encoding="utf-8")
        self.assertIn('display_name: "Mouse Pointer Theme Maker"', content)
        self.assertIn('default_prompt: "Use $mouse-pointer-theme-maker', content)

    def test_skill_includes_current_installation_flow_and_style_choices(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        installation = INSTALLATION_PATH.read_text(encoding="utf-8")
        styles = STYLES_PATH.read_text(encoding="utf-8")
        self.assertIn("Mousecape SwiftUI", installation)
        for style in ("retro-pixel", "chibi-anime", "abstract-expression"):
            self.assertIn(style, styles)
        self.assertNotIn("abstract-meme", styles)

    def test_skill_defaults_to_an_approved_eight_state_preview(self) -> None:
        import json

        skill = SKILL_PATH.read_text(encoding="utf-8")
        cursors = json.loads(ESSENTIAL_MANIFEST_PATH.read_text(encoding="utf-8"))["cursors"]
        self.assertEqual(len(cursors), 8)
        self.assertIn("Preview approval gate", skill)
        self.assertIn("Do not build a `.cape`", skill)
        self.assertIn("卡片式", skill)
        self.assertIn("10x", skill)

    def test_skill_requires_png_preview_before_install_delivery(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        for required in (
            "PNG/JPG",
            "先发送 PNG",
            "确认后再发送",
            "preview.png",
            "preview.svg 只作为内部",
        ):
            self.assertIn(required, skill)

    def test_skill_marks_hotspot_guides_as_preview_only(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("预览专用", skill)
        self.assertIn("不得写入", skill)
        self.assertIn("红色十字", skill)

    def test_mousecape_binary_is_never_bundled_or_redistributed(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        tutorial = COMPLETE_TUTORIAL_PATH.read_text(encoding="utf-8")
        downloader = SKILL_PATH.parent / "scripts" / "download_mousecape.py"
        self.assertFalse(downloader.exists())
        self.assertNotIn("Mousecape-latest.zip", skill)
        self.assertNotIn("Mousecape-latest.zip", tutorial)
        self.assertIn("https://github.com/sdmj76/Mousecape-swiftUI/releases", skill)
        self.assertIn("不得打包或再分发", tutorial)

    def test_skill_documents_windows_theme_generation(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("build_windows_cursor.py", content)
        self.assertTrue(WINDOWS_BUILDER_PATH.is_file())
        self.assertTrue(WINDOWS_INSTALLATION_PATH.is_file())

    def test_skill_requires_platform_confirmation_before_packaging(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("先确认用户平台", content)
        self.assertIn("不要把 macOS 与 Windows 打进同一个压缩包", content)
        tutorial = COMPLETE_TUTORIAL_PATH.read_text(encoding="utf-8")
        self.assertIn("先确认用户使用的是 macOS 还是 Windows", tutorial)
        self.assertNotIn("平台未知，包含两节", tutorial)

    def test_skill_starts_with_a_first_run_intake_and_answer_example(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")
        for required in (
            "首次使用提问",
            "电脑平台",
            "retro-pixel",
            "chibi-anime",
            "abstract-expression",
            "主题/角色",
            "回答示例",
        ):
            self.assertIn(required, content)

    def test_skill_forbids_crop_edge_residue(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("裁剪边缘", content)
        self.assertIn("残留线条", content)

    def test_skill_requires_automatic_safe_border_rejection(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("safe transparent border", content)
        self.assertIn("拒绝生成预览", content)
        self.assertIn("2440×1388", content)
        self.assertIn("GitHub gallery", content)

    def test_skill_requires_a_complete_cross_platform_user_tutorial(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("complete-tutorial.md", skill)
        self.assertTrue(COMPLETE_TUTORIAL_PATH.is_file())

        tutorial = COMPLETE_TUTORIAL_PATH.read_text(encoding="utf-8")
        for required_section in (
            "## macOS：从下载到应用",
            "## Windows 10/11：从解压到应用",
            "## 安装后立刻验证",
            "## 恢复默认鼠标",
            "Finder",
            "Run with PowerShell",
            "HKCU",
        ):
            self.assertIn(required_section, tutorial)


if __name__ == "__main__":
    unittest.main()
