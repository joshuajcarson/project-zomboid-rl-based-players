# Start the normal rendered game client without Steam, to join the local RL server (127.0.0.1:16261).
# Usage: .\scripts\start-client.ps1 [-Connect 127.0.0.1]
# The client uses its own data folder (.pzclient in the repo, git-ignored) with the repo mods copied in, so the
# server's required mods are present and your normal Zomboid folder is left alone. Settings start fresh there.
param([string]$Connect = '')
. "$PSScriptRoot\pz-env.ps1"

$ClientCache = if ($env:PZ_RL_CLIENT_CACHE) { $env:PZ_RL_CLIENT_CACHE } else { Join-Path $RepoRoot '.pzclient' }
New-Item -ItemType Directory -Force -Path (Join-Path $ClientCache 'mods') | Out-Null
Get-ChildItem (Join-Path $RepoRoot 'mods') -Directory | ForEach-Object {
    $t = Join-Path $ClientCache "mods\$($_.Name)"
    if (Test-Path $t) { Remove-Item $t -Recurse -Force }
    Copy-Item $_.FullName $t -Recurse
}

$args = @(
    '--enable-native-access=ALL-UNNAMED',
    '--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED',
    '-Xmx3072m', '-XX:+UseZGC',
    '-XX:-CreateCoredumpOnCrash', '-XX:-OmitStackTraceInFastThrow',
    '-Dzomboid.steam=0',
    '-Djava.library.path=win64/;.',
    '-cp', $ClassPath, 'zombie.gameStates.MainScreenState',
    '-nosteam', "-cachedir=$ClientCache"
)
if ($Connect) { $args += @('+connect', $Connect) }

Push-Location $GameDir
try { & $Java @args }
finally { Pop-Location }
