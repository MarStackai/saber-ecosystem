param(
  [Parameter(Mandatory=$true)]
  [string]$SiteUrl = "https://saberrenewables.sharepoint.com/sites/SaberEPCPartners"
)

# --- Connect ---
Connect-PnPOnline -Url $SiteUrl -Interactive

# --- Ensure List exists ---
$epcListTitle = "EPC Onboarding"
$list = Get-PnPList -Identity $epcListTitle -ErrorAction SilentlyContinue
if (-not $list) {
  Write-Host "Creating list '$epcListTitle'..."
  $list = New-PnPList -Title $epcListTitle -Template GenericList -OnQuickLaunch -Url "Lists/EPC%20Onboarding" -EnableVersioning
} else {
  Write-Host "List '$epcListTitle' exists. Proceeding with field provisioning..."
}

# Helper: add or update a field safely
function Ensure-ChoiceField {
  param(
    [string]$DisplayName,
    [string]$InternalName,
    [string[]]$Choices,
    [switch]$Multi,
    [switch]$AddToDefaultView
  )
  $existing = Get-PnPField -List $epcListTitle -Identity $InternalName -ErrorAction SilentlyContinue
  if (-not $existing) {
    $xml = "<Field Type='Choice' DisplayName='$DisplayName' StaticName='$InternalName' Name='$InternalName' "
    if ($Multi) { $xml = "<Field Type='MultiChoice' DisplayName='$DisplayName' StaticName='$InternalName' Name='$InternalName' " }
    $xml += "Group='EPC Onboarding'>"
    foreach ($c in $Choices) { $xml += "<CHOICE>$c</CHOICE>" }
    $xml += ($Multi ? "</MCHOICES></Field>" : "</CHOICES></Field>")
    if ($Multi) { $xml = $xml.Replace("</CHOICE>", "</CHOICE>").Replace("<CHOICE>", "<CHOICE>") ; $xml = $xml.Replace("</Field>", "") ; $xml = $xml.Replace("</CHOICES>", "</CHOICES>") }
    # fix MultiChoice XML
    if ($Multi) { $xml = "<Field Type='MultiChoice' DisplayName='$DisplayName' StaticName='$InternalName' Name='$InternalName' Group='EPC Onboarding'><MCHOICES>" + ($Choices | ForEach-Object { "<CHOICE>$_</CHOICE>" } | Out-String).Trim() + "</MCHOICES></Field>" }
    Add-PnPFieldFromXml -List $epcListTitle -FieldXml $xml | Out-Null
    if ($AddToDefaultView) { Add-PnPViewField -List $epcListTitle -View "All Items" -Field $InternalName }
  } else {
    # Update choices if needed
    Set-PnPField -List $epcListTitle -Identity $InternalName -Values @{ Choices = $Choices } | Out-Null
  }
}

function Ensure-Field {
  param(
    [string]$DisplayName,
    [string]$InternalName,
    [ValidateSet("Text","Note","Number","Boolean","DateTime","User","URL")]
    [string]$Type,
    [switch]$AddToDefaultView,
    [hashtable]$Attributes
  )
  $existing = Get-PnPField -List $epcListTitle -Identity $InternalName -ErrorAction SilentlyContinue
  if (-not $existing) {
    $params = @{
      List = $epcListTitle
      DisplayName = $DisplayName
      InternalName = $InternalName
      Type = $Type
      Group = "EPC Onboarding"
    }
    if ($Type -eq "Note") { $params += @{ AddToDefaultView = $AddToDefaultView.IsPresent ; AdditionalAttributes = @{ "NumLines"="6"; "AppendOnly"="FALSE" } } }
    elseif ($Attributes) { $params += @{ AdditionalAttributes = $Attributes } }
    if ($AddToDefaultView) { $params += @{ AddToDefaultView = $true } }
    Add-PnPField @params | Out-Null
  } else {
    if ($Attributes) { Set-PnPField -List $epcListTitle -Identity $InternalName -Values $Attributes | Out-Null }
  }
  if ($AddToDefaultView) {
    try { Add-PnPViewField -List $epcListTitle -View "All Items" -Field $InternalName -ErrorAction SilentlyContinue | Out-Null } catch {}
  }
}

Write-Host "Provisioning fields..."

# --- Section 1: Company ---
Ensure-Field "Registered company name"           "CompanyName"              Text     -AddToDefaultView
Ensure-Field "Trading name (if different)"       "TradingName"              Text
Ensure-Field "Registered office address"         "RegisteredOffice"         Note
Ensure-Field "Head office address"               "HeadOffice"               Note
Ensure-Field "Company registration number"       "CompanyRegNo"             Text     -AddToDefaultView
Ensure-Field "VAT number"                        "VATNumber"                Text
Ensure-Field "Parent/holding company"            "ParentCompany"            Text
Ensure-Field "Years trading"                     "YearsTrading"             Number   -AddToDefaultView @{ "MinimumValue"="0" }

