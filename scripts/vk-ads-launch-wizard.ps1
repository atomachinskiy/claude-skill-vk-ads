# vk-ads-launch-wizard.ps1 - Spawn separate PowerShell window running
# vk-ads-oauth-setup.ps1. Used on Windows so VK_ADS_CLIENT_SECRET never
# enters the AI assistant's transcript.
#
# AI calls this script via Bash tool:
#   powershell -ExecutionPolicy Bypass -File vk-ads-launch-wizard.ps1
#
# A new PowerShell window opens. User enters client_id / client_secret there.
# AI never sees them.

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Setup     = Join-Path $ScriptDir 'vk-ads-oauth-setup.ps1'

if (-not (Test-Path $Setup)) {
    Write-Host "[x] Не найден $Setup" -ForegroundColor Red
    exit 1
}

$psExe = (Get-Command powershell.exe -ErrorAction SilentlyContinue).Source
if (-not $psExe) { $psExe = 'powershell.exe' }

Start-Process -FilePath $psExe `
              -ArgumentList @(
                  '-NoExit',
                  '-ExecutionPolicy', 'Bypass',
                  '-File', "`"$Setup`""
              )

Write-Host "[+] Открыл отдельное окно PowerShell с мастером VK Ads." -ForegroundColor Green
Write-Host "    Перейди в новое окно и следуй инструкциям там."
Write-Host "    VK_ADS_CLIENT_ID / VK_ADS_CLIENT_SECRET вводятся в новом окне, в этот чат они не попадут."
