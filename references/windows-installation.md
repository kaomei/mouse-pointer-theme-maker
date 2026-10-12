# Windows 10/11 installation

The Windows package contains 15 `.cur` files and two PowerShell scripts. Each `.cur` includes the validated 32×32 resource and, when the source manifest has a valid 2x file, a 64×64 resource for high-DPI selection. It does not use Mousecape and does not require administrator permission.

## Install

1. Extract the entire `windows` folder to a permanent location. Do not move or delete it after installation, because Windows reads the cursor files from that folder.
2. In File Explorer, right-click `install-current-user.ps1` and choose **Run with PowerShell**.
3. Review the normal Windows confirmation prompt, then allow it only if the folder is the expected theme package.
4. If the cursor does not refresh immediately, sign out and sign in again.

The generated script writes only `HKCU\\Control Panel\\Cursors` for the current user. It does not ask for administrator permission and must never be run by the agent.

## Restore

Right-click `restore-default.ps1` and choose **Run with PowerShell**, then sign out/in if necessary. This removes only the 15 cursor-role values created by the package. If a user has manually customized cursors after installation, tell them to choose their preferred scheme in **Mouse Properties → Pointers** instead of using the restore script.

## Limits

Windows applications choose their cursor roles independently. Arrow, text, link and resizing are common. Busy, background-working, unavailable and handwriting roles can be rare or replaced by in-app UI.
