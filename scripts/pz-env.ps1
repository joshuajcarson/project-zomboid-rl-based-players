# Shared paths for the launch scripts. Override with environment variables if your install differs.
$RepoRoot = Split-Path -Parent $PSScriptRoot
$GameDir  = if ($env:PZ_GAME_DIR) { $env:PZ_GAME_DIR } else { 'C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid' }
$Java     = Join-Path $GameDir 'jre64\bin\java.exe'
# Server saves/configs live inside the repo (git-ignored) so they never touch the normal Zomboid folder.
$CacheDir = if ($env:PZ_RL_CACHE) { $env:PZ_RL_CACHE } else { Join-Path $RepoRoot '.pzdata' }
$CommonJvm = @(
    '--enable-native-access=ALL-UNNAMED',
    '--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED',
    '-XX:-CreateCoredumpOnCrash',
    '-XX:-OmitStackTraceInFastThrow',
    '-Djava.awt.headless=true',
    '-Djava.library.path=./natives/;./natives/win64/;./'
)
$ClassPath = './;projectzomboid.jar'

if (-not (Test-Path $Java)) { throw "Java not found at $Java. Set PZ_GAME_DIR." }
New-Item -ItemType Directory -Force -Path $CacheDir | Out-Null
