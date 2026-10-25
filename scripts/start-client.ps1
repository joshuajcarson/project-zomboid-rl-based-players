# Start the normal rendered game client without Steam, to join the local RL server (127.0.0.1:16261).
# Usage: .\scripts\start-client.ps1
. "$PSScriptRoot\pz-env.ps1"

$args = @(
    '--enable-native-access=ALL-UNNAMED',
    '--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED',
    '-Xmx3072m', '-XX:+UseZGC',
    '-XX:-CreateCoredumpOnCrash', '-XX:-OmitStackTraceInFastThrow',
    '-Dzomboid.steam=0',
    '-Djava.library.path=win64/;.',
    '-cp', $ClassPath, 'zombie.gameStates.MainScreenState',
    '-nosteam'
)

Push-Location $GameDir
try { & $Java @args }
finally { Pop-Location }
