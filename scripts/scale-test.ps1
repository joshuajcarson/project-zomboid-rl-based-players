# Ramp up fake clients against the running server and report server CPU, observer tick rate and kill rate at each level.
# Needs the server running with the RLBridge mod (mods\RLBridge). Usage: .\scripts\scale-test.ps1 -Counts 1,4,8,16
param([int[]]$Counts = @(1, 4, 8, 16), [string]$Scenario = 'scenarios\scale-16.json', [int]$SettleSeconds = 45)
. "$PSScriptRoot\pz-env.ps1"

function Get-Server { Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object { $_.CommandLine -match 'GameServer' } | Select-Object -First 1 }
function Get-Fakes { @(Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object { $_.CommandLine -match 'FakeClientManager' }) }
$sid = (Get-Server).ProcessId
if (-not $sid) { throw 'Server is not running' }

Get-Fakes | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep 5
$started = 0
foreach ($n in $Counts) {
    while ($started -lt $n) {
        $started++
        Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile', '-File', (Join-Path $PSScriptRoot 'run-fake-client.ps1'), '-Scenario', $Scenario, '-Id', "$started", '-LogLevel', '1' | Out-Null
        Start-Sleep 3
    }
    Start-Sleep $SettleSeconds
    $s = Get-Process -Id $sid; $a = $s.TotalProcessorTime.TotalSeconds; $t0 = Get-Date
    Start-Sleep 20
    $s.Refresh(); $cpu = ($s.TotalProcessorTime.TotalSeconds - $a) / ((Get-Date) - $t0).TotalSeconds * 100
    $fakes = Get-Fakes
    $fakeRam = ($fakes | ForEach-Object { (Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue).WorkingSet64 } | Measure-Object -Sum).Sum / 1MB
    $stats = python (Join-Path $PSScriptRoot 'analyze_obs.py') --scale
    "{0,3} clients (alive {1,3}) | server CPU {2,5:N0}% of a core, RAM {3:N0} MB | fake clients RAM {4:N0} MB total | {5}" -f $n, $fakes.Count, $cpu, ($s.WorkingSet64 / 1MB), $fakeRam, $stats
}
