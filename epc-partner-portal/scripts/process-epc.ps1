#!/usr/bin/pwsh
param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$ClientId,
    
    [Parameter(Mandatory=$true)]
    [string]$Tenant,
    
    [switch]$WhatIf,
    
    [string]$LogPath = "$HOME/saber_business_ops/logs/epc_processor.log"
)

# Ensure log directory exists
$logDir = Split-Path -Path $LogPath -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogPath -Value $logMessage
    
    # Also output to console with color coding
    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARNING" { Write-Host $logMessage -ForegroundColor Yellow }
        "WHATIF" { Write-Host $logMessage -ForegroundColor Cyan }
        default { Write-Host $logMessage }
    }
}

Write-Log "==================== PROCESSOR START ====================" "INFO"
Write-Log "WhatIf mode: $WhatIf" "INFO"

try {
    # Connect to SharePoint
    Write-Log "Connecting to SharePoint: $SiteUrl" "INFO"
    Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $Tenant -DeviceLogin -WarningAction SilentlyContinue
    Write-Log "Successfully connected to SharePoint" "INFO"
    
    # Get items with Status=Submitted and SubmissionHandled != true
    $camlQuery = @"
<View>
    <Query>
        <Where>
            <And>
                <Eq>
                    <FieldRef Name='Status' />
                    <Value Type='Choice'>Submitted</Value>
                </Eq>
                <Or>
                    <IsNull>
                        <FieldRef Name='SubmissionHandled' />
                    </IsNull>
                    <Eq>
                        <FieldRef Name='SubmissionHandled' />
                        <Value Type='Boolean'>0</Value>
                    </Eq>
                </Or>
            </And>
        </Where>
    </Query>
    <ViewFields>
        <FieldRef Name='ID' />
        <FieldRef Name='Title' />
        <FieldRef Name='CompanyName' />
        <FieldRef Name='Status' />
        <FieldRef Name='SubmissionHandled' />
    </ViewFields>
</View>
"@
    
    Write-Log "Querying EPC Onboarding list for submitted items" "INFO"
    $items = Get-PnPListItem -List "EPC Onboarding" -Query $camlQuery
    
    if ($items.Count -eq 0) {
        Write-Log "No items to process (Status=Submitted and not handled)" "INFO"
    } else {
        Write-Log "Found $($items.Count) items to process" "INFO"
        
        foreach ($item in $items) {
            $itemId = $item.Id
            $companyName = $item["CompanyName"]
            
            Write-Log "Processing item ID=$itemId, Company='$companyName'" "INFO"
            
            # Create folder name
            $folderName = "$itemId - $companyName"
            $folderPath = "EPC Submissions/$folderName"
            
            # Check/create folder
            try {
                $folder = Get-PnPFolder -Url $folderPath -ErrorAction SilentlyContinue
                Write-Log "Folder already exists: $folderPath" "INFO"
            } catch {
                if ($WhatIf) {
                    Write-Log "[WHATIF] Would create folder: $folderPath" "WHATIF"
                } else {
                    Write-Log "Creating folder: $folderPath" "INFO"
                    Add-PnPFolder -Name $folderName -Folder "EPC Submissions"
                    Write-Log "Folder created successfully" "INFO"
                }
            }
            
            # Get attachments
            $attachments = Get-PnPProperty -ClientObject $item -Property "AttachmentFiles"
            
            if ($attachments.Count -gt 0) {
                Write-Log "Found $($attachments.Count) attachments for item $itemId" "INFO"
                
                foreach ($attachment in $attachments) {
                    $fileName = $attachment.FileName
                    $serverRelativeUrl = $attachment.ServerRelativeUrl
                    
                    Write-Log "Processing attachment: $fileName" "INFO"
                    
                    if ($WhatIf) {
                        Write-Log "[WHATIF] Would download attachment from: $serverRelativeUrl" "WHATIF"
                        Write-Log "[WHATIF] Would upload to: $folderPath/$fileName" "WHATIF"
                        Write-Log "[WHATIF] Would remove original attachment: $fileName" "WHATIF"
                    } else {
                        try {
                            # Download attachment
                            $fileBytes = Get-PnPFile -Url $serverRelativeUrl -AsMemoryStream
                            $memoryStream = New-Object System.IO.MemoryStream
                            $fileBytes.CopyTo($memoryStream)
                            $fileContent = $memoryStream.ToArray()
                            $memoryStream.Dispose()
                            $fileBytes.Dispose()
                            
                            Write-Log "Downloaded ${fileName} ($($fileContent.Length) bytes)" "INFO"
                            
                            # Upload to library
                            Add-PnPFile -FileName $fileName -Folder $folderPath -Content $fileContent
                            Write-Log "Uploaded $fileName to $folderPath" "INFO"
                            
                            # Remove from list item
                            Remove-PnPListItemAttachment -List "EPC Onboarding" -Identity $itemId -FileName $fileName -Force
                            Write-Log "Removed attachment $fileName from list item" "INFO"
                            
                        } catch {
                            Write-Log "Error processing attachment ${fileName}: $_" "ERROR"
                        }
                    }
                }
            } else {
                Write-Log "No attachments found for item $itemId" "INFO"
            }
            
            # Update list item
            $folderUrl = "$SiteUrl/EPC Submissions/$folderName"
            
            if ($WhatIf) {
                Write-Log "[WHATIF] Would update item $itemId with:" "WHATIF"
                Write-Log "[WHATIF]   SubmissionFolder = $folderUrl" "WHATIF"
                Write-Log "[WHATIF]   SubmissionHandled = true" "WHATIF"
            } else {
                try {
                    Set-PnPListItem -List "EPC Onboarding" -Identity $itemId -Values @{
                        SubmissionFolder = $folderUrl
                        SubmissionHandled = $true
                    }
                    Write-Log "Updated item $itemId with folder URL and handled flag" "INFO"
                } catch {
                    Write-Log "Error updating item ${itemId}: $_" "ERROR"
                }
            }
            
            Write-Log "Completed processing item $itemId" "INFO"
        }
    }
    
} catch {
    Write-Log "Critical error: $_" "ERROR"
    exit 1
} finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
    Write-Log "Disconnected from SharePoint" "INFO"
    Write-Log "==================== PROCESSOR END ====================" "INFO"
}