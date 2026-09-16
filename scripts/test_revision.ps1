[CmdletBinding()]
param(
    [ValidateSet('Quick', 'Full')]
    [string]$Mode = 'Quick',
    [string]$ResultsDir = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$StartedUtc = (Get-Date).ToUniversalTime()
$RunId = $StartedUtc.ToString('yyyyMMdd-HHmmss')
if ([string]::IsNullOrWhiteSpace($ResultsDir)) {
    $ResultsDir = Join-Path $RepoRoot ("build/revision-test-results/{0}-{1}" -f $RunId, $Mode.ToLowerInvariant())
}
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

$StepResults = [System.Collections.Generic.List[object]]::new()
$FailedStep = $null

function Invoke-RevisionStep {
    param([string]$Name, [string]$FilePath, [string[]]$Arguments)

    $logPath = Join-Path $ResultsDir ((($Name -replace '[^A-Za-z0-9_.-]', '_')) + '.log')
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $global:LASTEXITCODE = 0
    $exitCode = 0
    $previousErrorActionPreference = $ErrorActionPreference
    Push-Location $RepoRoot
    try {
        # Windows PowerShell 5.1 wraps native stderr as NativeCommandError.
        # Native tools such as CMake may write warnings to stderr while still
        # returning exit code 0, so judge native steps by LASTEXITCODE instead.
        $ErrorActionPreference = 'Continue'
        & $FilePath @Arguments *> $logPath
        if ($null -ne $LASTEXITCODE) { $exitCode = [int]$LASTEXITCODE }
    }
    catch {
        ($_ | Out-String) | Add-Content -Path $logPath
        $exitCode = 1
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
        Pop-Location
        $timer.Stop()
    }

    $StepResults.Add([pscustomobject]@{
        name = $Name
        result = $(if ($exitCode -eq 0) { 'PASS' } else { 'FAIL' })
        exit_code = $exitCode
        duration_ms = $timer.ElapsedMilliseconds
        log = $logPath
    })
    return ($exitCode -eq 0)
}

$BuildDir = Join-Path $RepoRoot ("build/revision-{0}" -f $Mode.ToLowerInvariant())
$Steps = @(
    @{ Name='release-tooling'; File='python'; Args=@('scripts/test_release_v2.py') },
    @{ Name='release-tooling-optimized'; File='python'; Args=@('-O','scripts/test_release_v2.py') },
    @{ Name='boundaries'; File='python'; Args=@('tools/check_boundaries.py') },
    @{ Name='cmake-configure'; File='cmake'; Args=@('-S','cpp','-B',$BuildDir,'-DMONAKA_BUILD_TESTS=ON','-DCMAKE_BUILD_TYPE=Release') },
    @{ Name='cmake-build'; File='cmake'; Args=@('--build',$BuildDir,'--config','Release') },
    @{ Name='ctest'; File='ctest'; Args=@('--test-dir',$BuildDir,'-C','Release','--output-on-failure') },
    @{ Name='jvm-build'; File='gradle'; Args=@('-p','jvm','--no-daemon','build') },
    @{ Name='wire-v2'; File='python'; Args=@('tools/test_v2.py') }
)

if ($Mode -eq 'Full') {
    $Steps += @(
        @{ Name='wire-v1'; File='python'; Args=@('tools/test.py') },
        @{ Name='package-v1'; File='python'; Args=@('tools/package.py','--wire-major','1') },
        @{ Name='verify-v1'; File='python'; Args=@('tools/verify_kit.py','--wire-major','1') },
        @{ Name='package-v2'; File='python'; Args=@('tools/package.py','--wire-major','2') },
        @{ Name='verify-v2'; File='python'; Args=@('tools/verify_kit.py','--wire-major','2') }
    )
}

foreach ($step in $Steps) {
    if (-not (Invoke-RevisionStep -Name $step.Name -FilePath $step.File -Arguments $step.Args)) {
        $FailedStep = $step.Name
        break
    }
}

$head = ''
try { $head = ((& git -C $RepoRoot rev-parse HEAD 2>$null) | Out-String).Trim() } catch { }
$result = if ($null -eq $FailedStep) { 'PASS' } else { 'FAIL' }
$summary = [ordered]@{
    repo = 'MonakaVR/MonakaProtocol'
    head = $head
    mode = $Mode
    result = $result
    failed_step = $FailedStep
    started_utc = $StartedUtc.ToString('o')
    ended_utc = (Get-Date).ToUniversalTime().ToString('o')
    hardware_validation = 'NOT RUN'
    steps = $StepResults
}
$summaryPath = Join-Path $ResultsDir 'summary.json'
$summary | ConvertTo-Json -Depth 6 | Set-Content -Path $summaryPath -Encoding UTF8
Write-Host ("RESULT={0} repo=MonakaProtocol mode={1} failed_step={2} summary={3}" -f $result, $Mode, $FailedStep, $summaryPath)
if ($result -eq 'FAIL') { exit 1 }
