"""Typography-led eight-state preview layout, independent of installed cursors."""
from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

WIDTH = 2440
MARGIN, GAP, CARD_WIDTH, CARD_HEIGHT, HEADER = 72, 28, 553, 580, 282
ART_SIZE = 480
ACCENTS = ('#D8F677', '#A9EEE4', '#FFBDDF', '#FFD290', '#FAEE8C', '#BDEAFF', '#C6E98F', '#D8C8FF')
TINTS = ('#F7FBEF', '#F0FAF8', '#FFF4FA', '#FFF8EF', '#FFFDF0', '#F2FAFF', '#F6FAEF', '#F8F4FF')
INK, MUTED = '#24223D', '#77718B'


def font_path(bold: bool, override: str | None = None) -> Path:
    """Find a CJK font without embedding or downloading third-party fonts."""
    if override:
        path = Path(override).expanduser()
        if not path.is_file():
            raise ValueError(f'preview font not found: {path}')
        return path
    user_fonts = Path.home() / 'Library' / 'Fonts'
    windows_fonts = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    candidates = (
        user_fonts / ('HarmonyOS_Sans_SC_Black.ttf' if bold else 'HarmonyOS_Sans_SC_Medium.ttf'),
        windows_fonts / ('msyhbd.ttc' if bold else 'msyh.ttc'),
        windows_fonts / 'simhei.ttf',
        Path('/System/Library/Fonts/PingFang.ttc'),
        Path('/System/Library/Fonts/STHeiti Medium.ttc' if bold else '/System/Library/Fonts/STHeiti Light.ttc'),
        Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if bold else '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
        Path('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'),
    )
    for path in candidates:
        if path.is_file():
            try:
                ImageFont.truetype(str(path), 24)
                return path
            except OSError:
                continue
    raise ValueError('No Chinese preview font found. Install Noto Sans CJK or set theme.preview_font to a local CJK TTF/OTF/TTC file.')


def fit_font(text: str, path: Path, maximum: int, available: int, minimum: int = 18) -> ImageFont.FreeTypeFont:
    for size in range(maximum, minimum - 1, -1):
        font = ImageFont.truetype(str(path), size)
        if font.getlength(text) <= available:
            return font
    raise ValueError(f'Preview text is too long for its area: {text!r}; use a shorter display name.')


def art_box(index: int) -> tuple[int, int, int]:
    x = MARGIN + index % 4 * (CARD_WIDTH + GAP)
    y = HEADER + index // 4 * (CARD_HEIGHT + GAP)
    return x + (CARD_WIDTH - ART_SIZE) // 2, y + 28, ART_SIZE


def hotspot_position(index: int, hotspot: list[int]) -> tuple[float, float]:
    x, y, size = art_box(index)
    return x + hotspot[0] * size / 32, y + hotspot[1] * size / 32


