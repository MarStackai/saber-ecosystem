#!/usr/bin/pwsh
# Simplified SharePoint Schema Deployment

Write-Host "=== EPC Portal Schema Deployment ===" -ForegroundColor Cyan

# Connect to SharePoint
Connect-PnPOnline -Url 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners' -ClientId 'bbbfe394-7cff-4ac9-9e01-33cbf116b930' -Tenant 'saberrenewables.onmicrosoft.com' -DeviceLogin

Write-Host "✅ Connected to SharePoint" -ForegroundColor Green

# Check if list exists
$listTitle = "EPC Onboarding"
$list = Get-PnPList -Identity $listTitle -ErrorAction SilentlyContinue

if (-not $list) {
    Write-Host "Creating list '$listTitle'..." -ForegroundColor Yellow
    $list = New-PnPList -Title $listTitle -Template GenericList -OnQuickLaunch -Url "Lists/EPC%20Onboarding"
    Write-Host "✅ List created" -ForegroundColor Green
} else {
    Write-Host "✅ List '$listTitle' already exists" -ForegroundColor Yellow
}

# Add key fields for extended form
Write-Host "Adding extended form fields..." -ForegroundColor Yellow

# Helper function to add fields safely
function Add-SafeField {
    param($DisplayName, $InternalName, $Type)
    
    $existing = Get-PnPField -List $listTitle -Identity $InternalName -ErrorAction SilentlyContinue
    if (-not $existing) {
        try {
            Add-PnPField -List $listTitle -DisplayName $DisplayName -InternalName $InternalName -Type $Type -Group "EPC Extended"
            Write-Host "✅ Added: $DisplayName" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Failed to add $DisplayName : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "⏭️  Exists: $DisplayName" -ForegroundColor Gray
    }
}

# Add core extended fields
Add-SafeField "Company Name" "CompanyName" "Text"
Add-SafeField "Trading Name" "TradingName" "Text" 
Add-SafeField "Registered Office" "RegisteredOffice" "Note"
Add-SafeField "Head Office" "HeadOffice" "Note"
Add-SafeField "Company Reg No" "CompanyRegNo" "Text"
Add-SafeField "VAT Number" "VATNumber" "Text"
Add-SafeField "Parent Company" "ParentCompany" "Text"
Add-SafeField "Years Trading" "YearsTrading" "Number"

Add-SafeField "Primary Contact Name" "PrimaryContactName" "Text"
Add-SafeField "Primary Contact Title" "PrimaryContactTitle" "Text"
Add-SafeField "Primary Contact Phone" "PrimaryContactPhone" "Text"
Add-SafeField "Primary Contact Email" "PrimaryContactEmail" "Text"

Add-SafeField "Specialisations" "Specialisations" "Note"
Add-SafeField "Software Used" "SoftwareUsed" "Note"
Add-SafeField "Projects Per Month" "ProjectsPerMonth" "Number"

Add-SafeField "Acts as Principal Contractor" "ActsAsPrincipalContractor" "Boolean"
Add-SafeField "PC Last Year Scale" "PrincipalContractor_LastYearScale" "Note"
Add-SafeField "Acts as Principal Designer" "ActsAsPrincipalDesigner" "Boolean"
Add-SafeField "PD Last Year Scale" "PrincipalDesigner_LastYearScale" "Note"

Add-SafeField "Internal Staff %" "LabourMix_InternalPct" "Number"
Add-SafeField "Subcontract %" "LabourMix_SubcontractPct" "Number"

Add-SafeField "NICEIC CPS" "NICEIC_CPS" "Boolean"
Add-SafeField "MCS Approved" "MCS_Approved" "Boolean"

Add-SafeField "Public Liability Present" "PublicProductLiability_Present" "Boolean"
Add-SafeField "PPL Indemnity Clause" "PublicProductLiability_IndemnityInPrinciple" "Boolean"
Add-SafeField "Employers Liability Present" "EmployersLiability_Present" "Boolean"
Add-SafeField "Professional Indemnity Present" "ProfIndemnity_Present" "Boolean"

Add-SafeField "PPL Expiry" "PublicProductLiability_Expiry" "DateTime"
Add-SafeField "EL Expiry" "EmployersLiability_Expiry" "DateTime"
Add-SafeField "PI Expiry" "ProfIndemnity_Expiry" "DateTime"

Add-SafeField "HSE Notices Last 5Y" "HSE_ImprovementOrProhibition_Last5Y" "Text"
Add-SafeField "RIDDOR Count" "RIDDOR_Incidents_Last3Y_Count" "Number"
Add-SafeField "RIDDOR Details" "RIDDOR_Incidents_Last3Y_Details" "Note"

Add-SafeField "HS CDM Evidence" "HSE_CDM_Management_Evidence" "Note"
Add-SafeField "Named Principal Designer" "Named_PrincipalDesigner" "Text"
Add-SafeField "PD Qualifications" "PD_Qualifications" "Note"
Add-SafeField "Training Records" "TrainingRecords_Summary" "Note"
Add-SafeField "Near Miss Procedure" "NearMiss_Procedure" "Text"
Add-SafeField "Quality Evidence" "Quality_Procedure_Evidence" "Note"

Add-SafeField "HS Policy Date" "Policy_HS_DateSigned" "DateTime"
Add-SafeField "Env Policy Date" "Policy_Env_DateSigned" "DateTime"
Add-SafeField "Modern Slavery Policy Date" "Policy_MS_DateSigned" "DateTime"
Add-SafeField "Misuse Substances Date" "Policy_MOS_DateSigned" "DateTime"
Add-SafeField "Right to Work Method" "RightToWork_Monitoring_Method" "Note"
Add-SafeField "GDPR Policy Date" "GDPRPolicy_DateSigned" "DateTime"
Add-SafeField "Cyber Incident Last 3Y" "CyberIncident_Last3Y" "Text"

Add-SafeField "Resources Per Project" "Resources_PerProject" "Note"
Add-SafeField "Nationwide Coverage" "Coverage_Nationwide" "Boolean"
Add-SafeField "Client Reference" "Client_Reference" "Note"

Add-SafeField "Pending Prosecutions" "PendingProsecutions_Details" "Note"
Add-SafeField "Contracts Reviewed" "Contracts_ReviewedBySignatory" "Boolean"
Add-SafeField "Legal Clarifications" "Legal_Clarifications" "Note"

Add-SafeField "Received Contract Pack" "Received_ContractOverviewPack" "Boolean"
Add-SafeField "Agree to Saber Terms" "Willing_To_WorkToSaberTerms" "Boolean"
Add-SafeField "Agree to Codes" "AgreeToCodes" "Boolean"
Add-SafeField "Data Processing Consent" "DataProcessingConsent" "Boolean"
Add-SafeField "Marketing Consent" "MarketingConsent" "Boolean"
Add-SafeField "Additional Info" "AdditionalInfo" "Note"

# System fields
Add-SafeField "Submission Status" "SubmissionStatus" "Text"
Add-SafeField "Reference Number" "ReferenceNumber" "Text"

Write-Host "`n=== Deployment Summary ===" -ForegroundColor Cyan
$allFields = Get-PnPField -List $listTitle | Where-Object { $_.Group -eq "EPC Extended" -or $_.InternalName -in @("CompanyName","ReferenceNumber","SubmissionStatus") }
Write-Host "Extended fields created: $($allFields.Count)" -ForegroundColor Green

Write-Host "`n✅ Schema deployment complete!" -ForegroundColor Green
Write-Host "Next: Update Cloudflare Worker with new field mappings" -ForegroundColor Yellow