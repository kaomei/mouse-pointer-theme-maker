# Default preview design (1.1.1)

Use `scripts/render_preview.py` to render the default user-facing PNG. Its 4×2 layout uses a bold Chinese title, large character artwork, white cards with light tinted art areas, small English state IDs, and one footer explaining hotspot marks. The eight-state canvas is 2440×1600. Do not repeat installation notes inside every card or use a decorative serif face for the main title.

Optional manifest display fields:

```json
{
  "theme": {
    "preview_title": "王者峡谷 多巴胺小队",
    "preview_subtitle": "八位英雄，把快乐带到指尖。",
    "platform": "macos"
  },
  "cursors": {
    "normal": {
      "character_name": "瑶",
      "preview_source": "normalized/normal.png"
    }
  }
}
```

These fields supplement the existing theme and cursor fields, not replace them. Set `platform` from the user's selected platform; omit it if unknown. A card with `character_name` puts the hero name and Chinese function label on separate lines so long names do not collide. Without it, the Chinese function label is primary. Full state identifiers remain visible in small text. Long titles and names are sized to fit; overlong text fails with a clear request for a shorter display title rather than clipping.

`preview_source` is optional: a reviewed, square alpha PNG at least 320px with safe transparent margins. It must use EXACTLY the same normalized canvas and hotspot coordinate ratio as all cursor representations. It is display-only, never an installed cursor resource. Use the normalized high-resolution original when available to keep the enlarged art crisp; otherwise use the largest approved representation. Never recrop a preview source independently or upscale a 32px icon. Red crosses are drawn on the preview only, at the manifest's hotspot ratio.

Fonts are resolved from locally available HarmonyOS Sans SC, Windows Microsoft YaHei/SimHei, macOS PingFang/Heiti, or Linux Noto Sans CJK/WenQuanYi. No font download is automatic and no third-party font is redistributed. If no Chinese font is available, install Noto Sans CJK or set `theme.preview_font` to a local CJK TTF/OTF/TTC path. The renderer fails clearly instead of producing unreadable square glyphs. An override applies to both weights, so choose a bold readable Chinese font for the approved appearance.

The SVG is an internal engineering view and may retain its simpler layout; PNG is the approval artifact. Inspect the generated PNG at full size: all eight characters and labels must be complete, text must not overlap, and crosses must match the installed cursor hotspots.
