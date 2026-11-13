# READ-ONLY disk audit for Windows. Deletes nothing.
# Usage: powershell.exe -NoProfile -ExecutionPolicy Bypass -File measure_windows.ps1 [-Deep]
param([switch]$Deep)
$ErrorActionPreference = 'SilentlyContinue'
function SizeGB($p) {
  if (-not (Test-Path -LiteralPath $p)) { return $null }
  $s = (Get-ChildItem -LiteralPath $p -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
  [math]::Round(($s / 1GB), 2)
}
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -ne $null } |
  ForEach-Object { '{0}: free {1} GB of {2} GB' -f $_.Name, [math]::Round($_.Free/1GB,1), [math]::Round(($_.Used+$_.Free)/1GB,1) }
$L = $env:LOCALAPPDATA; $H = $env:USERPROFILE
$hh = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { "$L\hermes" }
$items = [ordered]@{
  'User TEMP'                 = $env:TEMP
  'Windows TEMP'              = "$env:WINDIR\Temp"
  'Hermes cache/scratch'      = "$hh\cache\scratch"
  'Hermes cache (all)'        = "$hh\cache"
  'Hermes skills-backup*'     = $null
  'npm cache'                 = "$L\npm-cache"
  'uv cache'                  = "$L\uv\cache"
  'pip cache'                 = "$L\pip\Cache"
  'HuggingFace hub'           = "$H\.cache\huggingface"
  'torch hub'                 = "$H\.cache\torch"
  'Chrome cache'              = "$L\Google\Chrome\User Data\Default\Cache"
  'Edge cache'                = "$L\Microsoft\Edge\User Data\Default\Cache"
  'Playwright browsers'       = "$L\ms-playwright"
  'CrashDumps'                = "$L\CrashDumps"
  'WER reports'               = "$L\Microsoft\Windows\WER"
  'Downloads'                 = "$H\Downloads"
}
$rows = foreach ($k in $items.Keys) {
  if ($k -eq 'Hermes skills-backup*') {
    $t = 0; Get-ChildItem $hh -Directory -Filter 'skills-*' | ForEach-Object { $t += SizeGB $_.FullName }
    [pscustomobject]@{ What = $k; GB = [math]::Round($t,2); Path = "$hh\skills-*" }
  } else { [pscustomobject]@{ What = $k; GB = (SizeGB $items[$k]); Path = $items[$k] } }
}
$rows | Sort-Object GB -Descending | Format-Table -AutoSize | Out-String -Width 200
# Recycle Bin (all drives)
$rb = (New-Object -ComObject Shell.Application).Namespace(0xA).Items() | ForEach-Object { $_.ExtendedProperty('Size') } | Measure-Object -Sum
'Recycle Bin: {0} item(s), {1} GB' -f $rb.Count, [math]::Round(($rb.Sum/1GB),2)
if ($Deep) {
  'Top-level folders in profile (GB):'
  Get-ChildItem $H -Force -Directory | ForEach-Object { [pscustomobject]@{ Dir = $_.Name; GB = SizeGB $_.FullName } } |
    Sort-Object GB -Descending | Select-Object -First 15 | Format-Table -AutoSize | Out-String -Width 200
  'AppData\Local top (GB):'
  Get-ChildItem $L -Force -Directory | ForEach-Object { [pscustomobject]@{ Dir = $_.Name; GB = SizeGB $_.FullName } } |
    Sort-Object GB -Descending | Select-Object -First 15 | Format-Table -AutoSize | Out-String -Width 200
}
'Component store (needs admin, optional): Dism.exe /Online /Cleanup-Image /AnalyzeComponentStore'
