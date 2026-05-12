# vk-ads-oauth-setup.ps1 - Native PowerShell wizard for VK Ads (ads.vk.com) setup.
# Runs in a separate PowerShell window opened by vk-ads-launch-wizard.ps1.
# AI assistant must NOT call this script directly via Bash tool - it would
# capture stdin prompts where user types VK_ADS_CLIENT_SECRET.

[CmdletBinding()]
param([switch]$Force)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$SecretsDir = Join-Path $env:USERPROFILE '.claude\secrets\vk-ads\clients'
$EnvFile    = Join-Path $SecretsDir 'self.env'
$VkBase     = if ($env:VK_ADS_BASE) { $env:VK_ADS_BASE } else { 'https://ads.vk.com' }
$TokenUrl   = "$VkBase/api/v2/oauth2/token.json"

function Write-Step($msg) { Write-Host ""; Write-Host "[>] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "[+] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[!] $msg" -ForegroundColor Yellow }
function Die($msg)        { Write-Host "[x] $msg" -ForegroundColor Red; Read-Host "Enter чтобы закрыть"; exit 1 }

New-Item -ItemType Directory -Path $SecretsDir -Force | Out-Null

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  VK Ads (ads.vk.com) - настройка (PowerShell, без Git Bash)" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

# ----- Step 1: read or ask credentials -----
$useExisting = $false
if ((Test-Path $EnvFile) -and -not $Force) {
    $content = Get-Content $EnvFile -Raw
    if ($content -match 'VK_ADS_CLIENT_ID=..' -and $content -match 'VK_ADS_CLIENT_SECRET=..') {
        Write-Ok "Найден заполненный $EnvFile"
        $ans = Read-Host 'Использовать существующие client_id/client_secret? [Y/n]'
        if ($ans -match '^[Yy]?$') { $useExisting = $true }
    }
}

if ($useExisting) {
    $envHash = @{}
    foreach ($line in (Get-Content $EnvFile)) {
        if ($line -match '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
            $envHash[$Matches[1]] = $Matches[2]
        }
    }
    $clientId     = $envHash['VK_ADS_CLIENT_ID']
    $clientSecret = $envHash['VK_ADS_CLIENT_SECRET']
    $clientName   = if ($envHash['VK_ADS_CLIENT_NAME']) { $envHash['VK_ADS_CLIENT_NAME'] } else { 'self' }
} else {
    Write-Host "Где взять значения:" -ForegroundColor Yellow
    Write-Host "  ads.vk.com -> Профиль -> Доступ к API -> Запросить доступ к API"
    Write-Host "  (после одобрения VK сгенерирует client_id и client_secret)"
    Write-Host ""

    $clientId = Read-Host 'client_id'
    if (-not $clientId) { Die "client_id пустой" }

    $secretSecure = Read-Host 'client_secret (вводится скрыто)' -AsSecureString
    $clientSecret = [System.Net.NetworkCredential]::new('', $secretSecure).Password
    if (-not $clientSecret) { Die "client_secret пустой" }

    $clientName = Read-Host 'Имя кабинета (любое, например agency-msk)'
    if (-not $clientName) { $clientName = 'self' }

    $now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $envContent = @"
# VK Ads (ads.vk.com) credentials
# Сгенерировано $now
VK_ADS_CLIENT_ID=$clientId
VK_ADS_CLIENT_SECRET=$clientSecret
VK_ADS_CLIENT_NAME=$clientName
VK_ADS_ISSUED_AT=$now
"@
    [System.IO.File]::WriteAllText($EnvFile, $envContent, (New-Object System.Text.UTF8Encoding($false)))

    try {
        $acl = New-Object System.Security.AccessControl.FileSecurity
        $acl.SetAccessRuleProtection($true, $false)
        $me = "$env:USERDOMAIN\$env:USERNAME"
        $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule($me, 'FullControl', 'Allow')))
        $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule('NT AUTHORITY\SYSTEM', 'FullControl', 'Allow')))
        Set-Acl -Path $EnvFile -AclObject $acl
    } catch {}
    Write-Ok "Сохранил в $EnvFile (доступ ограничен)"
}

# ----- Step 2: get tokens via client_credentials -----
Write-Step "Получаю access/refresh-токены через client_credentials..."

try {
    $body = @{
        grant_type    = 'client_credentials'
        client_id     = $clientId
        client_secret = $clientSecret
    }
    $resp = Invoke-RestMethod -Uri $TokenUrl `
                              -Method Post `
                              -ContentType 'application/x-www-form-urlencoded' `
                              -Body $body `
                              -TimeoutSec 30
} catch {
    $code = $null
    if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
    Write-Warn "HTTP $code : $($_.Exception.Message)"
    Die "Не удалось получить токены. Проверь client_id/client_secret в $EnvFile и перезапусти мастер."
}

