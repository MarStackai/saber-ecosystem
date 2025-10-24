// D1 Database helpers for EPC Portal
// This replaces Redis for Cloudflare-native data persistence

export class D1Helper {
  constructor(database) {
    this.db = database;
  }

  // Save draft form data for auto-save functionality
  async saveDraft(invitationCode, formData, currentStep) {
    const now = new Date().toISOString();
    
    try {
      await this.db.prepare(`
        INSERT OR REPLACE INTO draft_data (
          invitation_code, form_data, current_step, last_saved, status
        ) VALUES (?, ?, ?, ?, ?)
      `).bind(
        invitationCode,
        JSON.stringify(formData),
        currentStep,
        now,
        'draft'
      ).run();
      
      console.log(`✅ Draft saved for invitation: ${invitationCode}`);
      return { success: true, lastSaved: now };
    } catch (error) {
      console.error('❌ D1 draft save error:', error);
      throw error;
    }
  }

  // Retrieve draft form data
  async getDraft(invitationCode) {
    try {
      const result = await this.db.prepare(`
        SELECT form_data, current_step, last_saved, status
        FROM draft_data 
        WHERE invitation_code = ?
        ORDER BY last_saved DESC
        LIMIT 1
      `).bind(invitationCode).first();

      if (result) {
        return {
          formData: JSON.parse(result.form_data),
          currentStep: result.current_step,
          lastSaved: result.last_saved,
          status: result.status
        };
      }
      return null;
    } catch (error) {
      console.error('❌ D1 draft retrieval error:', error);
      return null;
    }
  }

