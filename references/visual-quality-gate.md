# Visual quality gate

Use this gate before showing a cursor preview. Format and hotspot validation cannot replace this visual review.

## Plan eight genuinely different performances

Before image generation, write one short row per state containing: character pose, expression, physical interaction with the functional cue, protected hotspot, and identity traits that must stay unchanged. Use the state-specific direction below rather than repeating one neutral standing portrait.

| State | Required character performance |
| --- | --- |
| `normal` | Peeks from, holds, rides, or guides the arrow body while leaving its tip clear. |
| `text` | Hugs, leans on, writes beside, or peers through the I-beam; the beam centre stays clear. |
| `action` | Reaches, presses, points, or jumps into the click; the fingertip is unmistakable. |
| `forbidden` | Blocks, refuses, recoils, or protests with a state-specific expression. |
| `busy` | Runs, spins, sweats, carries work, or reacts impatiently to a visible wait cue. |
| `open_hand` | Grabs, pushes, pulls, or opens both hands as part of the pan gesture. |
| `resize_horizontal` | Pulls or braces against opposite left/right directions with a stretched horizontal pose. |
| `resize_vertical` | Climbs, lifts, hangs, or braces against opposite up/down directions with a vertical pose. |

## Build one prompt per state

Use the reference image as the identity source in every generation job. Repeat the identity lock and the state-specific action in every prompt; do not rely on an earlier job's context.

```text
Reference role: strict character identity reference, not a cutout to paste.
Identity lock: preserve the same head/face shape, signature eyes, hair or helmet,
costume pattern, accessory, palette, outline treatment, and chibi proportions.
State: <one state only>.
Performance: <pose + expression + physical interaction from the table above>.
Functional cue: <arrow / I-beam / fingertip / prohibition / wait / palm / resize axis>.
Composition: character and cue form one compact silhouette; character occupies about
35-60% of the meaningful artwork; protected hotspot remains unobstructed.
Output: one square high-resolution cursor artwork, transparent background, generous
safe margin, no label, no preview card, no watermark, no other states.
Reject: neutral standing pose, source-image copy, mascot sticker beside a stock cursor,
contact sheet, tiny character, hidden cue, cropped anatomy, identity drift, blur.
```

For `retro-pixel`, generate or redraw at a deliberate pixel-art working scale with a limited palette and hard pixel edges; do not pixelate a smooth illustration after generation. For `chibi-anime`, require clean sticker-like linework but preserve distinct body performance. For `abstract-expression`, exaggerate the action without losing the reference character's signature identity traits.

## Non-negotiable rejection rules

Mark a state `REGENERATE` if any condition is true:

- It contains the same static character pose or the same source-image cutout used in another state.
- It looks like a stock system cursor with a small mascot sticker placed beside it.
- The character does not touch, hold, push, ride, block, or otherwise interact with the functional cue.
- The functional silhouette is ambiguous at thumbnail size or the hotspot is covered by decoration.
- The character becomes an unrelated redesign: helmet, face, hair, costume, signature accessory, palette, or body proportions drift from the reference.
- The artwork relies on tiny text, labels, or a preview card to explain the state.
- It contains blur, accidental antialiasing in pixel art, crop residue, opaque background, or clipped anatomy.

Do not lower the bar because a renderer, image tool, or delivery channel failed. Repair the generation path, then show only an artwork preview that passes.

## Contact-sheet review

Inspect the eight approved images together before rendering the user-facing card:

1. **Identity:** cover the cursor symbols mentally; all eight still read as the same character.
2. **Performance:** cover the faces mentally; body pose and cue interaction still distinguish the states.
3. **Function:** view at 32×32; arrow tip, I-beam centre, fingertip, prohibition centre, palm, and resize axes remain legible.
4. **Variety:** no two states use the same body silhouette merely mirrored, shifted, or paired with another icon.
5. **Cohesion:** outline weight, rendering medium, lighting, palette, and character scale form one theme.

Record `PASS` or `REGENERATE` for each state. A preview may be shown only when all eight are `PASS`.

## Tool boundary

Image generation or image editing must create each new performance. Deterministic scripts are appropriate only after artwork approval for alpha cleanup, safe-border checks, Retina resizing, hotspot validation, card rendering, and packaging. Copying the reference character into eight cards is not a fallback and must never be presented as generated cursor art.
