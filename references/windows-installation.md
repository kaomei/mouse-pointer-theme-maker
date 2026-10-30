# Windows 10/11 installation

The Windows package contains 15 `.cur` files, a `runtime` folder with high-resolution PNGs, three size-specific PowerShell installers, and one restore script. Each `.cur` includes native 32×32, 64×64, 96×96, and 128×128 resources generated from the same transparent artwork canvas. It does not use Mousecape and does not require administrator permission.

## Install

1. Extract the entire Windows folder and keep it for the restore script.
2. Choose one installer in File Explorer, then right-click it and choose **Run with PowerShell**:
   - `install-current-user-小.ps1` applies 64×64.
   - `install-current-user-中.ps1` applies 96×96.
   - `install-current-user-大.ps1` applies 128×128.
3. Review the normal Windows confirmation prompt, then allow it only if the folder is the expected theme package.
4. The selected size applies immediately. The same size is reapplied for the current user at every logon.

The selected script writes only current-user values under `HKCU\\Control Panel\\Cursors` and `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`. It copies the cursor files, selected-size runtime PNGs, and the startup script to `%LOCALAPPDATA%`, then creates matching `HCURSOR` objects with `CreateIconIndirect` and immediately applies them with `SetSystemCursor`. It does not ask for administrator permission and must never be run by the agent.

## Restore

Right-click `restore-default.ps1` and choose **Run with PowerShell**. It removes the package's startup entry, restores the 15 cursor-role values saved before the first size installation, and refreshes the current session. If a user has manually customized cursors after installation, tell them to choose their preferred scheme in **Mouse Properties → Pointers** instead of using the restore script.

## Limits

Windows applications choose their cursor roles independently. Arrow, text, link and resizing are common. Busy, background-working, unavailable and handwriting roles can be rare or replaced by in-app UI.
