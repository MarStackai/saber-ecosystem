param(
  [Parameter(Mandatory=$true)][string]$SiteUrl,
  [Parameter(Mandatory=$true)][string]$ClientId,
  [Parameter(Mandatory=$true)][string]$Tenant
)

Import-Module PnP.PowerShell -Force
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin

Write-Host "Connected to site:" (Get-PnPWeb).Title -ForegroundColor Cyan

$items = Get-PnPListItem -List "EPC Onboarding" -PageSize 10 `
  -Fields "ID","CompanyName","Status","SubmissionFolder","SubmissionHandled","PrimaryContactEmail"

if (-not $items) {
  Write-Host "No items found in 'EPC Onboarding' yet." -ForegroundColor Yellow
} else {
  $items | ForEach-Object {
    [pscustomobject]@{
      ID                  = $_["ID"]
      CompanyName         = $_["CompanyName"]
      Status              = $_["Status"]
      SubmissionFolder    = $_["SubmissionFolder"]
      SubmissionHandled   = $_["SubmissionHandled"]
      PrimaryContactEmail = $_["PrimaryContactEmail"]
    }
  } | Format-Table -Auto
}

Disconnect-PnPOnline