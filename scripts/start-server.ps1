# Start a local, non-Steam Project Zomboid server for RL experiments.
# Usage: .\scripts\start-server.ps1 [-ServerName rl] [-AdminPassword changeme]
param(
    [string]$ServerName = 'rl',
    [string]$AdminPassword = 'rl-admin',
    [string]$MaxHeap = '4096m',
    [string]$JavaAgent = '',
    [double]$TimeScale = 1,
    [int]$ChannelPort = 0,
    [switch]$Dev
)
. "$PSScriptRoot\pz-env.ps1"

$logDir = Join-Path $RepoRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("server-{0:yyyyMMdd-HHmmss}.log" -f (Get-Date))

# -TimeScale K speeds up the server's own clock (all zombie.* classes) via the agent; needs -JavaAgent.
# -ChannelPort opens the localhost observation/command channel used by the Python env (needs -JavaAgent).
$agentParts = @()
if ($ChannelPort -gt 0) { $agentParts += "channel=$ChannelPort" }
if ($TimeScale -ne 1) { $agentParts += 'classes=zombie/' }
$agentOpt = if ($agentParts.Count) { '=' + ($agentParts -join ';') } else { '' }
$agentArg = if ($JavaAgent) { @("-javaagent:$JavaAgent$agentOpt", "-Drl.timescale=$TimeScale") } else { @() }
# -Dev enables the 'get' and 'lua' bridge commands (arbitrary reflection / Lua from the localhost channel); research use only.
$devArg = if ($Dev) { @('-Drl.dev=true') } else { @() }
$args = $CommonJvm + $agentArg + $devArg + @(
    "-Xmx$MaxHeap", '-XX:+UseZGC',
    '-cp', $ClassPath, 'zombie.network.GameServer',
    '-nosteam',
    "-cachedir=$CacheDir",
    "-servername", $ServerName,
    "-adminpassword", $AdminPassword
)

Write-Host "Server data: $CacheDir"
Write-Host "Log: $log"
Push-Location $GameDir
try { & $Java @args 2>&1 | Tee-Object -FilePath $log }
finally { Pop-Location }
