# Start a local, non-Steam Project Zomboid server for RL experiments.
# Usage: .\scripts\start-server.ps1 [-ServerName rl] [-AdminPassword changeme]
param(
    [string]$ServerName = 'rl',
    [string]$AdminPassword = 'rl-admin',
    [string]$MaxHeap = '4096m',
    [string]$JavaAgent = ''
)
. "$PSScriptRoot\pz-env.ps1"

$logDir = Join-Path $RepoRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("server-{0:yyyyMMdd-HHmmss}.log" -f (Get-Date))

$agentArg = if ($JavaAgent) { @("-javaagent:$JavaAgent") } else { @() }
$args = $CommonJvm + $agentArg + @(
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
