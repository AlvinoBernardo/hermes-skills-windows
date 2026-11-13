---
name: macos-printing
description: "Use when finding, setting up, or printing to a Mac or Windows printer."
version: 1.1.0
platforms: [macos, windows]
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [printing, cups, macos, windows, printer, driver]
    related_skills: [pdf, docx]
---

# macOS printing (detect → driver → queue → print)

## When to Use
- "Can you detect my printer?", "print this", "set up my printer", printer not showing / no driver.
- Any request to put a file (PDF, image, doc, text, slides) on paper.

The user's known printer is in memory (CUPS queue name + model). Check `lpstat -p -d` first; if the queue exists and is idle, skip straight to **Print**.

## 1. Detect
```bash
lpstat -p -d; lpstat -v                       # configured queues + default
lpinfo -v                                      # lists 'direct usb://...' for plugged-in USB printers even when NOT added
for s in _ipp._tcp _ipps._tcp _pdl-datastream._tcp _printer._tcp; do
  perl -e 'alarm 4; exec @ARGV' dns-sd -B $s local.; done   # network printers
```
- `lpinfo -v` is the reliable USB detector — `system_profiler SPPrintersDataType` only shows *added* printers and SPUSBDataType grep for "print" often misses them. Keep the exact `usb://...?serial=...` URI for step 3.
- The terminal tool rejects `&` backgrounding in foreground commands; bound blocking browsers like `dns-sd -B` with `perl -e 'alarm N; exec @ARGV' cmd` instead.

## 2. Driver
```bash
lpinfo -m | grep -i <model>     # is a PPD already installed?
```
- No match → get the **official vendor driver** for the current macOS version. For Epson: Epson Europe support page / download-center.epson.com lists the macOS 26 "Printer Driver" .dmg (direct `download.epson-europe.com/pub/download/...dmg`). Avoid third-party driver-mirror sites (printerdrivers.com, zofti, etc.) — unsigned/outdated bundles.
- Download with `curl -L -f -o ~/Downloads/<name>.dmg <url>`, `hdiutil attach -nobrowse`, then verify before opening:
  `pkgutil --check-signature <pkg>` → must show the vendor's Developer ID Installer + "Notarization: trusted by the Apple notary service". When the user asks "is it safe?", answer from these facts (official source domain, vendor signature, notarized, standard driver, uninstallable via vendor uninstaller).
- Install needs admin: test `sudo -n true`. If a password is required, `open <pkg>` to launch the Installer GUI, tell the user the exact clicks (Continue → Agree → Install → password → Close), then end the turn and wait. Never type or ask for the password in chat.
- After the user says done, re-run `lpinfo -m | grep -i <model>` to get the PPD path (Epson: `Library/Printers/PPDs/Contents/Resources/EPSON <Model> Series.gz`).

## 3. Add queue
```bash
lpadmin -p <QUEUE> -D "<Model>" -L USB -v "<usb URI from lpinfo -v>" -m "<PPD path from lpinfo -m>" -E -o printer-is-shared=false
lpoptions -d <QUEUE>            # make default
lpoptions -p <QUEUE> -l          # vendor option names (paper size, quality, grayscale)
```
Works without sudo for an admin user. The "Printer drivers are deprecated" warning from lpadmin is harmless.

## 4. Test + print
- Prove it works with a tiny one-page plain-text test (saves ink): `lp -d <QUEUE> -t "Hermes test page" test.txt`, then poll `lpstat -o <QUEUE>` / `lpstat -W completed -o <QUEUE>` until the job leaves the queue. Tell the user to check the tray (blank/streaky page = nozzle clean, not a setup issue).
- Common options: `-n 2` copies, `-o page-ranges=2-4`, `-o media=A4|Letter|4x6`, `-o sides=two-sided-long-edge` (if supported), vendor grayscale/quality keys from `lpoptions -l` (Epson: `EPIJ_Ink_`, `EPIJ_Qual`).
- After first successful setup, save the queue name/model to memory so later sessions print directly.

