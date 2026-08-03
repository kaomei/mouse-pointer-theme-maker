# Beginner installation guide

Use the current Mousecape SwiftUI release obtained directly from its official upstream Releases page: <https://github.com/sdmj76/Mousecape-swiftUI/releases>. Do not recommend the old Mousecape 1813 archive to users on current macOS. Never bundle, mirror, or redistribute the Mousecape application with a generated theme.

1. Open the Release archive downloaded from the upstream project and wait for macOS to unpack it.
2. Open the unpacked folder and drag `Mousecape.app` to **Applications**.
3. Open **Applications**, then open Mousecape. If macOS says the developer cannot be verified, `control`-click Mousecape, choose **Open**, then choose **Open** again.
4. In Mousecape, use its helper/install option if it is shown and enter the Mac login password only in the normal macOS password dialog.
5. Double-click `<theme-name>.cape`, or open it from Mousecape. Confirm the theme appears in the list.
6. Select or right-click the theme and choose **Apply**.
7. Test the arrow, text field, link/button and disabled control. Explain that individual apps may not request every cursor state.

## Troubleshooting

| What the user sees | Give this fix |
| --- | --- |
| “This version cannot be opened on this Mac” | Delete the old archive and use the downloaded SwiftUI release, not Mousecape 1813. |
| “Developer cannot be verified” | `control`-click the app → **Open** → **Open**. |
| Theme imports but nothing changes | Reopen Mousecape, run its helper/install action if shown, then Apply the theme again. |
| Only the arrow changes | This is expected in apps that do not request text, link, or forbidden cursor types. |

Do not instruct users to run Terminal commands unless normal app installation has failed and they explicitly want an advanced recovery path.
