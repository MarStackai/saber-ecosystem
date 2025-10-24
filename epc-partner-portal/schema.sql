-- EPC Partner Application Database Schema
-- Tables for storing form data, file metadata, and application submissions

-- Invitations table (used by sync/validate APIs)
CREATE TABLE IF NOT EXISTS invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auth_code TEXT UNIQUE NOT NULL,
    title TEXT,
    company_name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    notes TEXT,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invitations_auth_code ON invitations (auth_code);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON invitations (status);

CREATE TRIGGER IF NOT EXISTS update_invitations_updated_at 
    AFTER UPDATE ON invitations
BEGIN
    UPDATE invitations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Main applications table
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invitation_code TEXT NOT NULL,
    reference_number TEXT UNIQUE,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'submitted', 'processing', 'completed', 'rejected')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    submitted_at DATETIME,
    
    -- Company Information (Page 1)
    company_name TEXT,
    trading_name TEXT,
    registration_number TEXT,
    vat_number TEXT,
    registered_address TEXT,
    head_office TEXT,
    parent_company TEXT,
    years_trading INTEGER,
    
    -- Contact Information (Page 2)
    contact_name TEXT,
    contact_title TEXT,
    email TEXT,
    phone TEXT,
    company_website TEXT,
    
    -- Capabilities & Experience (Page 3)
    specializations TEXT,
    software_tools TEXT,
    projects_per_month INTEGER,
    team_size INTEGER,
    years_experience INTEGER,
    services TEXT,
    coverage TEXT,
    coverage_region TEXT,
    coverage_regions TEXT, -- JSON array of regions covered
    partner_logo_url TEXT,
    partner_logo_sp_id TEXT,
    resources_per_project TEXT,
    client_reference TEXT,
    
    -- Roles & Certifications (Page 4)
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
    
    -- Insurance & Compliance (Page 5)
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
    
    -- Policy & Compliance Dates (Page 5b)
    health_safety_policy_date DATE,
    environmental_policy_date DATE,
    modern_slavery_policy_date DATE,
    substance_misuse_policy_date DATE,
    right_to_work_method TEXT,
    gdpr_policy_date DATE,
    cyber_incident_last_3_years TEXT,
    legal_clarifications TEXT,
    
    -- Agreement & Submission (Page 6)
    agree_to_terms BOOLEAN DEFAULT FALSE,
    agree_to_codes BOOLEAN DEFAULT FALSE,
    data_processing_consent BOOLEAN DEFAULT FALSE,
    marketing_consent BOOLEAN DEFAULT FALSE,
    nationwide_coverage BOOLEAN DEFAULT FALSE,
    contracts_reviewed BOOLEAN DEFAULT FALSE,
    received_contract_pack BOOLEAN DEFAULT FALSE,
    additional_information TEXT,
    notes TEXT,
    clarifications TEXT,

    -- Partner approval status
    partner_approved BOOLEAN DEFAULT FALSE,
    approved_at DATETIME,
    approved_by TEXT, -- email of approver
    can_access_projects BOOLEAN DEFAULT FALSE
);

-- Files table for storing file metadata
CREATE TABLE IF NOT EXISTS application_files (
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
);

