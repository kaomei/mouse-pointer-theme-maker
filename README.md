# Mouse Pointer Theme Maker

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (Brasil)](README.pt-BR.md)

**Your favorite character shouldn't stay trapped in a picture. Put them under your fingertips.**

Turn a mascot, original IP, anime-inspired character, or even a half-formed visual idea into a complete mouse pointer theme for macOS or Windows—designed state by state, previewed in HD, and packaged only after you love the result.

**Choose a character. Pick a style. Get an entire pointer world built around it.**

✦ **3 distinctive art styles · 8 expressive states · macOS & Windows**
✦ Upload a reference image—or simply name the character you have in mind
✦ See the complete high-resolution preview before receiving any installation files

From sleepy pixel mascots and adorable chibi characters to wildly expressive visual jokes, every pointer is designed to feel like part of the character—not a picture awkwardly pasted onto an arrow.

## Featured themes

### Kaozai · Retro Pixel

Authentic 16/32-bit pixel construction, crisp functional silhouettes, and the mascot’s unmistakable sleepy expression.

![Kaozai retro pixel eight-state mouse pointer theme](examples/kaozai-retro-pixel/preview.png)

### Kaomeier · Chibi Anime

A polished Q-version character set built around a blue bear hood, expressive reactions, and readable cursor symbols.

![Kaomeier chibi anime eight-state mouse pointer theme](examples/kaomeier-chibi-anime/preview.png)

### Palace Drama · Abstract Expression

Exaggerated poses, visual metaphors, and meme-like timing show how the abstract style can be funny without being limited to parody.

![Palace drama abstract-expression eight-state mouse pointer theme](examples/zhenhuan-abstract-expression/preview.png)

> The red cross marks the real hotspot for review. It is never included in the installed pointer artwork.

## From an idea to an installable theme

1. Choose **macOS** or **Windows 10/11**.
2. Provide a character name, an original mascot, or a reference image and choose an art direction.
3. Review one high-resolution PNG showing all eight states.
4. After approval, receive only the package for the selected platform.

The preview always comes first. The skill does not build a `.cape`, `.cur` package, or installation archive before explicit approval.

## Art directions

| Style | What it means |
| --- | --- |
| `retro-pixel` | Purpose-built 16/32-bit pixel art with sharp silhouettes and intentional color clusters |
| `chibi-anime` | Cute Q-version characters, expressive poses, clean outlines, and cohesive accessories |
| `abstract-expression` | Exaggeration, visual metaphor, surreal humor, folk-art energy, or meme-like reactions |

## Eight practical states

| State | Function |
| --- | --- |
| `normal` | Ordinary selection |
| `text` | Text insertion |
| `action` | Link or button |
| `forbidden` | Unavailable action |
| `busy` | Processing or waiting |
| `open_hand` | Moving a canvas or object |
| `resize_horizontal` | Left/right resizing |
| `resize_vertical` | Up/down resizing |

The same eight original artworks expand to 51 mapped macOS cursor identifiers and 15 Windows cursor roles. Applications still decide which cursor type to request, so uncommon states may not appear in every app.

## Install the Codex skill

**Runtime requirement (workflow version 1.1.0):** the session needs a real image-generation tool that accepts references and returns image files. Installing this skill does not enable image generation. A chat model or Responses-compatible endpoint alone is insufficient; unavailable generation stops explicitly rather than producing scripted substitute artwork.

Python 3 and Pillow are required for local resizing and rendering (`python3 -m pip install Pillow`, or `py -3 -m pip install Pillow` on Windows). Resizing no longer requires macOS `sips`. Supported image tools may run independent jobs in batches of 2–3 after the first style anchor is reviewed; other tools run sequentially. Passing states are retained and only failed states are repaired. Duration and artwork vary by provider; gallery examples are not identical-output guarantees.

When upgrading, move old skill folders—including the legacy `macos-cursor-skin`—outside the skills directory before installing the new version. Renaming a backup inside the skills directory can leave it discoverable. Restart Codex and check the loaded skill path and version. A per-run `generation-record.json` records provider and state output evidence without credentials or full conversation logs.

```bash
git clone https://github.com/kaomei/mouse-pointer-theme-maker.git
mkdir -p ~/.codex/skills
cp -R mouse-pointer-theme-maker ~/.codex/skills/mouse-pointer-theme-maker
```

Restart Codex, then try:

```text
Use $mouse-pointer-theme-maker.
Computer: macOS
Style: retro-pixel
Theme: Turn my blue mascot reference into a complete pointer theme.
```

The skill first asks for the computer platform, introduces all three styles, and confirms the character/theme. It then generates the PNG review sheet before discussing installation.

## Platform delivery

### macOS

The approved artwork is packaged as a `.cape` theme. Importing and applying it requires the third-party [Mousecape SwiftUI releases](https://github.com/sdmj76/Mousecape-swiftUI/releases). This repository never bundles or redistributes the Mousecape application. Review its own license before use, especially for commercial workflows.

### Windows

The approved artwork is packaged as 15 `.cur` roles with an opt-in current-user PowerShell installer and a restore script. The installer writes only `HKCU\Control Panel\Cursors` and does not require administrator access.

## Quality guarantees

- User-facing previews are 2440×1388 PNG or larger.
- Cards render from 320×320 source artwork, never enlarged 32×32 icons.
- Hotspots sit on the arrow tip, I-beam center, pointing fingertip, palm, or resize control.
- Safe-border validation rejects clipped artwork and crop-edge residue.
- macOS and Windows are always delivered as separate packages.
- User references, downloaded applications, and generated install packages are excluded from the public repository.

## Important limitations

- Some applications draw their own pointers or keep requesting the normal arrow.
- Busy, forbidden, pan, and resize states can be rare depending on the app.
- Character names and reference images are treated as creative briefs, never as official licensing or endorsement.
- Only submit or publish imagery you have the right to use.

## Repository structure

```text
agents/       Codex UI metadata
assets/       Reusable manifest template
examples/     Curated high-resolution theme previews
references/   Style, state, platform, and installation guidance
scripts/      Preview, package, validation, and conversion tools
tests/        Contract and package tests
SKILL.md      Main Codex skill workflow
```

## Contributing

Issues and pull requests are welcome. Keep functional cursor cues clear, preserve hotspot accuracy, add no third-party application binaries, and run:

```bash
python3 -m unittest discover -s tests -v
```

## License

The skill source is available under the [MIT License](LICENSE). Example character artwork remains subject to the rights of its respective creator and is provided for demonstration; it is not an official product or endorsement.
