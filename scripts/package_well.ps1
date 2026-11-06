param([switch]$SkipBuild, [string]$NsisCompiler = 'E:\guge\nsis\nsis-3.10\makensis.exe', [string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    $version = [regex]::Match((Get-Content Cargo.toml -Raw), '(?m)^version = "([^"]+)"').Groups[1].Value
    Write-Host "Version: $version"
    
    if (-not $SkipBuild) {
        Write-Host "Building release binary wellshijian.exe..."
        $ErrorActionPreference = 'Continue'
        cargo build --release --bin wellshijian
        $exitCode = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        if ($exitCode -ne 0) { throw 'Release build failed' }
    }
    
    $Executable = Join-Path $projectRoot 'target\release\wellshijian.exe'
    if (-not (Test-Path -LiteralPath $Executable)) {
        # Check target/x86_64-pc-windows-msvc/release/wellshijian.exe if target was specified
        $Executable = Join-Path $projectRoot 'target\x86_64-pc-windows-msvc\release\wellshijian.exe'
    }
    if (-not (Test-Path -LiteralPath $Executable)) { throw "Cannot find $Executable" }
    
    $binary = Get-Item -LiteralPath $Executable
    Write-Host "Found binary: $($binary.FullName) ($($binary.Length) bytes)"
    
    if (-not (Test-Path -LiteralPath $NsisCompiler)) {
        $nsisDir = Join-Path $projectRoot 'target\nsis'
        $cachedNsis = Join-Path $nsisDir 'nsis-3.13\makensis.exe'
        if (Test-Path -LiteralPath $cachedNsis) {
            $NsisCompiler = $cachedNsis
        } else {
            New-Item -ItemType Directory -Path $nsisDir -Force | Out-Null
            $NsisCompiler = & (Join-Path $PSScriptRoot 'get-nsis.ps1') -Directory $nsisDir
        }
    }
    if (-not (Test-Path -LiteralPath $NsisCompiler)) { throw "NSIS compiler not found at $NsisCompiler" }
    
    if (-not $OutputDirectory) { $OutputDirectory = Join-Path $projectRoot 'dist' }
    $outputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
    if (-not (Test-Path -LiteralPath $outputDirectory)) {
        New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
    }
    
    # 1. Package Portable ZIP
    $stagingDirectory = Join-Path $outputDirectory "wellshijian-portable"
    if (Test-Path -LiteralPath $stagingDirectory) { Remove-Item -LiteralPath $stagingDirectory -Recurse -Force }
    New-Item -ItemType Directory -Path $stagingDirectory -Force | Out-Null
    Copy-Item -LiteralPath $binary.FullName -Destination (Join-Path $stagingDirectory 'wellshijian.exe')
    @('LICENSE','THIRD_PARTY_NOTICES.txt') | ForEach-Object {
        if (Test-Path -LiteralPath (Join-Path $projectRoot $_)) {
            Copy-Item -LiteralPath (Join-Path $projectRoot $_) -Destination $stagingDirectory -Recurse
        }
    }
    $portableZip = Join-Path $outputDirectory "wellshijian-portable.zip"
    if (Test-Path -LiteralPath $portableZip) { Remove-Item -LiteralPath $portableZip -Force }
    Compress-Archive -Path "$stagingDirectory\*" -DestinationPath $portableZip
    Write-Host "Created portable zip: $portableZip"
    
    # 2. Package Setup Installer
    $setup = Join-Path $outputDirectory "wellshijian-Setup.exe"
    if (Test-Path -LiteralPath $setup) { Remove-Item -LiteralPath $setup -Force }
    Write-Host "Compiling installer with NSIS..."
    $ErrorActionPreference = 'Continue'
    & $NsisCompiler /INPUTCHARSET UTF8 /V2 /WX "/DAPP_VERSION=$version" "/DPROJECT_DIR=$projectRoot" "/DSOURCE_EXE=$($binary.FullName)" "/DOUTPUT_FILE=$setup" (Join-Path $projectRoot 'installer\setup.nsi')
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($exitCode -ne 0) { throw 'Installer build failed' }
    Write-Host "Created installer: $setup"
    
    # 3. Checksums
    @($setup, $portableZip) | ForEach-Object {
        $checksum = (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()
        "$checksum  $([IO.Path]::GetFileName($_))"
    } | Set-Content -LiteralPath (Join-Path $outputDirectory 'SHA256SUMS.txt') -Encoding ascii
    
    Write-Host "SUCCESS!"
    Write-Host "Installer: $setup"
    Write-Host "Portable ZIP: $portableZip"
} finally {
    Pop-Location
}
