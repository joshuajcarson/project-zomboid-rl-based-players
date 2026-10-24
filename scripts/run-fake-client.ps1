# Run the game's built-in headless test client (zombie.network.FakeClientManager) against the local server.
# Usage: .\scripts\run-fake-client.ps1 -Scenario scenarios\smoke-1.json -Id 1
# Run one process per agent, each with a different -Id that matches a "movements" entry in the scenario.
param(
    [string]$Scenario = 'scenarios\smoke-1.json',
    [int]$Id = 1,
    [int]$LogLevel = 2
)
. "$PSScriptRoot\pz-env.ps1"

$scenarioPath = (Resolve-Path (Join-Path $RepoRoot $Scenario)).Path
$logDir = Join-Path $RepoRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("fakeclient-{0}-{1:yyyyMMdd-HHmmss}.log" -f $Id, (Get-Date))

$args = $CommonJvm + @(
    '-Xmx1024m',
    "-Dzomboid.steam=0",
    '-cp', $ClassPath, 'zombie.network.FakeClientManager',
    "-scenarios=$scenarioPath", "-id=$Id", "-loglevel=$LogLevel"
)

Write-Host "Log: $log"
Push-Location $GameDir
try { & $Java @args 2>&1 | Tee-Object -FilePath $log }
finally { Pop-Location }