  // Submit complete application to D1
  async submitApplication(invitationCode, formData, files = {}) {
    const now = new Date().toISOString();
    const referenceNumber = `EPC${Date.now()}`;
    
    try {
      // Start transaction
      await this.db.prepare(`
        INSERT INTO applications (
          invitation_code,
          reference_number,
          status,
          submission_date,
          company_name,
          trading_name,
          registered_office,
          company_registration_number,
          vat_number,
          years_trading,
          company_website,
          primary_contact_name,
          primary_contact_email,
          primary_contact_phone,
          coverage_regions,
          iso_standards,
          acts_as_principal_contractor,
          acts_as_principal_designer,
          has_gdpr_policy,
          hseq_incidents_last_5y,
          riddor_last_3y,
          notes_clarifications,
          created_at,
          updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        invitationCode,
        referenceNumber,
        'submitted',
        now,
        formData.companyName || '',
        formData.tradingName || '',
        formData.registeredOffice || '',
        formData.companyRegNo || '',
        formData.vatNo || '',
        parseInt(formData.yearsTrading) || 0,
        formData.companyWebsite || '',
        formData.primaryContactName || '',
        formData.primaryContactEmail || '',
        formData.primaryContactPhone || '',
        JSON.stringify(formData.coverageRegion || []),
        JSON.stringify(formData.isoStandards || []),
        formData.actsAsPrincipalContractor === 'yes',
        formData.actsAsPrincipalDesigner === 'yes',
        formData.hasGDPRPolicy === 'yes',
        parseInt(formData.hsqIncidents) || 0,
        parseInt(formData.riddor) || 0,
        formData.notes || '',
        now,
        now
      ).run();

      // Store file references
      for (const [fieldName, fileInfo] of Object.entries(files)) {
        if (fileInfo) {
          await this.db.prepare(`
            INSERT INTO application_files (
              invitation_code,
              field_name,
              original_filename,
              file_size,
              content_type,
              storage_path,
              upload_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
          `).bind(
            invitationCode,
            fieldName,
            fileInfo.name,
            fileInfo.size,
            fileInfo.type,
            fileInfo.storagePath || '',
            now
          ).run();
        }
      }

      // Clear draft after successful submission
      await this.clearDraft(invitationCode);

      console.log(`✅ Application submitted: ${referenceNumber}`);
      return {
        success: true,
        referenceNumber,
        submissionDate: now
      };
      
    } catch (error) {
      console.error('❌ D1 application submission error:', error);
      throw error;
    }
  }

  // Clear draft after successful submission
  async clearDraft(invitationCode) {
    try {
      await this.db.prepare(`
        DELETE FROM draft_data WHERE invitation_code = ?
      `).bind(invitationCode).run();
      
      console.log(`✅ Draft cleared for invitation: ${invitationCode}`);
    } catch (error) {
      console.error('❌ D1 draft clear error:', error);
    }
  }

  // Get all applications for operations dashboard
  async getAllApplications(limit = 50) {
    try {
      const results = await this.db.prepare(`
        SELECT 
          reference_number,
          company_name,
          primary_contact_name,
          primary_contact_email,
          status,
          submission_date,
          invitation_code
        FROM applications 
        ORDER BY submission_date DESC 
        LIMIT ?
      `).bind(limit).all();

      return results.results || [];
    } catch (error) {
      console.error('❌ D1 applications retrieval error:', error);
      return [];
    }
  }

  // Update application status (e.g., after SharePoint sync)
  async updateApplicationStatus(invitationCode, status, sharePointId = null) {
    try {
      const query = sharePointId 
        ? `UPDATE applications SET status = ?, sharepoint_id = ?, updated_at = ? WHERE invitation_code = ?`
        : `UPDATE applications SET status = ?, updated_at = ? WHERE invitation_code = ?`;
        
      const params = sharePointId
        ? [status, sharePointId, new Date().toISOString(), invitationCode]
        : [status, new Date().toISOString(), invitationCode];

      await this.db.prepare(query).bind(...params).run();
      
      console.log(`✅ Application status updated: ${invitationCode} -> ${status}`);
    } catch (error) {
      console.error('❌ D1 status update error:', error);
      throw error;
    }
  }
}

// Helper function to get D1 database from environment
export function getD1Database(env) {
  if (env.epc_form_data) {
    return new D1Helper(env.epc_form_data);
  }
  
  // Development fallback - log warning
  console.log('⚠️  D1 database not available, using mock helper');
  return createMockD1Helper();
}

// Mock D1 helper for development
function createMockD1Helper() {
  const mockStorage = new Map();
  
  return {
    async saveDraft(invitationCode, formData, currentStep) {
      const now = new Date().toISOString();
      mockStorage.set(`draft:${invitationCode}`, {
        formData,
        currentStep,
        lastSaved: now,
        status: 'draft'
      });
      console.log(`📝 Mock: Draft saved for ${invitationCode}`);
      return { success: true, lastSaved: now };
    },

    async getDraft(invitationCode) {
      const draft = mockStorage.get(`draft:${invitationCode}`);
      console.log(`📖 Mock: Retrieved draft for ${invitationCode}:`, !!draft);
      return draft || null;
    },

    async submitApplication(invitationCode, formData, files = {}) {
      const referenceNumber = `EPC${Date.now()}`;
      const now = new Date().toISOString();
      
      mockStorage.set(`app:${invitationCode}`, {
        referenceNumber,
        formData,
        files,
        status: 'submitted',
        submissionDate: now
      });
      
      // Clear draft
      mockStorage.delete(`draft:${invitationCode}`);
      
      console.log(`📝 Mock: Application submitted: ${referenceNumber}`);
      return {
        success: true,
        referenceNumber,
        submissionDate: now
      };
    },

    async clearDraft(invitationCode) {
      mockStorage.delete(`draft:${invitationCode}`);
      console.log(`🗑️  Mock: Draft cleared for ${invitationCode}`);
    },

    async getAllApplications(limit = 50) {
      const applications = [];
      for (const [key, value] of mockStorage.entries()) {
        if (key.startsWith('app:')) {
          applications.push({
            reference_number: value.referenceNumber,
            company_name: value.formData.companyName || 'Unknown',
            primary_contact_name: value.formData.primaryContactName || 'Unknown',
            primary_contact_email: value.formData.primaryContactEmail || 'Unknown',
            status: value.status,
            submission_date: value.submissionDate,
            invitation_code: key.replace('app:', '')
          });
        }
      }
      console.log(`📊 Mock: Retrieved ${applications.length} applications`);
      return applications;
    },

    async updateApplicationStatus(invitationCode, status, sharePointId = null) {
      const app = mockStorage.get(`app:${invitationCode}`);
      if (app) {
        app.status = status;
        if (sharePointId) app.sharePointId = sharePointId;
        mockStorage.set(`app:${invitationCode}`, app);
      }
      console.log(`📝 Mock: Status updated: ${invitationCode} -> ${status}`);
    }
  };
}