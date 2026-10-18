param([ValidateSet('dev','build','install')][string]$Task = 'dev')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$candidates = @()
$installed = Get-Command node -ErrorAction SilentlyContinue
if ($installed) { $candidates += $installed.Source }
$candidates += Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
$runtime = $null
foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
        $version = [version]((& $candidate --version).TrimStart('v'))
        if (($version.Major -eq 20 -and $version -ge [version]'20.19.0') -or $version -ge [version]'22.12.0') {
            $runtime = $candidate
            break
        }
    }
}
if (-not $runtime) { throw 'Install Node 22.12 or newer, or Node 20.19. The current Vite build cannot run on Node 16.' }
$previousPath = $env:PATH
Push-Location (Join-Path $projectRoot 'frontend')
try {
    $env:PATH = (Split-Path $runtime -Parent) + [IO.Path]::PathSeparator + $previousPath
    Write-Host ("Using Node " + (& $runtime --version))
    if ($Task -eq 'install') {
        & npm.cmd ci
    } elseif ($Task -eq 'build') {
        & $runtime 'node_modules/vite/bin/vite.js' build
    } else {
        & $runtime 'node_modules/vite/bin/vite.js' --host 127.0.0.1
    }
    if ($LASTEXITCODE -ne 0) { throw "Frontend $Task failed with exit code $LASTEXITCODE" }
} finally {
    $env:PATH = $previousPath
    Pop-Location
}
