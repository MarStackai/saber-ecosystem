#!/usr/bin/pwsh
# Compare what fields SHOULD exist vs what ACTUALLY exists in SharePoint

Write-Host "=== Comparing Schema Script vs Deployed Fields ===" -ForegroundColor Cyan

# Fields that SHOULD exist according to deploy-schema-simple.ps1
$expectedFields = @(
    "CompanyName", "TradingName", "RegisteredOffice", "HeadOffice", 
    "CompanyRegNo", "VATNumber", "ParentCompany", "YearsTrading",
    "PrimaryContactName", "PrimaryContactTitle", "PrimaryContactPhone", "PrimaryContactEmail",
    "Specialisations", "SoftwareUsed", "ProjectsPerMonth",
    "ActsAsPrincipalContractor", "PrincipalContractor_LastYearScale", 
    "ActsAsPrincipalDesigner", "PrincipalDesigner_LastYearScale",
    "LabourMix_InternalPct", "LabourMix_SubcontractPct",
    "NICEIC_CPS", "MCS_Approved",
    "PublicProductLiability_Present", "PublicProductLiability_IndemnityInPrinciple",
    "EmployersLiability_Present", "ProfIndemnity_Present",
    "PublicProductLiability_Expiry", "EmployersLiability_Expiry", "ProfIndemnity_Expiry",
    "HSE_ImprovementOrProhibition_Last5Y", "RIDDOR_Incidents_Last3Y_Count", "RIDDOR_Incidents_Last3Y_Details",
    "HSE_CDM_Management_Evidence", "Named_PrincipalDesigner", "PD_Qualifications",
    "TrainingRecords_Summary", "NearMiss_Procedure", "Quality_Procedure_Evidence",
    "Policy_HS_DateSigned", "Policy_Env_DateSigned", "Policy_MS_DateSigned", "Policy_MOS_DateSigned",
    "RightToWork_Monitoring_Method", "GDPRPolicy_DateSigned", "CyberIncident_Last3Y",
    "Resources_PerProject", "Coverage_Nationwide", "Client_Reference",
    "PendingProsecutions_Details", "Contracts_ReviewedBySignatory", "Legal_Clarifications",
    "Received_ContractOverviewPack", "Willing_To_WorkToSaberTerms", 
    "AgreeToCodes", "DataProcessingConsent", "MarketingConsent", "AdditionalInfo",
    "SubmissionStatus", "ReferenceNumber"
)

# Fields that ACTUALLY exist (from our previous check)
$actualFields = @(
    "AdditionalInfo", "AgreeToCodes", "Client_Reference", "CompanyName", 
    "Contracts_ReviewedBySignatory", "Coverage_Nationwide", "CyberIncident_Last3Y", 
    "DataProcessingConsent", "EmployersLiability_Expiry", "EmployersLiability_Present", 
    "GDPRPolicy_DateSigned", "HeadOffice", "HSE_CDM_Management_Evidence", 
    "HSE_ImprovementOrProhibition_Las", "HSE_ImprovementOrProhibition_Las0", 
    "LabourMix_InternalPct", "LabourMix_SubcontractPct", "Legal_Clarifications", 
    "MarketingConsent", "MCS_Approved", "Named_PrincipalDesigner", "NearMiss_Procedure", 
    "NICEIC_CPS", "ParentCompany", "PD_Qualifications", "PendingProsecutions_Details", 
    "Policy_Env_DateSigned", "Policy_HS_DateSigned", "Policy_MOS_DateSigned", 
    "Policy_MS_DateSigned", "PrimaryContactTitle", "PrincipalContractor_LastYearScal", 
    "PrincipalContractor_LastYearScal0", "PrincipalDesigner_LastYearScale", 
    "ProfIndemnity_Expiry", "ProfIndemnity_Present", "ProjectsPerMonth", 
    "PublicProductLiability_Expiry", "PublicProductLiability_Indemnity", 
    "PublicProductLiability_Indemnity0", "PublicProductLiability_Present", 
    "Quality_Procedure_Evidence", "Received_ContractOverviewPack", "ReferenceNumber", 
    "Resources_PerProject", "RIDDOR_Incidents_Last3Y_Count", "RIDDOR_Incidents_Last3Y_Details", 
    "RightToWork_Monitoring_Method", "SoftwareUsed", "Specialisations", "SubmissionStatus", 
    "TrainingRecords_Summary", "VATNumber", "Willing_To_WorkToSaberTerms"
)

Write-Host "`nExpected fields: $($expectedFields.Count)" -ForegroundColor Yellow
Write-Host "Actual fields: $($actualFields.Count)" -ForegroundColor Yellow

# Find missing fields
$missingFields = $expectedFields | Where-Object { $_ -notin $actualFields -and "$($_)0" -notin $actualFields -and $_.Replace("_LastYearScale", "_LastYearScal") -notin $actualFields -and $_.Replace("_Last5Y", "_Las") -notin $actualFields -and $_.Replace("_IndemnityInPrinciple", "_Indemnity") -notin $actualFields }

Write-Host "`n=== MISSING FIELDS ===" -ForegroundColor Red
if ($missingFields.Count -eq 0) {
    Write-Host "✅ No missing fields! All expected fields exist (some with truncated names)" -ForegroundColor Green
} else {
    foreach ($field in $missingFields) {
        Write-Host "❌ Missing: $field" -ForegroundColor Red
    }
}

# Find extra fields (that exist but weren't expected)
$extraFields = $actualFields | Where-Object { $_ -notin $expectedFields -and $_.Replace("0", "") -notin $expectedFields -and $_.Replace("_LastYearScal", "_LastYearScale") -notin $expectedFields -and $_.Replace("_Las", "_Last5Y") -notin $expectedFields -and $_.Replace("_Indemnity", "_IndemnityInPrinciple") -notin $expectedFields }

Write-Host "`n=== EXTRA/TRUNCATED FIELDS ===" -ForegroundColor Yellow
foreach ($field in $extraFields) {
    Write-Host "➕ Extra: $field" -ForegroundColor Yellow
}

# Key missing fields for form functionality
$criticalMissing = @(
    "RegisteredOffice", "CompanyRegNo", "TradingName", 
    "PrimaryContactName", "PrimaryContactPhone", "PrimaryContactEmail",
    "ActsAsPrincipalContractor", "ActsAsPrincipalDesigner"
)

$actualCriticalMissing = $criticalMissing | Where-Object { $_ -notin $actualFields }

Write-Host "`n=== CRITICAL MISSING FIELDS FOR FORM ===" -ForegroundColor Red
if ($actualCriticalMissing.Count -eq 0) {
    Write-Host "✅ All critical form fields exist!" -ForegroundColor Green
} else {
    foreach ($field in $actualCriticalMissing) {
        Write-Host "🚨 CRITICAL: $field" -ForegroundColor Red
    }
}

Write-Host "`n=== RECOMMENDATION ===" -ForegroundColor Cyan
if ($actualCriticalMissing.Count -gt 0) {
    Write-Host "Run deploy-schema-simple.ps1 again to create missing critical fields" -ForegroundColor Yellow
} else {
    Write-Host "Schema is complete! Use the corrected flow definition with exact field names" -ForegroundColor Green
}