# Primary Contact
Ensure-Field "Primary contact name"              "PrimaryContactName"       Text     -AddToDefaultView
Ensure-Field "Primary contact title"             "PrimaryContactTitle"      Text
Ensure-Field "Primary contact phone"             "PrimaryContactPhone"      Text
Ensure-Field "Primary contact email"             "PrimaryContactEmail"      Text

# --- Section 2: Services & Roles ---
Ensure-ChoiceField -DisplayName "Services provided" -InternalName "Services" -Choices @("EPC","Design","O&M","Roof Solar","Ground Solar","Carports","Battery Storage","CHP","HV/LV Electrical","Civils","Structural","Other") -Multi
Ensure-Field "Specialisations"                    "Specialisations"          Note
Ensure-Field "Software tools used"                "SoftwareUsed"             Note
Ensure-Field "Average projects per month"         "ProjectsPerMonth"         Number @{ "MinimumValue"="0" }

Ensure-Field "Acts as Principal Contractor"       "ActsAsPrincipalContractor" Boolean  -AddToDefaultView
Ensure-Field "PC: scale last year"                "PrincipalContractor_LastYearScale" Note
Ensure-Field "Acts as Principal Designer"         "ActsAsPrincipalDesigner"  Boolean
Ensure-Field "PD: scale last year"                "PrincipalDesigner_LastYearScale" Note
Ensure-Field "Internal staff %"                   "LabourMix_InternalPct"    Number @{ "MinimumValue"="0"; "MaximumValue"="100" }
Ensure-Field "Subcontract labour %"               "LabourMix_SubcontractPct" Number @{ "MinimumValue"="0"; "MaximumValue"="100" }

# --- Section 3: Certs & Insurance ---
Ensure-ChoiceField -DisplayName "ISO certifications" -InternalName "ISOStandards" -Choices @("ISO 9001","ISO 14001","ISO 27001","ISO 45001") -Multi -AddToDefaultView
Ensure-ChoiceField -DisplayName "Construction scheme accreditations" -InternalName "ConstructionSchemes" -Choices @("ConstructionLine","CHAS","SMAS","SafeContractor","Other") -Multi
Ensure-Field "NICEIC CPS contractor"             "NICEIC_CPS"               Boolean
Ensure-Field "MCS Approved Contractor"           "MCS_Approved"             Boolean

Ensure-Field "Public & Product Liability present" "PublicProductLiability_Present" Boolean
Ensure-Field "P&PL: Indemnity in Principle clause" "PublicProductLiability_IndemnityInPrinciple" Boolean
Ensure-Field "Employers' Liability present"       "EmployersLiability_Present" Boolean
Ensure-Field "Professional Indemnity present"     "ProfIndemnity_Present"     Boolean
Ensure-Field "P&PL expiry date"                  "PublicProductLiability_Expiry" DateTime
Ensure-Field "EL expiry date"                    "EmployersLiability_Expiry" DateTime
Ensure-Field "PI expiry date"                    "ProfIndemnity_Expiry"      DateTime

# --- Section 4: H,S,Q & Policies ---
Ensure-Field "HSE notices in last 5 years"        "HSE_ImprovementOrProhibition_Last5Y" Text
Ensure-Field "RIDDOR incidents (last 3 years)"    "RIDDOR_Incidents_Last3Y_Count" Number @{ "MinimumValue"="0" }
Ensure-Field "RIDDOR details"                     "RIDDOR_Incidents_Last3Y_Details" Note
Ensure-Field "H&S / CDM2015 evidence (notes)"     "HSE_CDM_Management_Evidence" Note
Ensure-Field "Named Principal Designer"           "Named_PrincipalDesigner"   Text
Ensure-Field "PD qualifications (notes)"          "PD_Qualifications"         Note
Ensure-Field "Training records (notes)"           "TrainingRecords_Summary"   Note
Ensure-Field "Accident/near-miss procedure"       "NearMiss_Procedure"        Text
Ensure-Field "Quality / CI evidence (notes)"      "Quality_Procedure_Evidence" Note

# Policies (dates: supplied via uploads tracked in Evidence lib; dates here for validation dashboards)
Ensure-Field "H&S Policy date signed"             "Policy_HS_DateSigned"      DateTime
Ensure-Field "Environmental Policy date signed"   "Policy_Env_DateSigned"     DateTime
Ensure-Field "Modern Slavery Policy date signed"  "Policy_MS_DateSigned"      DateTime
Ensure-Field "Misuse of Substances date signed"   "Policy_MOS_DateSigned"     DateTime
Ensure-Field "Right-to-Work monitoring method"    "RightToWork_Monitoring_Method" Note
Ensure-Field "GDPR Policy date signed"            "GDPRPolicy_DateSigned"     DateTime
Ensure-Field "Cyber incident in last 3 years"     "CyberIncident_Last3Y"      Text

