param(
    [Parameter(Position = 0)]
    [ValidateSet('build', 'serve')]
    [string]$Action = 'build',
    [switch]$Native
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$entryPoint = Join-Path $scriptDir 'docs.py'
$runnerArgs = @()
if ($Native) {
    $runnerArgs += '--native'
}
$runnerArgs += $Action

$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -ne $python) {
    & $python.Source $entryPoint @runnerArgs
} else {
    $pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($null -eq $pythonLauncher) {
        throw "docs requires Python 3.11+ (or Python 3.10 with tomli)."
    }
    & $pythonLauncher.Source -3 $entryPoint @runnerArgs
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
