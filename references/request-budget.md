# Request budget and 413 recovery

Use this reference only when the client, gateway, or API reports an oversized request or when a cursor generation turn is becoming large.

## Keep the payload small

- Treat the active prompt as a small work order, not a copy of the Skill. Refer to this Skill and read only the one state/style reference needed for the current job.
- Keep one state per image-generation job. Do not send eight prompts, every reference document, and a complete transcript in one request.
- Attach the character image through the client's normal image/file input. Never paste a local image as Base64, data URI, hex, or a giant OCR dump into the prompt.
- Do not echo full tool outputs, manifests, SVGs, stack traces, or generated image bytes back into the next model request. Keep only a short result summary such as `state=action; output=action.png; hotspot=(7,12)`.
- Render the 4×2 approval card locally from the approved state PNGs. The card is an output artifact, not input context for another generation request.
- When revising one state, attach only that state's source/reference and the brief identity lock. Do not resend all eight images unless the model genuinely needs a comparison.

## Recovery sequence for HTTP 413

1. Cancel the current retry loop. A 413 means the gateway rejected the request body before the model processed it; sending the same body again will not help.
2. Preserve the user's intent in a compact recovery record:

   ```text
   platform: macos | windows
   style: retro-pixel | chibi-anime | abstract-expression
   theme: <short name>
   current state: <one state>
   identity lock: <short visual traits>
   output: one square transparent PNG, crisp edges, safe margin, hotspot clear
   ```

3. Remove old transcript, duplicate attachments, raw logs, full documents, and unused state prompts. Reattach only the single required reference image.
4. Retry once with the compact record. If it succeeds, continue one state at a time and rebuild the local preview.
5. If it fails with 413 again, stop and tell the user the configured proxy/server limit is too small. Do not retry more, create a partial archive, or report a successful generation.

## Server-side note

When the API service is under the user's control, inspect the reverse proxy and upstream body limits (for example Nginx `client_max_body_size` and the application request limit). Raising those limits is an administrator action outside this Skill; never attempt to change a remote service silently.
