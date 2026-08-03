# Standard exact-ID coverage

Mousecape replaces the cursor identifier requested by an application. It does not infer that a control is “a resize control” or “a disabled button.” Therefore a package with only one horizontal and one vertical resize ID will miss programs that request a cardinal-direction or diagonal ID.

Create only these eight original artworks, then use `scripts/expand_standard_coverage.py` before building the `.cape`:

| Original artwork | Exact identifiers covered |
| --- | --- |
| `normal` | Arrow, small Arrow, context Arrow, zoom, help, crosshair, cell, camera, empty |
| `text` | I-beam, small I-beam, XOR I-beam, horizontal I-beam |
| `action` | pointing hand, link, context menu, copy, copy drag, alias |
| `forbidden` | forbidden, poof/remove |
| `busy` | busy and system wait |
| `open_hand` | open hand, closed hand, move |
| `resize_horizontal` | generic west-east resize, west resize, east resize, and native Window E / E-W / W borders |
| `resize_vertical` | generic north-south resize, north resize, south resize, count up/down, and native Window N / N-S / S borders |
| `resize_horizontal` / `resize_vertical` | native Window NE / NW / SE / SW and the two diagonal Window resize variants |

The resulting manifest contains 51 unique IDs. The eight-artwork preview remains the approval gate because aliases intentionally reuse approved art and hotspots.

## What this can and cannot solve

This exact mapping makes common system cursor variants substantially more likely to show: left/right/up/down and diagonal resizing no longer depend on one generic ID. Crucially, it includes both generic `Resize` and native window-border `Window` cursor families, as well as both busy identifiers.

It cannot force an app that uses a custom-drawn cursor, a web app with CSS cursor overrides, or a control that continues to request the normal Arrow. A disabled button or window close button usually does not request `forbidden`; seeing an arrow there is normal macOS behavior, not a failed package.
