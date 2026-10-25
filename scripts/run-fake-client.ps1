# Run the game's built-in headless test client (zombie.network.FakeClientManager) against the local server.
# Usage: .\scripts\run-fake-client.ps1 -Scenario scenarios\smoke-1.json -Id 1
# Run one process per agent, each with a different -Id that matches a "movements" entry in the scenario.
param(
    [string]$Scenario = 'scenarios\smoke-1.json',
    [int]$Id = 1,
    [int]$LogLevel = 2,
    [double]$TimeScale = 1,
    [int]$ControlPort = 0
)
. "$PSScriptRoot\pz-env.ps1"

$scenarioPath = (Resolve-Path (Join-Path $RepoRoot $Scenario)).Path
$logDir = Join-Path $RepoRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("fakeclient-{0}-{1:yyyyMMdd-HHmmss}.log" -f $Id, (Get-Date))

# The agent is only attached when needed: a scaled clock (-TimeScale) and/or the localhost control socket (-ControlPort).
$timeArgs = @()
if ($TimeScale -ne 1 -or $ControlPort -gt 0) {
    $agentJar = Join-Path $RepoRoot 'agent\rl-agent.jar'
    $parts = @('client')
    if ($ControlPort -gt 0) { $parts += "control=$ControlPort" }
    if ($TimeScale -ne 1) { $parts += 'classes=zombie/network/FakeClientManager,zombie/core/utils/UpdateLimit' }
    $agentSpec = "-javaagent:$agentJar=" + ($parts -join ';')
    $timeArgs = @($agentSpec, "-Drl.timescale=$TimeScale")
}
$args = $CommonJvm + $timeArgs + @(
    '-Xmx1024m',
    "-Dzomboid.steam=0",
    '-cp', $ClassPath, 'zombie.network.FakeClientManager',
    "-scenarios=$scenarioPath", "-id=$Id", "-loglevel=$LogLevel"
)

Write-Host "Log: $log"
Push-Location $GameDir
try { & $Java @args 2>&1 | Tee-Object -FilePath $log }
finally { Pop-Location }
