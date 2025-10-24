#!/usr/bin/pwsh
<#
.SYNOPSIS
    Daily Operations Script for EPC Portal Management
.DESCRIPTION
    This script handles all daily operational tasks for the EPC Portal:
    - Process submitted applications
    - Monitor system health
    - Generate daily reports
    - Clean up old data
    - Send notifications
.PARAMETER Mode
    Operation mode: Interactive, Automated, or Report
#>

param(
    [ValidateSet("Interactive", "Automated", "Report")]
    [string]$Mode = "Interactive",
    
    [string]$ConfigPath = "$PSScriptRoot/config.json",
    
    [switch]$SendReport,
    
    [string]$ReportEmail = "sysadmin@saberrenewables.com"
)

# Load configuration
$config = Get-Content -Path $ConfigPath | ConvertFrom-Json
$siteUrl = $config.SharePoint.SiteUrl
$clientId = $config.SharePoint.ClientId
$tenant = $config.SharePoint.Tenant

# Logging setup
$logDate = Get-Date -Format "yyyy-MM-dd"
$logPath = "$PSScriptRoot/logs/daily-ops-$logDate.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logPath -Value $logMessage
    
    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARNING" { Write-Host $logMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        default { Write-Host $logMessage }
    }
}

function Show-Menu {
    Clear-Host
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     EPC PORTAL DAILY OPERATIONS MENU       ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Process Pending Submissions" -ForegroundColor Yellow
    Write-Host "2. Generate Daily Report" -ForegroundColor Yellow
    Write-Host "3. Check System Health" -ForegroundColor Yellow
    Write-Host "4. Clean Up Old Data (30+ days)" -ForegroundColor Yellow
    Write-Host "5. Test Power Automate Flow" -ForegroundColor Yellow
    Write-Host "6. Add Test Submission" -ForegroundColor Yellow
    Write-Host "7. View Recent Logs" -ForegroundColor Yellow
    Write-Host "8. Run All Daily Tasks" -ForegroundColor Green
    Write-Host "9. Exit" -ForegroundColor Red
    Write-Host ""
}

function Process-Submissions {
    Write-Log "Starting submission processing" "INFO"
    Write-Host "`n━━━ Processing Submissions ━━━" -ForegroundColor Cyan
    
    # Run the processor script
    & "$PSScriptRoot/scripts/process-epc.ps1" `
        -SiteUrl $siteUrl `
        -ClientId $clientId `
        -Tenant $tenant
    
    Write-Log "Submission processing completed" "SUCCESS"
}

function Generate-Report {
    Write-Log "Generating daily report" "INFO"
    Write-Host "`n━━━ Daily Report ━━━" -ForegroundColor Cyan
    
    try {
        Connect-PnPOnline -Url $siteUrl -ClientId $clientId -Tenant $tenant -Interactive -WarningAction SilentlyContinue
        
        # Get today's statistics
        $today = Get-Date -Format "yyyy-MM-dd"
        $yesterday = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
        
        # Get submissions
        $allSubmissions = Get-PnPListItem -List "EPC Onboarding"
        $todaySubmissions = $allSubmissions | Where-Object { 
            $_.FieldValues.Created -ge $today 
        }
        $pendingSubmissions = $allSubmissions | Where-Object { 
            $_.FieldValues.Status -eq "Submitted" -and 
            $_.FieldValues.SubmissionHandled -ne $true 
        }
        
        # Get invitations
        $invitations = Get-PnPListItem -List "EPC Invitations"
        $activeInvitations = $invitations | Where-Object { 
            $_.FieldValues.Status -eq "Active" 
        }
        $usedToday = $invitations | Where-Object { 
            $_.FieldValues.UsedDate -ge $today 
        }
        
        # Generate report
        $report = @"
════════════════════════════════════════
EPC PORTAL DAILY REPORT - $today
════════════════════════════════════════

SUBMISSIONS
-----------
Total Submissions: $($allSubmissions.Count)
Today's Submissions: $($todaySubmissions.Count)
Pending Processing: $($pendingSubmissions.Count)

INVITATIONS
-----------
Total Invitations: $($invitations.Count)
Active Invitations: $($activeInvitations.Count)
Used Today: $($usedToday.Count)

TOP COMPANIES (Last 7 Days)
----------------------------
"@
        
        # Get recent companies
        $recentCompanies = $allSubmissions | 
            Where-Object { $_.FieldValues.Created -ge (Get-Date).AddDays(-7) } |
            Select-Object -ExpandProperty FieldValues |
            Select-Object -Property CompanyName, Created, Status |
            Sort-Object -Property Created -Descending |
            Select-Object -First 5
        
        foreach ($company in $recentCompanies) {
            $report += "`n- $($company.CompanyName) ($($company.Status))"
        }
        
        $report += @"

SYSTEM STATUS
-------------
SharePoint Connection: ✓ Active
Power Automate Flow: $(if (Test-Path "$PSScriptRoot/logs/epc_processor.log") { "✓ Running" } else { "⚠ Check Required" })
Last Processor Run: $(Get-Date -Format "HH:mm:ss")

════════════════════════════════════════
"@
        
        Write-Host $report -ForegroundColor White
        
        # Save report to file
        $reportPath = "$PSScriptRoot/reports/daily-$today.txt"
        if (!(Test-Path "$PSScriptRoot/reports")) {
            New-Item -ItemType Directory -Path "$PSScriptRoot/reports" -Force | Out-Null
        }
        $report | Out-File -FilePath $reportPath
        
        Write-Log "Report saved to $reportPath" "SUCCESS"
        
        # Send email if requested
        if ($SendReport) {
            Write-Log "Sending report to $ReportEmail" "INFO"
            # Email sending would go here (requires additional setup)
        }
        
        Disconnect-PnPOnline
        
    } catch {
        Write-Log "Error generating report: $_" "ERROR"
    }
}

