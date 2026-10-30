# Start the normal rendered game client without Steam, to join the local RL server (127.0.0.1:16261).
# Usage: .\scripts\start-client.ps1 [-Connect 127.0.0.1]
# The client uses its own data folder (.pzclient in the repo, git-ignored) with the repo mods copied in, so the
# server's required mods are present and your normal Zomboid folder is left alone. Settings start fresh there.
param([string]$Connect = '', [switch]$Small, [string]$AgentArgs = '', [double]$TimeScale = 1,
      [string]$User = '', [string]$Pass = '', [string]$Server = '127.0.0.1', [int]$Port = 16261, [int]$Hash = 1)
. "$PSScriptRoot\pz-env.ps1"

$ClientCache = if ($env:PZ_RL_CLIENT_CACHE) { $env:PZ_RL_CLIENT_CACHE } else { Join-Path $RepoRoot '.pzclient' }
New-Item -ItemType Directory -Force -Path (Join-Path $ClientCache 'mods') | Out-Null
Get-ChildItem (Join-Path $RepoRoot 'mods') -Directory | ForEach-Object {
    $t = Join-Path $ClientCache "mods\$($_.Name)"
    if (Test-Path $t) { Remove-Item $t -Recurse -Force }
    Copy-Item $_.FullName $t -Recurse
}

# -Small: tiny window, low frame rate, no sound/voice, written to the client's own options.ini (never your normal one)
if ($Small) {
    $opt = Join-Path $ClientCache 'options.ini'
    if (-not (Test-Path $opt)) {
        @('width=640', 'height=480', 'fullScreen=false', 'borderless=false', 'vsync=false', 'frameRate=30') | Set-Content $opt
    }
}
# -User: log in automatically from the main menu (RLClient mod reads rl_client.txt from the client's own Lua folder)
$luaDir = Join-Path $ClientCache 'Lua'
New-Item -ItemType Directory -Force -Path $luaDir | Out-Null
$cfgFile = Join-Path $luaDir 'rl_client.txt'
if ($User) {
    if (-not $Pass) { $Pass = $User }   # fake-client accounts use their username as the password
    Set-Content -Path $cfgFile -Value "$User|$Pass|$Server|$Port|$Hash" -NoNewline
    $modList = @('VERSION = 1,', '', 'mods', '{', '    mod = RLBridge,', '    mod = RLClient,', '}', '', 'maps', '{', '}')
    Set-Content -Path (Join-Path (Join-Path $ClientCache 'mods') 'default.txt') -Value $modList
} elseif (Test-Path $cfgFile) { Remove-Item $cfgFile }
# the bot's live logic (swing instrumentation, aim override use, tidy) is loaded by the RLBot 'reload' command from this file in the client's Lua folder
if (Test-Path (Join-Path $PSScriptRoot 'rl_bot_dev.lua')) { Copy-Item (Join-Path $PSScriptRoot 'rl_bot_dev.lua') (Join-Path $luaDir 'rl_bot_dev.lua') -Force }
if (-not $AgentArgs -and $User) { $AgentArgs = 'client;autostart;aim' }   # auto-login accounts also click through the loading screen
if ($TimeScale -ne 1 -and $AgentArgs -and $AgentArgs -notmatch 'classes=') { $AgentArgs = "$AgentArgs;classes=zombie/" }   # client clock patch (same as the server's)
if ($env:PZ_AGENT_EXTRA -and $AgentArgs) { $AgentArgs = "$AgentArgs;$($env:PZ_AGENT_EXTRA)" }   # e.g. norender (headless-client spike)
$agentArg = @()
if ($AgentArgs) {
    $jar = if ($env:RL_AGENT_JAR) { $env:RL_AGENT_JAR } else { Join-Path (Join-Path $RepoRoot 'agent') 'rl-agent.jar' }
    $spec = "-javaagent:$jar=$AgentArgs"
    $agentArg = @($spec, "-Drl.timescale=$TimeScale")
}
$args = $agentArg + @(
    '--enable-native-access=ALL-UNNAMED',
    '--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED',
    '-Xmx3072m', '-XX:+UseZGC',
    '-XX:-CreateCoredumpOnCrash', '-XX:-OmitStackTraceInFastThrow',
    '-Dzomboid.steam=0',
    '-Djava.library.path=win64/;.',
    '-cp', $ClassPath, 'zombie.gameStates.MainScreenState',
    '-nosteam', "-cachedir=$ClientCache"
)
if ($Small) { $args += @('-nosound', '-novoip') }
if ($Connect) { $args += @('+connect', $Connect) }

Push-Location $GameDir
try { & $Java @args }
finally { Pop-Location }
