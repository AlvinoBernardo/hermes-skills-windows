param([switch]$DryRun, [string[]]$Only)
$ErrorActionPreference = "Stop"
$src  = Join-Path $PSScriptRoot "skills"
$home_ = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:LOCALAPPDATA "hermes" }
$dest = Join-Path $home_ "skills"
$bak  = Join-Path $home_ ("skills-replaced-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Force $dest | Out-Null }
$skills = Get-ChildItem $src -Recurse -Filter SKILL.md | ForEach-Object { $_.Directory }
$n = 0
foreach ($d in $skills) {
  if ($Only -and ($Only -notcontains $d.Name)) { continue }
  $rel = $d.FullName.Substring($src.Length).TrimStart('\','/')
  # an existing skill with the same name anywhere in the skills dir gets moved aside
  $existing = Get-ChildItem $dest -Recurse -Filter SKILL.md -ErrorAction SilentlyContinue |
              Where-Object { $_.Directory.Name -eq $d.Name } | ForEach-Object { $_.Directory.FullName }
  $target = Join-Path $dest $rel
  if ($DryRun) { Write-Host "[dry-run] $rel"; if ($existing) { Write-Host "          would replace: $existing" }; $n++; continue }
  foreach ($e in $existing) {
    $b = Join-Path $bak ($e.Substring($dest.Length).TrimStart('\','/'))
    New-Item -ItemType Directory -Force (Split-Path $b) | Out-Null
    Move-Item $e $b
    Write-Host "  backed up old $($d.Name) -> $b"
  }
  New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
  Copy-Item $d.FullName $target -Recurse -Force
  Write-Host "+ $rel"; $n++
}
Write-Host "`n$n skill(s) $(if ($DryRun) {'would be '})installed to $dest. Restart Hermes to load them."
