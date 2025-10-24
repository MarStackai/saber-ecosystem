#!/usr/bin/pwsh
<#
.SYNOPSIS
  Verifies an EPC submission exists in SharePoint and (optionally) that the invitation was marked Used.

.DESCRIPTION
  Connects to SharePoint via PnP.PowerShell (Device Login) and searches the
  "EPC Onboarding" list for a submission matching the provided InvitationCode,
  Email, or CompanyName. Optionally checks the "EPC Invitations" list for the
  invitation status.

.EXAMPLE
  ./verify-submission.ps1 -InvitationCode ABCD1234 -Email test@example.com

.EXAMPLE
  ./verify-submission.ps1 -CompanyName "Test EPC Ltd" -VerifyInvitation

.NOTES
  Requires PowerShell 7+ and PnP.PowerShell module:
    Install-Module PnP.PowerShell -Scope CurrentUser

  Uses Device Login (interactive) and does not store secrets.
#>

param(
  [string]$ConfigPath = "$HOME/saber_business_ops/config.json",
  [string]$SiteUrl,
  [string]$ClientId,
  [string]$Tenant,

  [string]$InvitationCode,
  [string]$Email,
  [string]$CompanyName,

  [int]$LookbackDays = 14,
  [switch]$VerifyInvitation,
  [switch]$Json
)

function Read-Config {
  param([string]$Path)
  if (Test-Path $Path) {
    try { return Get-Content $Path -Raw | ConvertFrom-Json } catch { return $null }
  }
  return $null
}

function Get-FieldValue {
  param($Item, [string[]]$Names)
  foreach ($n in $Names) {
    if ($Item.FieldValues.ContainsKey($n) -and $Item.FieldValues[$n]) { return $Item.FieldValues[$n] }
  }
  return $null
}

function Out-Result {
  param($Object)
  if ($Json) { $Object | ConvertTo-Json -Depth 6 }
  else { $Object | Format-Table -AutoSize }
}

# Load config defaults if not provided
$cfg = Read-Config -Path $ConfigPath
if (-not $SiteUrl -and $cfg) { $SiteUrl = $cfg.SharePoint.SiteUrl }
if (-not $ClientId -and $cfg) { $ClientId = $cfg.SharePoint.ClientId }
if (-not $Tenant  -and $cfg) { $Tenant  = $cfg.SharePoint.Tenant }

if (-not $SiteUrl -or -not $ClientId -or -not $Tenant) {
  Write-Error "Missing SiteUrl/ClientId/Tenant. Provide via params or config.json."
  exit 2
}

if (-not ($InvitationCode -or $Email -or $CompanyName)) {
  Write-Error "Provide at least one of: -InvitationCode, -Email, -CompanyName"
  exit 2
}

Write-Host "Connecting to SharePoint: $SiteUrl" -ForegroundColor Cyan
try {
  Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin -WarningAction SilentlyContinue
} catch {
  Write-Error "Failed to connect: $_"
  exit 1
}

try {
  $since = (Get-Date).AddDays(-1 * [Math]::Abs($LookbackDays))
  # Pull recent items and filter client-side to avoid internal name mismatches
  $items = Get-PnPListItem -List "EPC Onboarding" -PageSize 200 -ScriptBlock {
    param($items)
    $items.Context.Load($items.ListItemCollectionPosition)
  }

  $matches = @()
  foreach ($item in $items) {
    $created = $item.FieldValues["Created"]
    if ($created -and ([datetime]$created) -lt $since) { continue }

    $fInvitation = Get-FieldValue $item @('InvitationCode','InviteCode')
    $fEmail      = Get-FieldValue $item @('PrimaryContactEmail','Email')
    $fCompany    = Get-FieldValue $item @('CompanyName','Title')
    $fStatus     = Get-FieldValue $item @('Status')
    $fSubDate    = Get-FieldValue $item @('SubmissionDate','Modified')
    $fFolder     = Get-FieldValue $item @('SubmissionFolder')
    $fHandled    = Get-FieldValue $item @('SubmissionHandled')

    $ok = $true
    if ($InvitationCode) { $ok = $ok -and ($fInvitation -and $fInvitation -eq $InvitationCode) }
    if ($Email)          { $ok = $ok -and ($fEmail -and ($fEmail -ieq $Email)) }
    if ($CompanyName)    { $ok = $ok -and ($fCompany -and ($fCompany -like "*${CompanyName}*")) }
    if (-not $ok) { continue }

    $matches += [pscustomobject]@{
      Id                = $item.Id
      CompanyName       = $fCompany
      Email             = $fEmail
      InvitationCode    = $fInvitation
      Status            = $fStatus
      SubmissionDate    = $fSubDate
      SubmissionFolder  = $fFolder
      SubmissionHandled = $fHandled
    }
  }

  if ($matches.Count -eq 0) {
    Write-Host "No onboarding submissions matched." -ForegroundColor Yellow
  } else {
    Write-Host "Matched submissions:" -ForegroundColor Green
    Out-Result ($matches | Sort-Object SubmissionDate -Descending)
  }

  $inviteStatus = $null
  if ($VerifyInvitation -and $InvitationCode) {
    Write-Host "\nChecking invitation status for code '$InvitationCode'..." -ForegroundColor Cyan
    $invItems = Get-PnPListItem -List "EPC Invitations" -PageSize 200 -ScriptBlock {
      param($items)
      $items.Context.Load($items.ListItemCollectionPosition)
    }

    foreach ($it in $invItems) {
      $code = Get-FieldValue $it @('InviteCode','Title')
      if ($code -ne $InvitationCode) { continue }
      $status    = Get-FieldValue $it @('InviteStatus','Status')
      $usedDate  = Get-FieldValue $it @('UsedDate')
      $expiry    = Get-FieldValue $it @('ExpiryDate')
      $inviteStatus = [pscustomobject]@{
        Id       = $it.Id
        Code     = $code
        Status   = $status
        UsedDate = $usedDate
        Expiry   = $expiry
      }
      break
    }

    if ($inviteStatus) {
      Write-Host "Invitation record:" -ForegroundColor Green
      Out-Result $inviteStatus
    } else {
      Write-Host "Invitation code not found in 'EPC Invitations'." -ForegroundColor Yellow
    }
  }

  # Exit code: 0 if submission matched, else 1
  if ($matches.Count -gt 0) { exit 0 } else { exit 1 }

} catch {
  Write-Error $_
  exit 1
} finally {
  Disconnect-PnPOnline -ErrorAction SilentlyContinue
}

