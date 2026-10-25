# Build agent\rl-agent.jar (no game classes needed; uses reflection). Needs a JDK: set $env:RL_JDK or use C:\bench\tools\jdk.
$jdk = if ($env:RL_JDK) { $env:RL_JDK } else { 'C:\bench\tools\jdk' }
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root 'agent\build'
New-Item -ItemType Directory -Force -Path $out | Out-Null
& "$jdk\bin\javac.exe" --release 21 -d $out (Join-Path $root 'agent\src\RLAgent.java')
if ($LASTEXITCODE) { throw 'javac failed' }
& "$jdk\bin\jar.exe" cfm (Join-Path $root 'agent\rl-agent.jar') (Join-Path $root 'agent\MANIFEST.MF') -C $out .
if ($LASTEXITCODE) { throw 'jar failed' }
Write-Host "Built agent\rl-agent.jar"