-- Draft data table for auto-save functionality
CREATE TABLE IF NOT EXISTS draft_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invitation_code TEXT UNIQUE NOT NULL,
    form_data TEXT, -- JSON string of form data
    current_step INTEGER DEFAULT 1,
    last_saved DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for tracking changes
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER,
    action TEXT NOT NULL,
    details TEXT, -- JSON string of changes
    user_info TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (application_id) REFERENCES applications (id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_applications_invitation_code ON applications (invitation_code);
CREATE INDEX IF NOT EXISTS idx_applications_reference_number ON applications (reference_number);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications (status);
CREATE INDEX IF NOT EXISTS idx_applications_created_at ON applications (created_at);
CREATE INDEX IF NOT EXISTS idx_application_files_application_id ON application_files (application_id);
CREATE INDEX IF NOT EXISTS idx_draft_data_invitation_code ON draft_data (invitation_code);
CREATE INDEX IF NOT EXISTS idx_audit_log_application_id ON audit_log (application_id);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_applications_updated_at 
    AFTER UPDATE ON applications
BEGIN
    UPDATE applications SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Section-by-section reviews for operations
CREATE TABLE IF NOT EXISTS application_section_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    section TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
    reviewer TEXT,
    note TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(application_id, section),
    FOREIGN KEY (application_id) REFERENCES applications (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_app_section_reviews_app ON application_section_reviews (application_id);

-- Free-form notes by operations team
CREATE TABLE IF NOT EXISTS application_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    author TEXT,
    note TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_application_notes_app ON application_notes (application_id);

-- Insert some initial test data (optional)
-- INSERT INTO applications (invitation_code, company_name, email, status) 
-- VALUES ('TEST001', 'Test Company Ltd', 'test@example.com', 'draft');

-- Draft files table: store uploaded documents in R2 until final submission
CREATE TABLE IF NOT EXISTS draft_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invitation_code TEXT NOT NULL,
    field_name TEXT NOT NULL,
    r2_key TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    content_type TEXT,
    file_size INTEGER,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_draft_files_invitation ON draft_files (invitation_code);

-- Partner portal and project management tables

-- Partner sessions for authentication
CREATE TABLE IF NOT EXISTS partner_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (partner_id) REFERENCES applications (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_partner_sessions_token ON partner_sessions (session_token);
CREATE INDEX IF NOT EXISTS idx_partner_sessions_partner ON partner_sessions (partner_id);
CREATE INDEX IF NOT EXISTS idx_partner_sessions_email ON partner_sessions (email);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    project_code TEXT UNIQUE,
    tender_id TEXT UNIQUE, -- SABER-XXXX format
    description TEXT,
    client_name TEXT,
    location TEXT,
    latitude REAL,
    longitude REAL,
    project_type TEXT, -- 'G99', 'Planning', 'EPC', etc.
    status TEXT DEFAULT 'active' CHECK(status IN ('draft', 'active', 'completed', 'cancelled')),
    tender_status TEXT DEFAULT 'NEW' CHECK(tender_status IN ('NEW', 'IN_REVIEW', 'PLANNING', 'LIVE')),
    created_by TEXT, -- email of creator
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    start_date DATE,
    target_completion DATE
);

CREATE INDEX IF NOT EXISTS idx_projects_code ON projects (project_code);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects (status);
CREATE INDEX IF NOT EXISTS idx_projects_type ON projects (project_type);
CREATE INDEX IF NOT EXISTS idx_projects_tender_id ON projects (tender_id);
CREATE INDEX IF NOT EXISTS idx_projects_tender_status ON projects (tender_status);

CREATE TRIGGER IF NOT EXISTS update_projects_updated_at
    AFTER UPDATE ON projects
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Tender sequence for auto-generated SABER-XXXX IDs
CREATE TABLE IF NOT EXISTS tender_sequence (
    id INTEGER PRIMARY KEY DEFAULT 1,
    last_number INTEGER DEFAULT 0
);

-- Insert initial sequence value if not exists
INSERT OR IGNORE INTO tender_sequence (id, last_number) VALUES (1, 0);

-- Project documents table for tender documentation
CREATE TABLE IF NOT EXISTS project_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    document_name TEXT NOT NULL,
    document_type TEXT,
    original_filename TEXT,
    r2_key TEXT,
    sharepoint_url TEXT,
    file_size INTEGER,
    content_type TEXT,
    uploaded_by TEXT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_documents_project ON project_documents (project_id);

-- Project partners - which partners are assigned to which projects
CREATE TABLE IF NOT EXISTS project_partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL,
    role TEXT DEFAULT 'contributor', -- 'viewer', 'contributor', 'manager'
    invited_by TEXT, -- email of inviter
    invited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    accepted_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'invited' CHECK(status IN ('invited', 'accepted', 'declined', 'revoked')),
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
    FOREIGN KEY (partner_id) REFERENCES applications (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_partners_project ON project_partners (project_id);
CREATE INDEX IF NOT EXISTS idx_project_partners_partner ON project_partners (partner_id);
CREATE INDEX IF NOT EXISTS idx_project_partners_status ON project_partners (status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_project_partners_unique ON project_partners (project_id, partner_id);

-- Project deliverables - track required documents per project phase
CREATE TABLE IF NOT EXISTS project_deliverables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    folder_path TEXT NOT NULL, -- e.g., "01. Design", "02. Grid/G99 Application"
    deliverable_name TEXT NOT NULL,
    description TEXT,
    required BOOLEAN DEFAULT TRUE,
    due_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_deliverables_project ON project_deliverables (project_id);
CREATE INDEX IF NOT EXISTS idx_project_deliverables_folder ON project_deliverables (folder_path);

-- Partner uploads - track partner file submissions for projects
CREATE TABLE IF NOT EXISTS partner_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL,
    deliverable_id INTEGER, -- optional link to specific deliverable
    folder_path TEXT NOT NULL, -- matches SharePoint structure
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    r2_key TEXT, -- temporary storage before SharePoint migration
    sharepoint_url TEXT, -- final SharePoint location
    content_type TEXT,
    file_size INTEGER,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'submitted', 'approved', 'rejected')),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    submitted_at DATETIME,
    reviewed_at DATETIME,
    reviewed_by TEXT, -- email of reviewer
    review_notes TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
    FOREIGN KEY (partner_id) REFERENCES applications (id) ON DELETE CASCADE,
    FOREIGN KEY (deliverable_id) REFERENCES project_deliverables (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_partner_uploads_project ON partner_uploads (project_id);
CREATE INDEX IF NOT EXISTS idx_partner_uploads_partner ON partner_uploads (partner_id);
CREATE INDEX IF NOT EXISTS idx_partner_uploads_status ON partner_uploads (status);
CREATE INDEX IF NOT EXISTS idx_partner_uploads_folder ON partner_uploads (folder_path);

-- Project notifications
CREATE TABLE IF NOT EXISTS project_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    partner_id INTEGER, -- NULL for system notifications
    notification_type TEXT NOT NULL, -- 'invitation', 'deadline', 'approval', 'submission'
    title TEXT NOT NULL,
    message TEXT,
    read_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
    FOREIGN KEY (partner_id) REFERENCES applications (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_notifications_project ON project_notifications (project_id);
CREATE INDEX IF NOT EXISTS idx_project_notifications_partner ON project_notifications (partner_id);
CREATE INDEX IF NOT EXISTS idx_project_notifications_type ON project_notifications (notification_type);
