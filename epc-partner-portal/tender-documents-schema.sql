-- Tender Documents Schema for SharePoint Integration
-- Tracks document uploads, versions, and sync status with SharePoint

-- Table to track tender documents
CREATE TABLE IF NOT EXISTS tender_documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  partner_id INTEGER,

  -- Document metadata
  original_filename TEXT NOT NULL,
  stored_filename TEXT NOT NULL,
  folder_path TEXT NOT NULL,
  file_size INTEGER,
  content_type TEXT,

  -- SharePoint integration
  sharepoint_id TEXT,
  sharepoint_url TEXT,
  sharepoint_version TEXT DEFAULT '1.0',
  sync_status TEXT DEFAULT 'pending', -- pending, synced, failed
  sync_error TEXT,
  last_synced_at DATETIME,

  -- Version control
  version_number INTEGER DEFAULT 1,
  is_current_version BOOLEAN DEFAULT TRUE,
  previous_version_id INTEGER,
  version_notes TEXT,

  -- R2 storage
  r2_key TEXT,
  r2_url TEXT,

  -- Audit fields
  uploaded_by TEXT,
  uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  modified_by TEXT,
  modified_at DATETIME,
  deleted_at DATETIME,
  deleted_by TEXT,

  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (partner_id) REFERENCES partners(id),
  FOREIGN KEY (previous_version_id) REFERENCES tender_documents(id)
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_tender_docs_project ON tender_documents(project_id);
CREATE INDEX IF NOT EXISTS idx_tender_docs_partner ON tender_documents(partner_id);
CREATE INDEX IF NOT EXISTS idx_tender_docs_folder ON tender_documents(folder_path);
CREATE INDEX IF NOT EXISTS idx_tender_docs_sharepoint ON tender_documents(sharepoint_id);
CREATE INDEX IF NOT EXISTS idx_tender_docs_version ON tender_documents(project_id, original_filename, is_current_version);

-- Table for document access log
CREATE TABLE IF NOT EXISTS document_access_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id INTEGER NOT NULL,
  action TEXT NOT NULL, -- viewed, downloaded, updated, deleted
  performed_by TEXT NOT NULL,
  performed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  ip_address TEXT,
  user_agent TEXT,

  FOREIGN KEY (document_id) REFERENCES tender_documents(id)
);

-- Table for document permissions (if needed for partner-specific access)
CREATE TABLE IF NOT EXISTS document_permissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id INTEGER NOT NULL,
  partner_id INTEGER,
  permission_type TEXT NOT NULL, -- read, write, delete
  granted_by TEXT,
  granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  revoked_at DATETIME,
  revoked_by TEXT,

  FOREIGN KEY (document_id) REFERENCES tender_documents(id),
  FOREIGN KEY (partner_id) REFERENCES partners(id)
);

-- View for current documents (latest versions only)
CREATE VIEW IF NOT EXISTS current_tender_documents AS
SELECT
  td.*,
  p.project_name,
  p.tender_id,
  ptr.company_name as partner_name
FROM tender_documents td
LEFT JOIN projects p ON td.project_id = p.id
LEFT JOIN partners ptr ON td.partner_id = ptr.id
WHERE td.is_current_version = TRUE
  AND td.deleted_at IS NULL;