if (-not $resp.access_token) {
    Die "В ответе нет access_token: $($resp | ConvertTo-Json)"
}

$expiresIn = if ($resp.expires_in) { [int]$resp.expires_in } else { 86400 }
$expIso    = (Get-Date).ToUniversalTime().AddSeconds($expiresIn - 300).ToString("yyyy-MM-ddTHH:mm:ssZ")
$tokenType = if ($resp.token_type) { $resp.token_type } else { 'Bearer' }
$scopes    = if ($resp.scope) { $resp.scope } else { '' }
$refresh   = if ($resp.refresh_token) { $resp.refresh_token } else { '' }

# Re-read .env, update token fields, rewrite
$updates = @{
    'VK_ADS_ACCESS_TOKEN'  = $resp.access_token
    'VK_ADS_REFRESH_TOKEN' = $refresh
    'VK_ADS_TOKEN_TYPE'    = $tokenType
    'VK_ADS_TOKEN_EXPIRES' = $expIso
    'VK_ADS_SCOPES'        = $scopes
}
$lines = @()
$seen  = @{}
foreach ($raw in (Get-Content $EnvFile)) {
    $s = $raw.Trim()
    if (-not $s -or $s.StartsWith('#') -or -not $s.Contains('=')) { $lines += $raw; continue }
    $k = $s.Split('=', 2)[0].Trim()
    if ($updates.ContainsKey($k)) {
        $lines += "$k=$($updates[$k])"
        $seen[$k] = $true
    } else {
        $lines += $raw
    }
}
foreach ($k in $updates.Keys) {
    if (-not $seen.ContainsKey($k)) { $lines += "$k=$($updates[$k])" }
}
[System.IO.File]::WriteAllText($EnvFile, ($lines -join "`n") + "`n", (New-Object System.Text.UTF8Encoding($false)))

try {
    $acl = New-Object System.Security.AccessControl.FileSecurity
    $acl.SetAccessRuleProtection($true, $false)
    $me = "$env:USERDOMAIN\$env:USERNAME"
    $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule($me, 'FullControl', 'Allow')))
    $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule('NT AUTHORITY\SYSTEM', 'FullControl', 'Allow')))
    Set-Acl -Path $EnvFile -AclObject $acl
} catch {}

Write-Ok "Токены сохранены (access живёт ${expiresIn}s, обновится автоматически)"

# ----- Step 3: sanity check -----
Write-Step "Проверяю кабинет..."

$headers = @{ Authorization = "Bearer $($resp.access_token)"; Accept = 'application/json' }
try {
    $userInfo = Invoke-RestMethod -Uri "$VkBase/api/v2/user.json" -Headers $headers -TimeoutSec 20
    $plans    = Invoke-RestMethod -Uri "$VkBase/api/v2/ad_plans.json?limit=200&fields=id,status" -Headers $headers -TimeoutSec 20
} catch {
    Write-Warn "Sanity-check упал: $($_.Exception.Message)"
    Write-Warn "Конфиг сохранён, попробуй позже через cli.py"
    Read-Host "Enter чтобы закрыть"
    exit 0
}

$userName   = if ($userInfo.username) { $userInfo.username } elseif ($userInfo.first_name) { $userInfo.first_name } else { '?' }
$userId     = if ($userInfo.id) { $userInfo.id } else { '?' }
$userType   = if ($userInfo.type) { $userInfo.type } else { '?' }
$userStatus = if ($userInfo.status) { $userInfo.status } else { '?' }
$plansTotal = if ($plans.count) { $plans.count } else { 0 }
$plansActive = 0
if ($plans.items) {
    $plansActive = ($plans.items | Where-Object { $_.status -eq 'active' }).Count
}

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Green
Write-Host "  + VK Ads настроен и работает" -ForegroundColor Green
Write-Host "===============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Кабинет:        $userName  (id=$userId, type=$userType, status=$userStatus)"
Write-Host "  Кампаний всего: $plansTotal"
Write-Host "  Активных:       $plansActive"
Write-Host ""
Write-Host "  Конфиг + токены: $EnvFile"
Write-Host ""
Write-Host "Дальше в чате с Клодом можно спрашивать:"
Write-Host "  - 'Заполни отчёт по моему VK-кабинету за месяц'"
Write-Host "  - 'Покажи активные кампании и остатки бюджета'"
Write-Host "  - 'Сравни CPM по группам объявлений'"
Write-Host "  - 'Сколько лидов получили за последние 30 дней'"
Write-Host ""
Read-Host 'Готово. Нажми Enter чтобы закрыть это окно'
