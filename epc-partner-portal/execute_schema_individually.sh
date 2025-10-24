#!/bin/bash

# Script to execute SQL schema commands individually on D1 database
source /home/marstack/.cloudflare-env

echo "Executing SQL schema on D1 database epc-form-data..."

# Execute each major SQL statement individually
echo "Creating applications table..."
wrangler d1 execute epc-form-data --remote --command="CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invitation_code TEXT NOT NULL,
    reference_number TEXT UNIQUE,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'submitted', 'processing', 'completed', 'rejected')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    submitted_at DATETIME,
    company_name TEXT,
    trading_name TEXT,
    registration_number TEXT,
    vat_number TEXT,
    registered_address TEXT,
    head_office TEXT,
    parent_company TEXT,
    years_trading INTEGER,
    contact_name TEXT,
    contact_title TEXT,
    email TEXT,
    phone TEXT,
    company_website TEXT,
    specializations TEXT,
    software_tools TEXT,
    projects_per_month INTEGER,
    team_size INTEGER,
    years_experience INTEGER,
    services TEXT,
    coverage TEXT,
    coverage_region TEXT,
    resources_per_project TEXT,
    client_reference TEXT,
    principal_contractor BOOLEAN DEFAULT FALSE,
    principal_designer BOOLEAN DEFAULT FALSE,
    principal_contractor_scale TEXT,
    principal_designer_scale TEXT,
    internal_staff_percentage TEXT,
    subcontract_percentage TEXT,
    niceic_contractor BOOLEAN DEFAULT FALSE,
    mcs_approved BOOLEAN DEFAULT FALSE,
    accreditations TEXT,
    certification_details TEXT,
    iso_standards TEXT,
    named_principal_designer TEXT,
    principal_designer_qualifications TEXT,
    training_records_summary TEXT,
    public_liability_insurance BOOLEAN DEFAULT FALSE,
    public_liability_expiry DATE,
    public_liability_indemnity BOOLEAN DEFAULT FALSE,
    employers_liability_insurance BOOLEAN DEFAULT FALSE,
    employers_liability_expiry DATE,
    professional_indemnity_insurance BOOLEAN DEFAULT FALSE,
    professional_indemnity_expiry DATE,
    hse_notices_last_5_years TEXT,
    pending_prosecutions TEXT,
    riddor_incident_count INTEGER,
    riddor_incident_details TEXT,
    cdm_management_evidence TEXT,
    near_miss_procedure TEXT,
    quality_procedure_evidence TEXT,
    hseq_incidents TEXT,
    riddor_incidents TEXT,
    health_safety_policy_date DATE,
    environmental_policy_date DATE,
    modern_slavery_policy_date DATE,
    substance_misuse_policy_date DATE,
    right_to_work_method TEXT,
    gdpr_policy_date DATE,
    cyber_incident_last_3_years TEXT,
    legal_clarifications TEXT,
    agree_to_terms BOOLEAN DEFAULT FALSE,
    agree_to_codes BOOLEAN DEFAULT FALSE,
    data_processing_consent BOOLEAN DEFAULT FALSE,
    marketing_consent BOOLEAN DEFAULT FALSE,
    nationwide_coverage BOOLEAN DEFAULT FALSE,
    contracts_reviewed BOOLEAN DEFAULT FALSE,
    received_contract_pack BOOLEAN DEFAULT FALSE,
    additional_information TEXT,
    notes TEXT,
    clarifications TEXT
);"

echo "Creating application_files table..."
wrangler d1 execute epc-form-data --remote --command="CREATE TABLE IF NOT EXISTS application_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    file_size INTEGER,
    content_type TEXT,
    upload_url TEXT,
    sharepoint_id TEXT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications (id) ON DELETE CASCADE
);"

echo "Creating draft_data table..."
wrangler d1 execute epc-form-data --remote --command="CREATE TABLE IF NOT EXISTS draft_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invitation_code TEXT UNIQUE NOT NULL,
    form_data TEXT,
    current_step INTEGER DEFAULT 1,
    last_saved DATETIME DEFAULT CURRENT_TIMESTAMP
);"

echo "Creating audit_log table..."
wrangler d1 execute epc-form-data --remote --command="CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    user_info TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications (id) ON DELETE CASCADE
);"

echo "Creating indexes..."
wrangler d1 execute epc-form-data --remote --command="CREATE INDEX IF NOT EXISTS idx_applications_invitation_code ON applications (invitation_code);"
wrangler d1 execute epc-form-data --remote --command="CREATE INDEX IF NOT EXISTS idx_applications_reference_number ON applications (reference_number);"
wrangler d1 execute epc-form-data --remote --command="CREATE INDEX IF NOT EXISTS idx_applications_status ON applications (status);"
wrangler d1 execute epc-form-data --remote --command="CREATE INDEX IF NOT EXISTS idx_applications_created_at ON applications (created_at);"
wrangler d1 execute epc-form-data --remote --command="CREATE INDEX IF NOT EXISTS idx_application_files_application_id ON application_files (application_id);"
wrangler d1 execute epc-form-data --remote --command="CREATE INDEX IF NOT EXISTS idx_draft_data_invitation_code ON draft_data (invitation_code);"
wrangler d1 execute epc-form-data --remote --command="CREATE INDEX IF NOT EXISTS idx_audit_log_application_id ON audit_log (application_id);"

echo "Creating trigger..."
wrangler d1 execute epc-form-data --remote --command="CREATE TRIGGER IF NOT EXISTS update_applications_updated_at 
    AFTER UPDATE ON applications
BEGIN
    UPDATE applications SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;"

echo "Schema execution completed!"