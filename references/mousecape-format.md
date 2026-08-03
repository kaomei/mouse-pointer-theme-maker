# Mousecape format used by this Skill

The package is a binary property list with these top-level fields:

| Field | Value |
| --- | --- |
| `CapeName` | Theme display name |
| `Identifier` | Stable reverse-domain theme identifier |
| `CapeVersion` | User version number |
| `Version`, `MinimumVersion` | `2` |
| `Cloud` | `false` |
| `HiDPI` | `true` for delivered Retina themes |
| `Cursors` | Dictionary keyed by cursor identifier |

Each cursor record has `FrameCount: 1`, `FrameDuration: 1.0`, `HotSpotX`, `HotSpotY`, `PointsWide: 32`, `PointsHigh: 32`, and four PNG byte strings in `Representations`: 32, 64, 160, and 320 pixels. The representations are the same cursor at 1x, 2x, 5x, and 10x display density, not distinct user choices.

The four core states are mandatory; the default skill workflow also adds busy, open-hand, and two resize states. These identifiers are taken from the current Mousecape SwiftUI cursor discovery source.

| State | Identifier | Use |
| --- | --- | --- |
| `normal` | `com.apple.coregraphics.Arrow` | ordinary selection |
| `text` | `com.apple.coregraphics.IBeam` | text entry |
| `action` | `com.apple.cursor.13` | pointing button/link |
| `forbidden` | `com.apple.cursor.3` | unavailable action |
| `link` | `com.apple.cursor.2` | link |
| `busy` / `wait` | `com.apple.cursor.4` / `com.apple.coregraphics.Wait` | working / waiting |
| `copy` / `alias` / `move` | `com.apple.coregraphics.Copy` / `Alias` / `Move` | drag operations |
| `open_hand` / `closed_hand` | `com.apple.cursor.12` / `.11` | pan/grab |
| `crosshair` / `help` / `context_menu` | `com.apple.cursor.7` / `.40` / `.24` | precision/help/menu |
| `zoom_in` / `zoom_out` | `com.apple.cursor.42` / `.43` | zoom |
| `resize_horizontal` / `resize_vertical` | `com.apple.cursor.19` / `.23` | resize |
| `resize_ne_sw` / `resize_nw_se` | `com.apple.cursor.30` / `.34` | diagonal resize |

This contract is derived from Mousecape’s public sample cape and source definitions. The identifiers are implementation details of Mousecape rather than public Apple APIs.
