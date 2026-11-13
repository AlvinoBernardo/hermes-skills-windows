# Inkjet colour problems (Epson ink-tank, e.g. L120)

## Diagnose: file or printer?
- Average the sheet's RGB with PIL (`ImageStat.Stat(im).mean`). If R≈G≈B, the file is neutral and the cast comes from the hardware. Tell the user plainly that the printer is at fault, not the file.
- Cast → missing ink: pink/magenta = cyan (and often yellow) missing; green = magenta missing; blue/purple = yellow missing.
- Driver colour sliders (`EPIJ_Cyan`, `EPIJ_Mage`, etc. in `lpoptions -l`) can't compensate for a channel that isn't firing. Don't try them.

## Escalation ladder (stop as soon as the nozzle check shows all 4 colours)
1. Check the tank level of each missing colour (must be above the lower line). Check that the tank caps are seated and the ink tubes aren't kinked.
2. Open the utility: `open "/Library/Printers/EPSON/InkjetPrinter2/Utility/UT4/Epson Printer Utility 4.app"`. Run **Nozzle Check**. Hardware fallback: with the printer off, hold the ink 💧 button while pressing power.
3. Run **Head Cleaning**, then Nozzle Check again. Repeat up to 3 times. Hardware fallback: hold 💧 for 3 seconds.
4. If a colour is still completely absent: run **Power Ink Flushing** from the same utility. Requirements: each tank about ⅓ full or more, and the printer must not be powered off during the run (it can't be interrupted). It can run once per 12 hours, and quality improves over the 12 hours after it.
5. If there's still nothing after the 12-hour rest, the ink isn't reaching the head (tubes, air, or a dead head) → Epson service.

## Dialog explanations the user may ask about
- Power Ink Flushing "waste ink pads" warning: the pads are sponges inside the base, under the print head's park position on the right. They soak up flushed ink, aren't user-accessible (the case has to be opened), and have finite capacity. One flush is fine. When they're full, the printer stops with both lights blinking and needs Epson service.

## After the fix
Once the nozzle check is clean, reprint the already-saved sheet PDF. If the user reprints before the 12-hour rest, warn that colours may still be weak.
