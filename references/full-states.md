# Essential cursor state catalog

Use only `assets/essential-theme-manifest.json`. It covers the eight useful, common states below.

| State | Required cue | Hotspot guidance |
| --- | --- | --- |
| `normal` | arrow | arrow tip |
| `text` | I-beam | centre of beam |
| `action` | pointing hand | fingertip |
| `forbidden` | crossed circle | centre |
| `busy` | working cue | centre |
| `open_hand` | open hand | palm |
| `resize_horizontal` | horizontal double-headed arrow | centre |
| `resize_vertical` | vertical double-headed arrow | centre |

## Compatibility promise

`normal`, `text`, `action`, and `forbidden` are the reliable core. Busy, pan, and resize are useful enhancements, but the Mac app chooses which type it requests. A theme may install correctly even if a particular app never displays resize or pan states.

## Hotspot rule

The hotspot is where a click or insertion occurs, not the visual centre. For every package, run `validate_hotspots.py` and inspect its red-cross preview. A hotspot must be on an opaque functional pixel. A character may never cover or displace the arrow tip, I-beam centre, or pointing fingertip.
