# Generation runtime

The skill supplies workflow and packaging scripts, not an image model or an API subscription.

## Preflight

1. Inspect the session's available tools. Identify an actual image-generation/editing tool with reference-image input and file output; do not infer it from the chat model's name or operating system.
2. Prefer the built-in image tool. Follow its actual schema and concurrency documentation. Do not invent output-path, size, batch, or transparency parameters.
3. Check Python 3 and Pillow before normalization and PNG rendering (`python3 -c "import PIL"`; on Windows the interpreter may be `py -3`). Missing dependencies should be reported clearly. The user may install Pillow with that interpreter's `-m pip install Pillow`.
4. If generation is unavailable, stop artwork creation with `GENERATION_UNAVAILABLE`. Explain that installing this skill does not enable image generation. Do not silently select a third-party API, request a secret in chat, or fabricate a preview using the source image.

## Consistency and latency

Generate and review normal first. Reuse it as a style anchor alongside the original identity reference when supported. Generate the remaining states as independent compact jobs, in groups of 2–3 only when concurrent calls are documented as supported. Sequential execution remains valid otherwise. Do not promise a fixed duration; image generation dominates runtime.

Persist every successful file and its state mapping immediately. Validate and inspect completed jobs, retain passing states across interruptions, and repair only the rejected states. Limit quality repair to two targeted attempts per state; explain any remaining failure rather than returning a knowingly bad sheet.

Use local scripts for normalization and layout. No extra image call is needed to remove an already-clean white reference background or to create the final card grid. Reference images are identity guidance, not material to paste into repeated cards.

## Reproduction record

Write `generation-record.json` next to the preview with: `skill_version`, `skill_path`, `platform`, `style`, `provider`, `model` (null when unavailable), and each state's prompt, verified output path, review result, and repair count. Exclude tokens, Base64, raw logs, and conversation history. Gallery images demonstrate examples, not guaranteed identical output. Diagnose provider/tool differences before attributing appearance to macOS versus Windows.