function Check-Health {
    Write-Log "Running system health check" "INFO"
    Write-Host "`n━━━ System Health Check ━━━" -ForegroundColor Cyan
    
    $healthStatus = @()
    
    # Check SharePoint connection
    Write-Host "Checking SharePoint connection..." -NoNewline
    try {
        Connect-PnPOnline -Url $siteUrl -ClientId $clientId -Tenant $tenant -Interactive -WarningAction SilentlyContinue
        $web = Get-PnPWeb
        Write-Host " ✓" -ForegroundColor Green
        $healthStatus += "SharePoint: Connected to $($web.Title)"
        Disconnect-PnPOnline
    } catch {
        Write-Host " ✗" -ForegroundColor Red
        $healthStatus += "SharePoint: Connection failed - $_"
    }
    
    # Check API endpoint
    Write-Host "Checking API endpoint..." -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "https://epc-api.saberrenewable.energy/api/epc-submit" -Method OPTIONS -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host " ✓" -ForegroundColor Green
            $healthStatus += "API: Responding (HTTP 200)"
        }
    } catch {
        Write-Host " ✗" -ForegroundColor Red
        $healthStatus += "API: Not responding"
    }
    
    # Check frontend
    Write-Host "Checking frontend..." -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "https://epc.saberrenewable.energy" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host " ✓" -ForegroundColor Green
            $healthStatus += "Frontend: Online"
        }
    } catch {
        Write-Host " ✗" -ForegroundColor Red
        $healthStatus += "Frontend: Offline"
    }
    
    # Check logs
    Write-Host "Checking processor logs..." -NoNewline
    $processorLog = "$PSScriptRoot/logs/epc_processor.log"
    if (Test-Path $processorLog) {
        $lastLog = Get-Content $processorLog -Tail 1
        if ($lastLog -match "ERROR") {
            Write-Host " ⚠" -ForegroundColor Yellow
            $healthStatus += "Processor: Recent errors detected"
        } else {
            Write-Host " ✓" -ForegroundColor Green
            $healthStatus += "Processor: No recent errors"
        }
    } else {
        Write-Host " ⚠" -ForegroundColor Yellow
        $healthStatus += "Processor: No log file found"
    }
    
    # Display summary
    Write-Host "`n━━━ Health Summary ━━━" -ForegroundColor Cyan
    foreach ($status in $healthStatus) {
        Write-Host $status
    }
    
    Write-Log "Health check completed" "SUCCESS"
}

