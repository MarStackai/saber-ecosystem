param(
  [Parameter(Mandatory=$true)]
  [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
)

# --- Connect ---
Connect-PnPOnline -Url $SiteUrl -Interactive

Write-Host "=== Simplified EPC Partner Portal SharePoint Schema ===" -ForegroundColor Green
Write-Host "Purpose: Streamlined workflow for EPC partner onboarding communications" -ForegroundColor Yellow
Write-Host ""

# Helper: add or update a field safely
function Ensure-Field {
  param(
    [string]$DisplayName,
    [string]$InternalName,
    [ValidateSet("Text","Note","Number","Boolean","DateTime","User","URL","Choice")]
    [string]$Type,
    [string]$ListTitle,
    [switch]$AddToDefaultView,
    [hashtable]$Attributes,
    [string[]]$Choices
  )
  $existing = Get-PnPField -List $ListTitle -Identity $InternalName -ErrorAction SilentlyContinue
  if (-not $existing) {
    $params = @{
      List = $ListTitle
      DisplayName = $DisplayName
      InternalName = $InternalName
      Type = $Type
      Group = "EPC Partner Portal"
    }
    
    if ($Type -eq "Note") { 
      $params += @{ AddToDefaultView = $AddToDefaultView.IsPresent }
    }
    elseif ($Type -eq "Choice" -and $Choices) {
      $params += @{ Choices = $Choices }
    }
    elseif ($Attributes) { 
      $params += @{ AdditionalAttributes = $Attributes } 
    }
    
    if ($AddToDefaultView) { $params += @{ AddToDefaultView = $true } }
    
    Add-PnPField @params | Out-Null
    Write-Host "  ✓ Added field: $DisplayName" -ForegroundColor Green
  } else {
    Write-Host "  → Field exists: $DisplayName" -ForegroundColor Gray
    if ($Attributes) { Set-PnPField -List $ListTitle -Identity $InternalName -Values $Attributes | Out-Null }
  }
  
  if ($AddToDefaultView) {
    try { Add-PnPViewField -List $ListTitle -View "All Items" -Field $InternalName -ErrorAction SilentlyContinue | Out-Null } catch {}
  }
}

# =============================================================================
# 1. EPC INVITATIONS LIST (existing - just ensure it has required fields)
# =============================================================================
Write-Host ""
Write-Host "1. ENSURING EPC INVITATIONS LIST..." -ForegroundColor Cyan
Write-Host "   Purpose: Manages invitation codes and tracks partner engagement"

$invitationsListTitle = "EPC Invitations"
$inviteList = Get-PnPList -Identity $invitationsListTitle -ErrorAction SilentlyContinue
if (-not $inviteList) {
  Write-Host "   Creating EPC Invitations list..." -ForegroundColor Yellow
  $inviteList = New-PnPList -Title $invitationsListTitle -Template GenericList -OnQuickLaunch -EnableVersioning
} else {
  Write-Host "   EPC Invitations list exists" -ForegroundColor Gray
}

# Core invitation fields
Ensure-Field "Company Name" "CompanyName" Text $invitationsListTitle -AddToDefaultView
Ensure-Field "Contact Email" "ContactEmail" Text $invitationsListTitle -AddToDefaultView
Ensure-Field "Contact Name" "ContactName" Text $invitationsListTitle 
Ensure-Field "Invitation Code" "InvitationCode" Text $invitationsListTitle -AddToDefaultView
Ensure-Field "Code Expiry Date" "CodeExpiryDate" DateTime $invitationsListTitle -AddToDefaultView
Ensure-Field "Invitation Status" "InvitationStatus" Choice $invitationsListTitle -AddToDefaultView -Choices @("Sent","Opened","In Progress","Completed","Expired")
Ensure-Field "Application Submitted" "ApplicationSubmitted" Boolean $invitationsListTitle -AddToDefaultView
Ensure-Field "Submission Date" "SubmissionDate" DateTime $invitationsListTitle
Ensure-Field "Notes" "InvitationNotes" Note $invitationsListTitle

Write-Host "   ✓ EPC Invitations list configured" -ForegroundColor Green

# =============================================================================
# 2. EPC OPERATIONS HANDOFF LIST (new - for operations review)
# =============================================================================
Write-Host ""
Write-Host "2. CREATING EPC OPERATIONS HANDOFF LIST..." -ForegroundColor Cyan
Write-Host "   Purpose: Basic company info for operations review with link to full application data"

$handoffListTitle = "EPC Operations Handoff"
$handoffList = Get-PnPList -Identity $handoffListTitle -ErrorAction SilentlyContinue
if (-not $handoffList) {
  Write-Host "   Creating EPC Operations Handoff list..." -ForegroundColor Yellow
  $handoffList = New-PnPList -Title $handoffListTitle -Template GenericList -OnQuickLaunch -EnableVersioning
} else {
  Write-Host "   EPC Operations Handoff list exists" -ForegroundColor Gray
}

# Basic company information for operations review
Ensure-Field "Company Name" "CompanyName" Text $handoffListTitle -AddToDefaultView
Ensure-Field "Primary Contact Name" "PrimaryContactName" Text $handoffListTitle -AddToDefaultView  
Ensure-Field "Primary Contact Email" "PrimaryContactEmail" Text $handoffListTitle -AddToDefaultView
Ensure-Field "Primary Contact Phone" "PrimaryContactPhone" Text $handoffListTitle -AddToDefaultView
Ensure-Field "Invitation Code" "InvitationCode" Text $handoffListTitle -AddToDefaultView
Ensure-Field "Application Submission Date" "ApplicationSubmissionDate" DateTime $handoffListTitle -AddToDefaultView

# Link to full application data in our system
Ensure-Field "Portal Application Link" "PortalApplicationLink" URL $handoffListTitle -AddToDefaultView
Ensure-Field "Application Reference" "ApplicationReference" Text $handoffListTitle -AddToDefaultView

# Operations workflow fields  
Ensure-Field "Review Status" "ReviewStatus" Choice $handoffListTitle -AddToDefaultView -Choices @("Pending Review","Under Review","Additional Info Required","Approved","Rejected")
Ensure-Field "Assigned Reviewer" "AssignedReviewer" User $handoffListTitle -AddToDefaultView
Ensure-Field "Review Priority" "ReviewPriority" Choice $handoffListTitle -Choices @("Low","Normal","High","Urgent")
Ensure-Field "Review Due Date" "ReviewDueDate" DateTime $handoffListTitle
Ensure-Field "Review Notes" "ReviewNotes" Note $handoffListTitle
Ensure-Field "Operations Notes" "OperationsNotes" Note $handoffListTitle
Ensure-Field "Partner Feedback Notes" "PartnerFeedbackNotes" Note $handoffListTitle

# Approval workflow
Ensure-Field "Approval Decision" "ApprovalDecision" Choice $handoffListTitle -Choices @("Pending","Approved","Rejected","On Hold")
Ensure-Field "Approval Date" "ApprovalDate" DateTime $handoffListTitle
Ensure-Field "Approved By" "ApprovedBy" User $handoffListTitle
Ensure-Field "Partner Notified Date" "PartnerNotifiedDate" DateTime $handoffListTitle
Ensure-Field "Final Status" "FinalStatus" Choice $handoffListTitle -AddToDefaultView -Choices @("Active","Approved","Rejected","Withdrawn","On Hold")

Write-Host "   ✓ EPC Operations Handoff list configured" -ForegroundColor Green

# =============================================================================
# 3. CREATE CUSTOM VIEWS
# =============================================================================
Write-Host ""
Write-Host "3. CREATING CUSTOM VIEWS..." -ForegroundColor Cyan

# Invitations Views
$inviteViews = Get-PnPView -List $invitationsListTitle
if (-not ($inviteViews | Where-Object {$_.Title -eq "Active Invitations"})) {
  Add-PnPView -List $invitationsListTitle -Title "Active Invitations" -Fields "ID","CompanyName","ContactEmail","InvitationCode","InvitationStatus","ApplicationSubmitted","Modified" -Query '<Where><And><Neq><FieldRef Name="InvitationStatus"/><Value Type="Choice">Expired</Value></Neq><Neq><FieldRef Name="InvitationStatus"/><Value Type="Choice">Completed</Value></Neq></And></Where>' -RowLimit 50 | Out-Null
  Write-Host "   ✓ Created 'Active Invitations' view" -ForegroundColor Green
}

if (-not ($inviteViews | Where-Object {$_.Title -eq "Completed Applications"})) {
  Add-PnPView -List $invitationsListTitle -Title "Completed Applications" -Fields "ID","CompanyName","ContactEmail","InvitationCode","SubmissionDate","Modified" -Query '<Where><Eq><FieldRef Name="ApplicationSubmitted"/><Value Type="Boolean">1</Value></Eq></Where>' -RowLimit 50 | Out-Null
  Write-Host "   ✓ Created 'Completed Applications' view" -ForegroundColor Green
}

# Operations Handoff Views
$handoffViews = Get-PnPView -List $handoffListTitle
if (-not ($handoffViews | Where-Object {$_.Title -eq "Pending Review"})) {
  Add-PnPView -List $handoffListTitle -Title "Pending Review" -Fields "ID","CompanyName","PrimaryContactName","PrimaryContactEmail","ApplicationSubmissionDate","ReviewPriority","ReviewDueDate" -Query '<Where><Eq><FieldRef Name="ReviewStatus"/><Value Type="Choice">Pending Review</Value></Eq></Where>' -RowLimit 50 | Out-Null
  Write-Host "   ✓ Created 'Pending Review' view" -ForegroundColor Green
}

if (-not ($handoffViews | Where-Object {$_.Title -eq "Under Review"})) {
  Add-PnPView -List $handoffListTitle -Title "Under Review" -Fields "ID","CompanyName","AssignedReviewer","ReviewDueDate","ReviewNotes","Modified" -Query '<Where><Eq><FieldRef Name="ReviewStatus"/><Value Type="Choice">Under Review</Value></Eq></Where>' -RowLimit 50 | Out-Null
  Write-Host "   ✓ Created 'Under Review' view" -ForegroundColor Green
}

if (-not ($handoffViews | Where-Object {$_.Title -eq "Approved Partners"})) {
  Add-PnPView -List $handoffListTitle -Title "Approved Partners" -Fields "ID","CompanyName","PrimaryContactName","PrimaryContactEmail","ApprovalDate","ApprovedBy","FinalStatus" -Query '<Where><Eq><FieldRef Name="ApprovalDecision"/><Value Type="Choice">Approved</Value></Eq></Where>' -RowLimit 50 | Out-Null
  Write-Host "   ✓ Created 'Approved Partners' view" -ForegroundColor Green
}

# =============================================================================
# 4. SET PERMISSIONS AND INDEXING
# =============================================================================
Write-Host ""
Write-Host "4. CONFIGURING PERMISSIONS AND INDEXING..." -ForegroundColor Cyan

# Index key fields for performance
try {
  Set-PnPField -List $invitationsListTitle -Identity "InvitationCode" -Values @{ Indexed = $true } | Out-Null
  Set-PnPField -List $invitationsListTitle -Identity "InvitationStatus" -Values @{ Indexed = $true } | Out-Null
  Set-PnPField -List $handoffListTitle -Identity "ReviewStatus" -Values @{ Indexed = $true } | Out-Null
  Set-PnPField -List $handoffListTitle -Identity "FinalStatus" -Values @{ Indexed = $true } | Out-Null
  Write-Host "   ✓ Indexed key fields for performance" -ForegroundColor Green
} catch {
  Write-Host "   ⚠ Could not set field indexing (may require permissions)" -ForegroundColor Yellow
}

# =============================================================================
# 5. SUMMARY
# =============================================================================
Write-Host ""
Write-Host "=== CONFIGURATION COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "WORKFLOW SUMMARY:" -ForegroundColor White
Write-Host "1. Power Automate creates invitation in 'EPC Invitations' list with 8-char code"
Write-Host "2. Partner uses code at /apply → completes React form → submits application"  
Write-Host "3. Application creates item in 'EPC Operations Handoff' with basic info + portal link"
Write-Host "4. Operations team reviews via SharePoint, updates status, adds notes"
Write-Host "5. Approval triggers email notifications to partner and operations"
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor White
Write-Host "- Update epc-application API endpoint to create handoff items"
Write-Host "- Configure Power Automate flows for email notifications"
Write-Host "- Set up operations review dashboard permissions"
Write-Host ""
Write-Host "Portal Integration Ready! ✨" -ForegroundColor Green