def render(manifest: dict[str, Any], manifest_dir: Path, records: list, output: Path, labels: dict[str, str]) -> Path:
    theme = manifest['theme']
    bold = font_path(True, theme.get('preview_font'))
    regular = font_path(False, theme.get('preview_font'))
    rows = max(1, (len(records) + 3) // 4)
    height = max(1600, HEADER + rows * CARD_HEIGHT + (rows - 1) * GAP + 130)
    styles = {
        'chibi-anime': ('#F4F3FD', '#7965F0', 'Q 版二次元'),
        'retro-pixel': ('#EEF6FF', '#387CBF', '复古像素风'),
        'abstract-expression': ('#FFF6ED', '#DA6852', '抽象表达风'),
    }
    background, accent, style_label = styles.get(theme.get('preview_style'), styles['chibi-anime'])
    image = Image.new('RGBA', (WIDTH, height), background)
    draw = ImageDraw.Draw(image)

    def text(x, y, value, maximum, available, heavy=True, color=INK):
        selected = fit_font(value, bold if heavy else regular, maximum, available)
        draw.text((x, y), value, font=selected, fill=color)

    def pill(box, fill, value, maximum, color=INK):
        draw.rounded_rectangle(box, radius=(box[3]-box[1])//2, fill=fill)
        selected = fit_font(value, bold, maximum, box[2]-box[0]-28)
        bounds = draw.textbbox((0, 0), value, font=selected)
        draw.text(((box[0]+box[2]-(bounds[2]-bounds[0]))/2, (box[1]+box[3]-(bounds[3]-bounds[1]))/2-bounds[1]), value, font=selected, fill=color)

    draw.rounded_rectangle((72, 56, 85, 221), radius=6, fill=accent)
    title = str(theme.get('preview_title', theme['name']))
    text(112, 51, title, 101, 1620)
    text(116, 183, str(theme.get('preview_subtitle', '把喜欢的角色，带到指尖。')), 34, 1620, False, MUTED)
    platform = {'macos': 'macOS', 'windows': 'Windows', 'both': 'macOS / Windows'}.get(theme.get('platform'), '鼠标主题')
    pill((1792, 64, 2368, 131), '#E4DEFF', f'{style_label}  /  {platform}', 28)
    pill((2017, 152, 2368, 213), '#D6F46C', f'鼠标皮肤 · {len(records)} 状态', 27)

    for i, (state, cursor, data) in enumerate(records):
        x = MARGIN + i % 4 * (CARD_WIDTH + GAP)
        y = HEADER + i // 4 * (CARD_HEIGHT + GAP)
        draw.rounded_rectangle((x, y+6, x+CARD_WIDTH, y+CARD_HEIGHT+6), radius=32, fill='#E7E4F2')
        draw.rounded_rectangle((x, y, x+CARD_WIDTH, y+CARD_HEIGHT), radius=32, fill='#FFFFFF')
        draw.rounded_rectangle((x+16, y+16, x+CARD_WIDTH-16, y+CARD_HEIGHT-122), radius=24, fill=TINTS[i % 8])
        pill((x+32, y+30, x+112, y+82), ACCENTS[i % 8], f'{i+1:02}', 24)
        # Keep the exact identifier visible, secondary to Chinese labels.
        code_font = fit_font(state, regular, 19, CARD_WIDTH - 176, 14)
        draw.text((x+CARD_WIDTH-32-code_font.getlength(state), y+39), state, font=code_font, fill='#8B879F')

        source = cursor.get('preview_source')
        if source:
            with Image.open(manifest_dir / source) as original:
                if original.width != original.height or original.width < 320 or 'A' not in original.getbands():
                    raise ValueError(f'{state}: preview_source must be a square alpha PNG at least 320px, with the same canvas/hotspot ratio as representations')
                art = original.convert('RGBA')
                box = art.getchannel('A').getbbox()
                border = max(1, art.width // 48)
                if not box or min(box[0], box[1], art.width-box[2], art.height-box[3]) < border:
                    raise ValueError(f'{state}: preview_source violates safe transparent border')
        else:
            art = Image.open(BytesIO(data[-1])).convert('RGBA')
        ax, ay, size = art_box(i)
        image.alpha_composite(art.resize((size, size), Image.Resampling.LANCZOS), (ax, ay))
        hx, hy = hotspot_position(i, cursor['hotspot'])
        draw.ellipse((hx-5, hy-5, hx+5, hy+5), fill='#FF4568')
        draw.line((hx-11, hy, hx+11, hy), fill='#FF4568', width=3)
        draw.line((hx, hy-11, hx, hy+11), fill='#FF4568', width=3)

        label = labels.get(state, state)
        character = cursor.get('character_name')
        if character:
            # Separate rows prevent long hero names from colliding with labels.
            text(x+32, y+CARD_HEIGHT-111, str(character), 43, CARD_WIDTH-64)
            text(x+32, y+CARD_HEIGHT-61, label, 26, CARD_WIDTH-64, False, MUTED)
        else:
            text(x+32, y+CARD_HEIGHT-95, label, 40, CARD_WIDTH-64)
        draw.line((x+32, y+CARD_HEIGHT-22, x+CARD_WIDTH-32, y+CARD_HEIGHT-22), fill=ACCENTS[i % 8], width=5)

    text(76, height-79, '红色小十字为热点校准标记，安装后的鼠标不会显示。', 26, 1750, False, MUTED)
    pill((1958, height-100, 2368, height-38), INK, '主题预览 / 确认后打包', 24, '#FFFFFF')
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format='PNG', optimize=True)
    return output