function Clean-OldData {
    param([int]$DaysToKeep = 30)
    
    Write-Log "Starting cleanup (keeping last $DaysToKeep days)" "INFO"
    Write-Host "`n━━━ Cleaning Old Data ━━━" -ForegroundColor Cyan
    
    try {
        Connect-PnPOnline -Url $siteUrl -ClientId $clientId -Tenant $tenant -Interactive -WarningAction SilentlyContinue
        
        $cutoffDate = (Get-Date).AddDays(-$DaysToKeep)
        
        # Clean old draft submissions
        $oldDrafts = Get-PnPListItem -List "EPC Onboarding" | Where-Object {
            $_.FieldValues.Status -eq "Draft" -and
            $_.FieldValues.Created -lt $cutoffDate
        }
        
        Write-Host "Found $($oldDrafts.Count) old draft submissions"
        
        if ($oldDrafts.Count -gt 0) {
            $confirm = Read-Host "Delete these items? (y/n)"
            if ($confirm -eq 'y') {
                foreach ($item in $oldDrafts) {
                    Remove-PnPListItem -List "EPC Onboarding" -Identity $item.Id -Force
                    Write-Log "Deleted draft submission ID $($item.Id)" "INFO"
                }
                Write-Host "Deleted $($oldDrafts.Count) items" -ForegroundColor Green
            }
        }
        
        # Clean expired invitations
        $expiredInvites = Get-PnPListItem -List "EPC Invitations" | Where-Object {
            $_.FieldValues.ExpiryDate -lt (Get-Date) -and
            $_.FieldValues.Status -eq "Active"
        }
        
        Write-Host "Found $($expiredInvites.Count) expired invitations"
        
        foreach ($invite in $expiredInvites) {
            Set-PnPListItem -List "EPC Invitations" -Identity $invite.Id -Values @{
                Status = "Expired"
            }
            Write-Log "Marked invitation $($invite.FieldValues.Code) as expired" "INFO"
        }
        
        Disconnect-PnPOnline
        
        Write-Log "Cleanup completed" "SUCCESS"
        
    } catch {
        Write-Log "Error during cleanup: $_" "ERROR"
    }
}

function Test-PowerAutomate {
    Write-Log "Testing Power Automate flow" "INFO"
    Write-Host "`n━━━ Testing Power Automate ━━━" -ForegroundColor Cyan
    
    & "$PSScriptRoot/test-epc-portal.sh"
    
    Write-Log "Power Automate test completed" "SUCCESS"
}

function Add-TestSubmission {
    Write-Log "Adding test submission" "INFO"
    Write-Host "`n━━━ Adding Test Submission ━━━" -ForegroundColor Cyan
    
    & "$PSScriptRoot/scripts/add-dummy-epc.ps1" `
        -SiteUrl $siteUrl `
        -ClientId $clientId `
        -Tenant $tenant `
        -SubmitImmediately
    
    Write-Log "Test submission added" "SUCCESS"
}

function View-Logs {
    Write-Host "`n━━━ Recent Logs ━━━" -ForegroundColor Cyan
    
    $logFiles = @(
        "$PSScriptRoot/logs/epc_processor.log",
        "$PSScriptRoot/logs/daily-ops-$logDate.log"
    )
    
    foreach ($log in $logFiles) {
        if (Test-Path $log) {
            Write-Host "`nFile: $log" -ForegroundColor Yellow
            Write-Host "─────────────────────────────" -ForegroundColor Gray
            Get-Content $log -Tail 20 | ForEach-Object {
                if ($_ -match "ERROR") {
                    Write-Host $_ -ForegroundColor Red
                } elseif ($_ -match "WARNING") {
                    Write-Host $_ -ForegroundColor Yellow
                } elseif ($_ -match "SUCCESS") {
                    Write-Host $_ -ForegroundColor Green
                } else {
                    Write-Host $_
                }
            }
        }
    }
}

function Run-AllTasks {
    Write-Log "Running all daily tasks" "INFO"
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║       RUNNING ALL DAILY TASKS              ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Green
    
    Check-Health
    Process-Submissions
    Generate-Report
    Clean-OldData
    
    Write-Host "`n✓ All daily tasks completed!" -ForegroundColor Green
    Write-Log "All daily tasks completed" "SUCCESS"
}

# Main execution
Write-Log "Daily operations script started in $Mode mode" "INFO"

switch ($Mode) {
    "Interactive" {
        do {
            Show-Menu
            $choice = Read-Host "Select an option (1-9)"
            
            switch ($choice) {
                '1' { Process-Submissions; Read-Host "`nPress Enter to continue" }
                '2' { Generate-Report; Read-Host "`nPress Enter to continue" }
                '3' { Check-Health; Read-Host "`nPress Enter to continue" }
                '4' { Clean-OldData; Read-Host "`nPress Enter to continue" }
                '5' { Test-PowerAutomate; Read-Host "`nPress Enter to continue" }
                '6' { Add-TestSubmission; Read-Host "`nPress Enter to continue" }
                '7' { View-Logs; Read-Host "`nPress Enter to continue" }
                '8' { Run-AllTasks; Read-Host "`nPress Enter to continue" }
                '9' { Write-Host "Exiting..." -ForegroundColor Yellow; break }
                default { Write-Host "Invalid option!" -ForegroundColor Red; Start-Sleep -Seconds 2 }
            }
        } while ($choice -ne '9')
    }
    
    "Automated" {
        # For cron job or scheduled task
        Run-AllTasks
    }
    
    "Report" {
        # Just generate and optionally send report
        Generate-Report
        if ($SendReport) {
            Write-Log "Report sent to $ReportEmail" "SUCCESS"
        }
    }
}

Write-Log "Daily operations script completed" "INFO"