# Copy repo mods into the server's mod folder (.pzdata\mods) and enable them in the server ini.
# Usage: .\scripts\install-mods.ps1 [-Enable RLProbe] [-ServerName rl]
param([string[]]$Enable = @(), [string]$ServerName = 'rl')
. "$PSScriptRoot\pz-env.ps1"
$src = Join-Path $RepoRoot 'mods'
$dst = Join-Path $CacheDir 'mods'
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Get-ChildItem $src -Directory | ForEach-Object {
    $t = Join-Path $dst $_.Name
    if (Test-Path $t) { Remove-Item $t -Recurse -Force }
    Copy-Item $_.FullName $t -Recurse
}
$ini = Join-Path $CacheDir "Server\$ServerName.ini"
if (Test-Path $ini) {
    $mods = $Enable -join ';'
    (Get-Content $ini) -replace '^Mods=.*', "Mods=$mods" | Set-Content $ini
    Write-Host "Mods=$mods in $ini"
}