# --- Section 5: Delivery ---
Ensure-Field "Resourcing approach for Saber projects" "Resources_PerProject"   Note
Ensure-Field "Nationwide coverage"               "Coverage_Nationwide"        Boolean
Ensure-ChoiceField -DisplayName "Regions covered" -InternalName "Coverage_Regions" -Choices @(
  "North East","North West","Yorkshire & Humber","East Midlands","West Midlands","East of England","London",
  "South East","South West","Wales","Scotland","Northern Ireland") -Multi
Ensure-Field "Client reference (notes)"          "Client_Reference"           Note

# --- Section 6: Legal & Agreement & Submission ---
Ensure-Field "Pending prosecutions (details)"    "PendingProsecutions_Details" Note
Ensure-Field "Contracts reviewed by signatories" "Contracts_ReviewedBySignatory" Boolean
Ensure-Field "Legal clarifications / concerns"   "Legal_Clarifications"       Note

Ensure-Field "Received Contract Overview Pack"   "Received_ContractOverviewPack" Boolean
Ensure-Field "Agree to Saber terms"              "Willing_To_WorkToSaberTerms"   Boolean
Ensure-Field "Agree to Codes of Practice"        "AgreeToCodes"               Boolean
Ensure-Field "Consent to data processing (GDPR)" "DataProcessingConsent"      Boolean
Ensure-Field "Consent to marketing comms"        "MarketingConsent"           Boolean
Ensure-Field "Additional information"            "AdditionalInfo"             Note

# Submission workflow helpers
Ensure-ChoiceField -DisplayName "Submission status" -InternalName "SubmissionStatus" -Choices @("Draft","Submitted","Under Review","Approved","Rejected") -AddToDefaultView
Ensure-Field "Reviewer"                            "Reviewer"                 User    @{ "UserSelectionMode"="PeopleOnly" }
Ensure-Field "Review notes"                        "ReviewNotes"              Note

# --- Optional: Index common query fields ---
Set-PnPField -List $epcListTitle -Identity "CompanyName" -Values @{ Indexed = $true } | Out-Null
Set-PnPField -List $epcListTitle -Identity "SubmissionStatus" -Values @{ Indexed = $true } | Out-Null

# --- Views ---
$views = Get-PnPView -List $epcListTitle
if (-not ($views | Where-Object {$_.Title -eq "Submissions"})) {
  Add-PnPView -List $epcListTitle -Title "Submissions" -Fields "ID","CompanyName","PrimaryContactName","PrimaryContactEmail","ISOStandards","Coverage_Nationwide","SubmissionStatus","Modified" -Paged -RowLimit 50 | Out-Null
}
if (-not ($views | Where-Object {$_.Title -eq "Under Review"})) {
  Add-PnPView -List $epcListTitle -Title "Under Review" -Fields "ID","CompanyName","Reviewer","ReviewNotes","Modified" -Query '<Where><Eq><FieldRef Name="SubmissionStatus"/><Value Type="Choice">Under Review</Value></Eq></Where>' -RowLimit 50 | Out-Null
}
if (-not ($views | Where-Object {$_.Title -eq "Approved"})) {
  Add-PnPView -List $epcListTitle -Title "Approved" -Fields "ID","CompanyName","PrimaryContactName","ISOStandards","Coverage_Nationwide","Modified" -Query '<Where><Eq><FieldRef Name="SubmissionStatus"/><Value Type="Choice">Approved</Value></Eq></Where>' -RowLimit 50 | Out-Null
}

# --- Evidence library (for uploads) ---
$evidenceLibTitle = "EPC Onboarding Evidence"
$lib = Get-PnPLibrary -Identity $evidenceLibTitle -ErrorAction SilentlyContinue
if (-not $lib) {
  Write-Host "Creating library '$evidenceLibTitle'..."
  $lib = New-PnPList -Title $evidenceLibTitle -Template DocumentLibrary -OnQuickLaunch
  # Columns to associate evidence to list items & section
  Add-PnPField -List $evidenceLibTitle -DisplayName "EPC Item ID" -InternalName "EpcItemId" -Type Number -Group "EPC Onboarding" | Out-Null
  Ensure-ChoiceField -DisplayName "Evidence Section" -InternalName "EvidenceSection" -Choices @(
    "Certifications","Insurance","Health & Safety","Policies","Data Protection","Delivery","References","Legal"
  ) -Multi:$false
  Add-PnPView -List $evidenceLibTitle -Title "By EPC Item" -Fields "LinkFilename","EpcItemId","EvidenceSection","Modified" -Paged -RowLimit 100 | Out-Null
}

Write-Host "Schema provisioning complete."