## 5. Printing photos/images — save paper by default
- Check sizes first: `sips -g pixelWidth -g pixelHeight <files>`. Never print one small image alone on a full page; tile all images from the request onto as few A4 sheets as possible. Run `python3 scripts/contact_sheet.py OUT.pdf img1 img2 ...` (2×3 grid, 300 dpi, aspect preserved; also writes `_preview.png`). `--cols/--rows` change the grid.
- Look at `_preview.png` before sending (all images present, none clipped), then `lp -d <QUEUE> -o media=A4 OUT.pdf`.
- Warn in one line about tiny sources (under ~400 px, they print soft) and near-solid-black images (they use a lot of ink).
- Save to `~/Desktop/Print-<date>/` and show the preview in the reply. "Reprint" means sending the same saved PDF again.

## 6. Wrong colours / faded / missing colours
The print has a colour cast (pink = no cyan/yellow, green = no magenta, etc.) → see `references/ink-color-troubleshooting.md`. First prove the file is neutral (average RGB of the sheet), then walk the user through the hardware ladder. Don't re-print hoping it fixes itself.

## User preference
- "Do it for me" means drive the whole flow (find driver, download, verify, open installer, add queue, test print); only hand off the password step.
- The user often writes in all caps and is frustrated during printer problems. Give a short numbered next action, not long explanations. When they paste an Epson dialog and ask "what does this mean", explain it in 2–3 plain bullets and say whether to click it.

## On Windows (this PC)
No CUPS (`lp`/`lpstat`/`lpadmin`/`lpinfo`/`sips`/`open` don't exist). Run PowerShell via a `.ps1` file + `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/...` (inline `$_` breaks in git-bash). Verified read-only here: `Get-Printer` lists **EPSON L120 Series** (USB001, Normal), Microsoft Print to PDF, AnyDesk Printer; the default is EPSON L120.

- **Detect:** `Get-Printer | Select Name,DriverName,PortName,PrinterStatus`. `Get-Printer`'s `Default` column is blank — get the default with `(Get-CimInstance Win32_Printer | ? Default).Name`. Plugged-in but not-added USB printers: `Get-PnpDevice -Class Printer,PrintQueue`. Driver: Windows Update usually has it; otherwise the vendor installer (Epson: official download page, check Authenticode with `Get-AuthenticodeSignature <exe>`), then `Add-Printer -Name X -DriverName "<name>" -PortName USB001`. Set default: `(New-Object -ComObject WScript.Network).SetDefaultPrinter('EPSON L120 Series')`.
- **Queue:** `Get-PrintJob -PrinterName "<name>"`; cancel `Remove-PrintJob`; settings `Get-PrintConfiguration -PrinterName "<name>"` / `Set-PrintConfiguration -PrinterName … -PaperSize A4 -Color $false -DuplexingMode TwoSidedLongEdge`.
- **Print a PDF/image:** best is SumatraPDF (`winget install SumatraPDF.SumatraPDF`): `SumatraPDF.exe -print-to "EPSON L120 Series" -print-settings "paper=A4,fit,1x" file.pdf` (silent). Fallback: `Start-Process -FilePath file.pdf -Verb Print` (uses the default PDF app and default printer; Edge/Acrobat may open UI). Images: `mspaint /pt file.png "EPSON L120 Series"`. Plain text: `Get-Content test.txt | Out-Printer -Name "EPSON L120 Series"`. Not installed here: SumatraPDF — ask before installing.
- **Test page (saves ink):** one-page text via `Out-Printer`, then poll `Get-PrintJob` until empty. Never print without the user's ask.
- **Photos:** `scripts/contact_sheet.py` runs unchanged on Windows (needs only Pillow, no fonts, no `python3` alias): use a venv with Pillow, e.g. `C:/Users/<you>/IkkimiAssets/engine/.venv/Scripts/python.exe scripts/contact_sheet.py OUT.pdf a.png b.jpg` (tested with 2 images: 1 page A4 PDF + `_preview.png`). Image sizes: `python -c "from PIL import Image; print(Image.open(f).size)"` instead of `sips`. Save under `~/Desktop/Print-<date>/` (or `%USERPROFILE%\Desktop`).
- Colour/fading issues: `references/ink-color-troubleshooting.md` still applies (Epson Status Monitor / printer properties → Maintenance → Nozzle Check on Windows).
