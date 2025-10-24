// Minimal EPC Backend Worker - Just API endpoints + simple operations
import { connect } from 'cloudflare:sockets';
import SharePointDocumentSync from './lib/sharepoint-sync.js';

// Dynamic CORS based on environment
const getCorsHeaders = (env) => {
  const origins = {
    'development': 'http://localhost:4200',
    'staging': 'https://staging-epc.saberrenewable.energy',
    'production': 'https://epc.saberrenewable.energy'
  };

  const origin = origins[env.ENVIRONMENT] || origins.production;

  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const corsHeaders = getCorsHeaders(env);

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Only handle specific routes, let React frontend handle the rest
    
    // Simple operations page - list applications
    if (url.pathname === '/operations') {
      return getOperationsPage(env);
    }

    // Operations detail page: /operations/<id or invitationCode>
    if (url.pathname.startsWith('/operations/')) {
      const ref = url.pathname.split('/')[2];
      return getOperationDetailPage(ref, env);
    }

    // Redirect /form/<code> -> /form?invitationCode=<code>
    if (url.pathname.startsWith('/form/')) {
      const code = url.pathname.split('/')[2];
      const target = `${url.origin}/form?invitationCode=${encodeURIComponent(code || '')}`;
      return Response.redirect(target, 302);
    }

    // API: Submit application (finalize). Creates D1 application and migrates R2 files to SharePoint
    if ((url.pathname === '/api/epc-application' || url.pathname === '/api/submit') && request.method === 'POST') {
      return submitEpcApplication(request, env, ctx);
    }

    // API: Get all applications from D1
    if (url.pathname === '/api/applications' && request.method === 'GET') {
      return getApplicationsD1(env);
    }

    // API: Get single application by id or invitation code
    if (url.pathname.startsWith('/api/application/') && request.method === 'GET') {
      const refNum = url.pathname.split('/')[3];
      return getApplicationAPI(env, refNum);
    }

    // API: Upload file (draft phase) -> store in R2 only; no SharePoint until final submission
    if ((url.pathname === '/upload-file' || url.pathname === '/api/upload-file') && request.method === 'POST') {
      return handleFileUploadToR2(request, env);
    }

    // API: Validate invitation codes (with hardcoded fallback for immediate functionality)
    if (url.pathname === '/api/validate-invitation' && request.method === 'POST') {
      return validateInvitation(request, env);
    }

    // API: Sync invitation from Power Automate
    if (url.pathname === '/api/sync-invitation' && request.method === 'POST') {
      return syncInvitation(request, env);
    }

    // API: Manually trigger migration of draft files from R2 to SharePoint
    if (url.pathname === '/api/migrate-files' && request.method === 'POST') {
      return migrateFilesEndpoint(request, env, ctx);
    }

    // API: Status for an invitation/application
    if (url.pathname === '/api/status' && request.method === 'GET') {
      return statusEndpoint(request, env);
    }

    // Reviews & notes endpoints
    const reviewMatch = url.pathname.match(/^\/api\/application\/(\d+)\/(reviews|review|notes|note|approve-all|delete)$/);
    if (reviewMatch) {
      const appId = parseInt(reviewMatch[1]);
      const action = reviewMatch[2];
      if (action === 'reviews' && request.method === 'GET') return getReviews(appId, env);
      if (action === 'review' && request.method === 'POST') return postReview(appId, request, env, ctx);
      if (action === 'notes' && request.method === 'GET') return getNotes(appId, env);
      if (action === 'note' && request.method === 'POST') return postNote(appId, request, env);
      if (action === 'approve-all' && request.method === 'POST') return approveAllHandler(appId, request, env, ctx);
      if (action === 'delete' && request.method === 'POST') return deleteApplicationHandler(appId, env, ctx);
      return new Response('Method not allowed', { status: 405, headers: corsHeaders });
    }

    // API: Save and retrieve draft data
    if (url.pathname === '/api/save-draft') {
      if (request.method === 'POST') return saveDraftHandler(request, env);
      if (request.method === 'GET') return loadDraftHandler(request, env);
      return new Response('Method not allowed', { status: 405, headers: corsHeaders });
    }

    // API: Clear draft
    if (url.pathname === '/api/clear-draft' && request.method === 'POST') {
      return clearDraftHandler(request, env);
    }

    // Admin API: List all applications (for cleanup)
    if (url.pathname === '/api/admin/applications' && request.method === 'GET') {
      try {
        const result = await env.epc_form_data.prepare('SELECT id, company_name, email, status, created_at FROM applications ORDER BY id').all();
        return new Response(JSON.stringify(result.results, null, 2), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Cleanup test data (keep only IDs 20, 22, 23)
    if (url.pathname === '/api/admin/cleanup' && request.method === 'POST') {
      try {
        // Delete test records: IDs 1-19 (except 20), and any future test IDs
        // Keep: ID 20 (Nimbus Solar EPC - test with approved status), ID 22 (Alt-Solar), ID 23 (Solarcrown)
        const deleteResult = await env.epc_form_data.prepare(
          'DELETE FROM applications WHERE id < 20 OR (id > 20 AND id != 22 AND id != 23 AND id < 100)'
        ).run();

        // Also clean up related data
        await env.epc_form_data.prepare('DELETE FROM application_files WHERE application_id NOT IN (20, 22, 23)').run();
        await env.epc_form_data.prepare('DELETE FROM draft_data WHERE invitation_code NOT IN (SELECT invitation_code FROM applications WHERE id IN (20, 22, 23))').run();

        return new Response(JSON.stringify({
          success: true,
          deleted_applications: deleteResult.changes,
          message: 'Cleaned up test data, kept IDs 20, 22, 23'
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Upload document to project
    if (url.pathname === '/api/admin/upload-document' && request.method === 'POST') {
      try {
        const requestData = await request.json();
        const { projectId, folderPath, originalFilename, contentType, fileSize, r2Key, fileData } = requestData;

        if (!projectId || !folderPath || !originalFilename || !r2Key || !fileData) {
          return new Response(JSON.stringify({ error: 'Missing required fields' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        // Convert array back to Uint8Array and upload to R2
        const fileBuffer = new Uint8Array(fileData);
        await env.EPC_DOCUMENTS.put(r2Key, fileBuffer, {
          httpMetadata: {
            contentType: contentType
          }
        });

        // Insert document record into database
        const insertResult = await env.epc_form_data.prepare(`
          INSERT INTO project_documents
          (project_id, document_name, document_type, original_filename, r2_key, file_size, content_type, uploaded_by)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(
          projectId,
          originalFilename,
          folderPath,
          originalFilename,
          r2Key,
          fileSize,
          contentType,
          'operations@saberrenewables.com'
        ).run();

        return new Response(JSON.stringify({
          success: true,
          documentId: insertResult.meta.last_row_id,
          r2Key: r2Key
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        console.error('Document upload error:', error);
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Upload tender document with SharePoint integration
    if (url.pathname === '/api/admin/tender-document/upload' && request.method === 'POST') {
      try {
        const formData = await request.formData();
        const tenderId = formData.get('tenderId');
        const tenderName = formData.get('tenderName');
        const partnerName = formData.get('partnerName');
        const folderPath = formData.get('folderPath');
        const document = formData.get('document');

        if (!tenderId || !tenderName || !partnerName || !folderPath || !document) {
          return new Response(JSON.stringify({ error: 'Missing required fields' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        // Get document info
        const originalFilename = document.name;
        const contentType = document.type;
        const fileSize = document.size;
        const fileBuffer = await document.arrayBuffer();

        console.log(`Processing tender document: ${originalFilename} for tender ${tenderId}`);

        // Generate R2 key
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const r2Key = `tender-documents/${tenderId}/${folderPath}/${timestamp}-${originalFilename}`;

        // Store in R2 first
        await env.EPC_DOCUMENTS.put(r2Key, fileBuffer, {
          httpMetadata: {
            contentType: contentType || 'application/octet-stream'
          },
          customMetadata: {
            tenderId,
            tenderName,
            partnerName,
            folderPath,
            originalFilename,
            uploadedAt: new Date().toISOString()
          }
        });

        console.log(`Document stored in R2: ${r2Key}`);

        // Initialize SharePoint sync
        const sharePointSync = new SharePointDocumentSync(env);

        // Upload to SharePoint with proper folder structure
        const sharePointResult = await sharePointSync.uploadToSharePoint(
          tenderId,
          partnerName,
          folderPath,
          originalFilename,
          new Uint8Array(fileBuffer),
          {
            TenderName: tenderName,
            PartnerName: partnerName,
            UploadedBy: 'Admin',
            UploadDate: new Date().toISOString()
          }
        );

        console.log('SharePoint upload result:', sharePointResult);

        // For testing, we'll simulate the database storage since we need the tender_documents table
        // In production, this would be stored in the actual database

        return new Response(JSON.stringify({
          success: true,
          document: {
            tender_id: tenderId,
            tender_name: tenderName,
            partner_name: partnerName,
            folder_path: folderPath,
            original_filename: originalFilename,
            file_size: fileSize,
            content_type: contentType,
            r2_key: r2Key,
            version_number: 1
          },
          sharepoint: sharePointResult.success ? {
            folderCreated: sharePointResult.folderCreated,
            uploaded: true,
            url: sharePointResult.sharePointUrl,
            version: sharePointResult.version
          } : {
            folderCreated: false,
            uploaded: false,
            error: sharePointResult.error
          }
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        console.error('Tender document upload error:', error);
        return new Response(JSON.stringify({ error: 'Failed to upload document' }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Delete document
    if (url.pathname === '/api/admin/delete-document' && request.method === 'DELETE') {
      try {
        const { fileId } = await request.json();

        if (!fileId) {
          return new Response(JSON.stringify({ error: 'Missing fileId' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        // Get document info first
        const docResult = await env.epc_form_data.prepare(
          'SELECT r2_key FROM project_documents WHERE id = ?'
        ).bind(fileId).first();

        if (!docResult) {
          return new Response(JSON.stringify({ error: 'Document not found' }), {
            status: 404,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        // Delete from R2
        await env.EPC_DOCUMENTS.delete(docResult.r2_key);

        // Delete from database
        await env.epc_form_data.prepare('DELETE FROM project_documents WHERE id = ?').bind(fileId).run();

        return new Response(JSON.stringify({ success: true }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        console.error('Document delete error:', error);
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Get single project details
    if (url.pathname.startsWith('/api/admin/project/') && !url.pathname.endsWith('/documents') && !url.pathname.endsWith('/partners') && request.method === 'GET') {
      try {
        const projectId = url.pathname.split('/')[4];

        const project = await env.epc_form_data.prepare(`
          SELECT * FROM projects WHERE id = ?
        `).bind(projectId).first();

        if (!project) {
          return new Response(JSON.stringify({ error: 'Project not found' }), {
            status: 404,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        return new Response(JSON.stringify({
          success: true,
          project: project
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Update project details
    if (url.pathname.startsWith('/api/admin/project/') && !url.pathname.endsWith('/documents') && request.method === 'PUT') {
      try {
        const projectId = url.pathname.split('/')[4];
        const updateData = await request.json();

        // Build dynamic update query
        const updateFields = Object.keys(updateData).filter(key => updateData[key] !== undefined);
        if (updateFields.length === 0) {
          return new Response(JSON.stringify({ error: 'No valid fields to update' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        const setClause = updateFields.map(field => `${field} = ?`).join(', ');
        const values = updateFields.map(field => updateData[field]);
        values.push(projectId); // for WHERE clause

        await env.epc_form_data.prepare(`
          UPDATE projects SET ${setClause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        `).bind(...values).run();

        return new Response(JSON.stringify({ success: true }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Get all projects (tenders)
    if (url.pathname === '/api/admin/projects' && request.method === 'GET') {
      try {
        const projects = await env.epc_form_data.prepare(`
          SELECT id, project_name, project_code, tender_id, location, project_type, tender_status, created_at, created_by
          FROM projects
          ORDER BY created_at DESC
        `).all();

        return new Response(JSON.stringify({
          success: true,
          projects: projects.results
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Create new project
    if (url.pathname === '/api/admin/projects' && request.method === 'POST') {
      try {
        const projectData = await request.json();
        const { projectName, location, latitude, longitude, description, projectType } = projectData;

        if (!projectName || !location) {
          return new Response(JSON.stringify({ error: 'Missing required fields: projectName, location' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        // Get next tender sequence number
        const sequenceResult = await env.epc_form_data.prepare('SELECT last_number FROM tender_sequence WHERE id = 1').first();
        const nextNumber = (sequenceResult?.last_number || 0) + 1;
        const tenderId = `SABER-${nextNumber.toString().padStart(4, '0')}`;
        const projectCode = `${projectType}-${nextNumber.toString().padStart(3, '0')}`;

        // Update sequence
        await env.epc_form_data.prepare('UPDATE tender_sequence SET last_number = ? WHERE id = 1').bind(nextNumber).run();

        // Insert project
        const insertResult = await env.epc_form_data.prepare(`
          INSERT INTO projects
          (project_name, project_code, tender_id, description, location, latitude, longitude, project_type, tender_status, created_by)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'NEW', 'operations@saberrenewables.com')
        `).bind(
          projectName, projectCode, tenderId, description, location, latitude, longitude, projectType
        ).run();

        const newProject = {
          id: insertResult.meta.last_row_id,
          project_name: projectName,
          project_code: projectCode,
          tender_id: tenderId,
          description,
          location,
          latitude,
          longitude,
          project_type: projectType,
          tender_status: 'NEW',
          created_by: 'operations@saberrenewables.com',
          created_at: new Date().toISOString()
        };

        return new Response(JSON.stringify({
          success: true,
          project: newProject
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Get project documents
    if (url.pathname.startsWith('/api/admin/project/') && url.pathname.endsWith('/documents') && request.method === 'GET') {
      try {
        const projectId = url.pathname.split('/')[4];

        const documents = await env.epc_form_data.prepare(`
          SELECT id, document_name, document_type, original_filename, file_size, content_type, uploaded_by, uploaded_at
          FROM project_documents
          WHERE project_id = ?
          ORDER BY uploaded_at DESC
        `).bind(projectId).all();

        return new Response(JSON.stringify({
          success: true,
          documents: documents.results
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Get approved partners for invitation
    if (url.pathname === '/api/admin/partners/approved' && request.method === 'GET') {
      try {
        const partners = await env.epc_form_data.prepare(`
          SELECT a.id, a.company_name, a.email, a.coverage_region, a.specializations, a.submitted_at
          FROM applications a
          WHERE a.status = 'completed'
          ORDER BY a.company_name ASC
        `).all();

        return new Response(JSON.stringify({
          success: true,
          partners: partners.results
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        console.error('Error fetching approved partners:', error);
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Get partners invited to a project
    if (url.pathname.startsWith('/api/admin/project/') && url.pathname.endsWith('/partners') && request.method === 'GET') {
      try {
        const projectId = url.pathname.split('/')[4];

        const partners = await env.epc_form_data.prepare(`
          SELECT pp.id, pp.partner_id, pp.role, pp.status, pp.invited_at,
                 a.company_name, a.email
          FROM project_partners pp
          JOIN applications a ON pp.partner_id = a.id
          WHERE pp.project_id = ?
          ORDER BY pp.invited_at DESC
        `).bind(projectId).all();

        return new Response(JSON.stringify({
          success: true,
          partners: partners.results
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        console.error('Error fetching project partners:', error);
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Invite partners to a project
    if (url.pathname.startsWith('/api/admin/project/') && url.pathname.endsWith('/invite-partners') && request.method === 'POST') {
      try {
        const projectId = url.pathname.split('/')[4];
        const { partnerIds, role = 'contributor' } = await request.json();

        if (!partnerIds || !Array.isArray(partnerIds) || partnerIds.length === 0) {
          return new Response(JSON.stringify({ error: 'Partner IDs are required' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        // Insert invitations for each partner
        const invitePromises = partnerIds.map(partnerId =>
          env.epc_form_data.prepare(`
            INSERT INTO project_partners (project_id, partner_id, role, status, invited_at)
            VALUES (?, ?, ?, 'invited', datetime('now'))
          `).bind(projectId, partnerId, role).run()
        );

        await Promise.all(invitePromises);

        return new Response(JSON.stringify({
          success: true,
          message: `Invited ${partnerIds.length} partner(s) to the project`
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        console.error('Error inviting partners:', error);
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Admin API: Update invitation status
    if (url.pathname.startsWith('/api/admin/project-invitation/') && request.method === 'PUT') {
      try {
        const invitationId = url.pathname.split('/')[3];
        const { status } = await request.json();

        if (!['invited', 'accepted', 'declined', 'revoked'].includes(status)) {
          return new Response(JSON.stringify({ error: 'Invalid status' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        await env.epc_form_data.prepare(`
          UPDATE project_partners
          SET status = ?, updated_at = datetime('now')
          WHERE id = ?
        `).bind(status, invitationId).run();

        return new Response(JSON.stringify({
          success: true,
          message: 'Invitation status updated successfully'
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        console.error('Error updating invitation status:', error);
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Partner Portal Authentication APIs
    if (url.pathname === '/api/partner/login' && request.method === 'POST') {
      return partnerLoginHandler(request, env);
    }

    // Simple test login for development
    if (url.pathname === '/api/partner/test-login' && request.method === 'POST') {
      return partnerTestLoginHandler(request, env);
    }

    if (url.pathname === '/api/partner/auth' && request.method === 'GET') {
      return partnerAuthCheckHandler(request, env);
    }

    if (url.pathname === '/api/partner/logout' && request.method === 'POST') {
      return partnerLogoutHandler(request, env);
    }

    // Partner Portal APIs (require authentication)
    if (url.pathname.startsWith('/api/partner/')) {
      const authResult = await validatePartnerAuth(request, env);
      if (!authResult.valid) {
        return new Response(JSON.stringify({ error: 'Authentication required' }), {
          status: 401,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }

      if (url.pathname === '/api/partner/profile' && request.method === 'GET') {
        return getPartnerProfileHandler(authResult.partner, env);
      }

      if (url.pathname === '/api/partner/projects' && request.method === 'GET') {
        return getPartnerProjectsHandler(authResult.partner, env);
      }

      if (url.pathname.startsWith('/api/partner/invitation/') && request.method === 'PUT') {
        const invitationId = url.pathname.split('/')[4];
        return updatePartnerInvitationHandler(authResult.partner, invitationId, request, env);
      }

      if (url.pathname === '/api/partner/upload-document' && request.method === 'POST') {
        return partnerUploadDocumentHandler(authResult.partner, request, env);
      }

      if (url.pathname.startsWith('/api/partner/document/') && url.pathname.endsWith('/replace') && request.method === 'POST') {
        const documentId = url.pathname.split('/')[4];
        return replacePartnerDocumentHandler(authResult.partner, documentId, request, env);
      }

      if (url.pathname.startsWith('/api/partner/document/') && url.pathname.endsWith('/delete') && request.method === 'DELETE') {
        const documentId = url.pathname.split('/')[4];
        return deletePartnerDocumentHandler(authResult.partner, documentId, env);
      }

      if (url.pathname.startsWith('/api/partner/document/') && url.pathname.endsWith('/versions') && request.method === 'GET') {
        const documentId = url.pathname.split('/')[4];
        return getDocumentVersionsHandler(authResult.partner, documentId, env);
      }

      if (url.pathname.startsWith('/api/partner/document/') && url.pathname.endsWith('/download') && request.method === 'GET') {
        const documentId = url.pathname.split('/')[4];
        return downloadPartnerDocumentHandler(authResult.partner, documentId, env);
      }

      if (url.pathname.startsWith('/api/partner/project/') && url.pathname.endsWith('/documents') && request.method === 'GET') {
        const projectId = url.pathname.split('/')[4];
        return getPartnerProjectDocumentsHandler(authResult.partner, projectId, env);
      }

      if (url.pathname.startsWith('/api/partner/project/') && url.pathname.endsWith('/sync-sharepoint') && request.method === 'POST') {
        const projectId = url.pathname.split('/')[4];
        return syncSharePointDocumentsHandler(authResult.partner, projectId, request, env);
      }

      if (url.pathname.startsWith('/api/partner/projects/') && request.method === 'GET') {
        const projectId = url.pathname.split('/')[4];
        return getPartnerProjectDetailHandler(authResult.partner, projectId, env);
      }
    }

    // For frontend routes (/apply, /form, /), return 404 so they can be handled by Pages
    // This allows the React frontend to handle these routes
    return new Response('Route not handled by Worker - should be handled by frontend', { 
      status: 404,
      headers: corsHeaders 
    });
  }
};

// Simple operations page - just shows links to applications
async function getOperationsPage(env) {
  const corsHeaders = getCorsHeaders(env);
  const html = `
<!DOCTYPE html>
<html>
<head>
    <title>EPC Operations</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen p-8">
    <div class="max-w-4xl mx-auto">
        <div class="flex items-center gap-3 mb-6">
          <img src="/images/Saber-mark-wob-green.svg" alt="Saber" class="h-8 w-auto"/>
          <h1 class="text-3xl font-bold">EPC Operations Dashboard</h1>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div class="rounded-lg bg-slate-800/80 ring-1 ring-white/10 p-4"><div class="text-slate-400 text-xs">New</div><div id="kpi-new" class="text-2xl font-semibold">-</div></div>
          <div class="rounded-lg bg-slate-800/80 ring-1 ring-white/10 p-4"><div class="text-slate-400 text-xs">In Review</div><div id="kpi-review" class="text-2xl font-semibold">-</div></div>
          <div class="rounded-lg bg-slate-800/80 ring-1 ring-white/10 p-4"><div class="text-slate-400 text-xs">Approved Partners</div><div id="kpi-approved" class="text-2xl font-semibold">-</div></div>
          <div class="rounded-lg bg-slate-800/80 ring-1 ring-white/10 p-4"><div class="text-slate-400 text-xs">Rejected</div><div id="kpi-rejected" class="text-2xl font-semibold">-</div></div>
        </div>

        <div class="bg-gray-800 rounded-lg p-6 mb-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold">Partner Hub</h2>
            <input id="partner-search" placeholder="Search partners" class="rounded-md bg-slate-700/40 px-3 py-2 text-sm ring-1 ring-slate-600/50" />
          </div>
          <div id="partners-grid" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
          <div id="partners-empty" class="text-gray-400 text-sm">No approved partners yet.</div>
        </div>

        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">Application Queue</h2>
            <div id="apps-list" class="space-y-3">
                <div class="text-gray-400">Loading applications...</div>
            </div>
        </div>
        
        <div class="text-sm text-gray-400">
            <p>This page shows applications submitted through the EPC Partner Portal.</p>
            <p>Data is read from D1 (Cloudflare) and files are stored in SharePoint.</p>
        </div>
    </div>

    <script>
        function computePhase(app, reviews) {
          const st = (app.status || '').toLowerCase();
          if (st === 'completed' || st === 'approved') return 'approved';
          if (!reviews) return st === 'submitted' ? 'new' : 'in_review';
          const vals = Object.values(reviews || {}).map(r => (r && r.status) || 'pending');
          if (vals.length && vals.every(v => v === 'approved')) return 'approved';
          if (vals.some(v => v === 'rejected')) return 'rejected';
          if (st === 'submitted') return 'new';
          return 'in_review';
        }

        function renderPartners(partners) {
          const grid = document.getElementById('partners-grid');
          const empty = document.getElementById('partners-empty');
          const q = (document.getElementById('partner-search').value || '').toLowerCase();
          const filtered = partners.filter(p => !q || (p.companyName||'').toLowerCase().includes(q) || (p.coverage||'').toLowerCase().includes(q));
          if (!filtered.length) { grid.innerHTML = ''; empty.style.display='block'; return; }
          empty.style.display='none';
          grid.innerHTML = filtered.map(p => {
            const regions = (function(){ try { var a = JSON.parse(p.coverageRegions||'[]'); return a.length?a.join(', '):''; } catch { return '' } })();
            var tags = [];
            if (p.mcsApproved) tags.push('MCS');
            if (p.niceicContractor) tags.push('NICEIC');
            if (p.principalContractor) tags.push('Principal Contractor');
            return '<div class="rounded-lg bg-slate-900/40 ring-1 ring-white/10 p-4">'
              + '<div class="flex items-center justify-between">'
              +   '<div class="flex items-center gap-3">'
              +     (p.logoUrl ? ('<img src="' + p.logoUrl + '" class="h-8 w-8 rounded-full object-cover ring-1 ring-white/10"/>') : '<img src="/images/Saber-mark-wob-green.svg" class="h-8 w-8"/>')
              +     '<div class="font-semibold">' + (p.companyName||'Unknown') + '</div>'
              +   '</div>'
              +   '<a class="text-sm text-blue-400" href="/operations/' + (p.invitationCode||p.id) + '">Open</a>'
              + '</div>'
              + '<div class="text-xs text-slate-400 mt-1">' + (p.coverage||'') + (regions? (' • ' + regions):'') + '</div>'
              + (tags.length? ('<div class="mt-2 flex flex-wrap gap-2">' + tags.map(function(t){return '<span class="text-xs px-2 py-0.5 rounded bg-slate-700/60">'+t+'</span>';}).join('') + '</div>'):'')
              + '</div>';
          }).join('');
        }

        async function loadApps() {
            try {
                const response = await fetch('/api/applications');
                const data = await response.json();
                
                const listEl = document.getElementById('apps-list');
                if (!(data.success && data.applications.length > 0)) {
                    listEl.innerHTML = '<div class="text-gray-400">No applications found</div>';
                    return;
                }

                var apps = data.applications;
                var reviewsMap = {};
                await Promise.all(apps.map(async function(a){
                  try {
                    var r = await fetch('/api/application/' + a.id + '/reviews');
                    var j = await r.json();
                    reviewsMap[a.id] = j.reviews || null;
                  } catch {}
                }));

                var phases = { new:0, in_review:0, approved:0, rejected:0 };
                var partners = [];
                apps.forEach(function(a){
                  var phase = computePhase(a, reviewsMap[a.id]);
                  phases[phase] = (phases[phase]||0)+1;
                  if (phase === 'approved') partners.push(a);
                });

                document.getElementById('kpi-new').textContent = phases.new || 0;
                document.getElementById('kpi-review').textContent = phases.in_review || 0;
                document.getElementById('kpi-approved').textContent = phases.approved || 0;
                document.getElementById('kpi-rejected').textContent = phases.rejected || 0;

                renderPartners(partners);
                document.getElementById('partner-search').addEventListener('input', function(){ renderPartners(partners); });

                listEl.innerHTML = apps.map(function(app){
                  var phase = computePhase(app, reviewsMap[app.id]);
                  var badge = phase === 'approved' ? 'bg-green-600' : (phase === 'rejected' ? 'bg-red-600' : (phase==='new'?'bg-slate-600':'bg-yellow-600'));
                  return '<div class="border border-gray-700 rounded p-4">'
                      + '<div class="flex items-center justify-between">'
                      +   '<h3 class="font-semibold">' + (app.companyName || 'Unknown Company') + '</h3>'
                      +   '<span class="text-xs px-2 py-0.5 rounded ' + badge + '">' + phase + '</span>'
                      + '</div>'
                      + '<p class="text-gray-400 text-sm">' + (app.email || 'No email') + ' • ' + (app.submittedAt || 'No date') + '</p>'
                      + '<p class="text-gray-300 text-xs">Invitation: ' + (app.invitationCode || 'N/A') + ' • App ID: ' + (app.id || 'N/A') + '</p>'
                      + '<a href="/operations/' + (app.invitationCode || app.id || '0') + '" '
                      +   'class="inline-block mt-2 bg-blue-600 hover:bg-blue-700 px-3 py-1 text-sm rounded">View Details</a>'
                    + '</div>';
                }).join('');
            } catch (error) {
                document.getElementById('apps-list').innerHTML = '<div class="text-red-400">Error loading applications</div>';
            }
        }
        
        loadApps();
        setInterval(loadApps, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>`;
  
  return new Response(html, {
    headers: { 'Content-Type': 'text/html', ...corsHeaders }
  });
}

// Operations detail page: show single application + files
async function getOperationDetailPage(ref, env) {
  const corsHeaders = getCorsHeaders(env);
  try {
    let row = null;
    if (/^[A-Za-z0-9]{8}$/.test(ref)) {
      row = await env.epc_form_data.prepare('SELECT * FROM applications WHERE invitation_code = ? ORDER BY id DESC LIMIT 1').bind(ref.toUpperCase()).first();
    }
    if (!row && /^\d+$/.test(ref)) {
      row = await env.epc_form_data.prepare('SELECT * FROM applications WHERE id = ?').bind(parseInt(ref)).first();
    }
    if (!row) {
      return new Response('<h1 style="font-family:sans-serif">Not Found</h1>', { status: 404, headers: { 'Content-Type': 'text/html', ...corsHeaders } });
    }
    const filesRes = await env.epc_form_data
      .prepare('SELECT id, field_name, original_filename, upload_url FROM application_files WHERE application_id = ? ORDER BY id DESC')
      .bind(row.id)
      .all();
    const files = filesRes.results || [];

    const spBase = 'https://saberrenewables.sharepoint.com';
    const fullLink = (u) => u && u.startsWith('/') ? spBase + u : u || '#';

    // Load reviews to determine overall approval
    let reviews = {};
    try {
      const r = await env.epc_form_data
        .prepare('SELECT section, status, reviewer, note FROM application_section_reviews WHERE application_id = ?')
        .bind(row.id)
        .all();
      (r.results || []).forEach(rec => { reviews[rec.section] = rec; });
    } catch {}
    const validSections = ['company','contact','services','roles','insurance','compliance','files'];
    const allApproved = validSections.length && validSections.every(s => reviews[s] && reviews[s].status === 'approved');

    const totalSections = validSections.length;
    const approvedCount = validSections.filter(s => reviews[s] && reviews[s].status === 'approved').length;
    const rejectedCount = validSections.filter(s => reviews[s] && reviews[s].status === 'rejected').length;
    const spFolderRoot = `/sites/SaberEPCPartners/Shared Documents/EPC Applications/${row.invitation_code || ''}`;

    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>EPC Application ${row.id}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style> a{ word-break: break-all } </style>
  </head>
<body class="bg-gray-900 text-white min-h-screen p-8">
  <div class="max-w-5xl mx-auto space-y-6">
    <!-- Header -->
    <div class="lg:flex lg:items-center lg:justify-between">
      <div class="min-w-0 flex-1">
        <nav aria-label="Breadcrumb" class="flex"><a href="/operations" class="text-sm text-slate-400 hover:text-slate-200">← Back</a></nav>
        ${(() => { const logoFile = files.find(f => (f.field_name||'').toLowerCase().includes('logo')); const logoUrl = logoFile ? fullLink(logoFile.upload_url) : '/images/Saber-mark-wob-green.svg'; return `
        <div class="mt-2 flex items-center gap-3">
          <img src="${logoUrl}" alt="Logo" class="h-10 w-10 rounded-full object-cover ring-1 ring-white/20 bg-white/10" />
          <div>
            <h1 class="text-2xl font-bold">${row.company_name || 'Application ' + row.id}</h1>
            <div class="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:space-x-6">
              <div class="text-sm text-slate-300">${row.contact_name || '—'}${row.email? ' • '+row.email:''}${row.phone? ' • '+row.phone:''}</div>
              <div class="text-xs text-slate-400">Invitation: ${row.invitation_code || '—'}</div>
            </div>
          </div>
        </div>` })()}
      </div>
      <div class="mt-5 flex lg:mt-0 lg:ml-4 gap-3">
        ${allApproved ? `<span class="inline-flex items-center rounded-md bg-green-700 px-3 py-2 text-sm font-semibold">APPROVED</span>` : `
        <button onclick="approveAll()" class="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white hover:bg-green-500">Approve all</button>`}
        <button onclick="openDelete()" class="inline-flex items-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white hover:bg-red-500">Delete</button>
      </div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-gray-800 rounded-lg p-5 ring-1 ring-white/10">
        <h2 class="text-lg font-semibold mb-3">Company & Contact</h2>
        <dl class="text-sm text-slate-300 space-y-2">
          <div class="flex justify-between"><dt>Invitation</dt><dd class="text-slate-100">${row.invitation_code || '—'}</dd></div>
          <div class="flex justify-between"><dt>Company</dt><dd class="text-slate-100">${row.company_name || '—'}</dd></div>
          <div class="flex justify-between"><dt>Contact</dt><dd class="text-slate-100">${row.contact_name || '—'}</dd></div>
          <div class="flex justify-between"><dt>Email</dt><dd class="text-slate-100">${row.email || '—'}</dd></div>
          <div class="flex justify-between"><dt>Status</dt><dd class="text-slate-100">${row.status || '—'}</dd></div>
          <div class="flex justify-between"><dt>Submitted</dt><dd class="text-slate-100">${row.submitted_at || row.created_at || '—'}</dd></div>
        </dl>
      </div>
      <div class="bg-gray-800 rounded-lg p-5 ring-1 ring-white/10">
        <h2 class="text-lg font-semibold mb-3">Coverage</h2>
        <p class="text-sm text-slate-300"><span class="text-slate-400">Summary:</span> ${row.coverage || '—'}</p>
        <p class="text-sm text-slate-300 mt-2"><span class="text-slate-400">Regions:</span> ${(() => { try { const a = JSON.parse(row.coverage_regions||'[]'); return a.length? a.join(', ') : '—'; } catch { return '—'; } })()}</p>
        ${row.coverage_region ? `<p class="text-sm text-slate-300 mt-2"><span class="text-slate-400">Other:</span> ${row.coverage_region}</p>` : ''}
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-slate-700 mt-2">
      <nav class="-mb-px flex gap-6" aria-label="Tabs">
        <button class="tab-btn px-1 py-3 text-sm font-medium text-slate-300 border-b-2 border-transparent hover:text-white" data-tab="overview">Overview</button>
        <button class="tab-btn px-1 py-3 text-sm font-medium text-slate-300 border-b-2 border-transparent hover:text-white" data-tab="company">Company</button>
        <button class="tab-btn px-1 py-3 text-sm font-medium text-slate-300 border-b-2 border-transparent hover:text-white" data-tab="files">Files</button>
        <button class="tab-btn px-1 py-3 text-sm font-medium text-slate-300 border-b-2 border-transparent hover:text-white" data-tab="reviews">Reviews</button>
        <button class="tab-btn px-1 py-3 text-sm font-medium text-slate-300 border-b-2 border-transparent hover:text-white" data-tab="notes">Notes</button>
      </nav>
    </div>

    <!-- Tab Panels -->
    <div id="tab-overview" class="tab-panel mt-4">
      <div class="bg-gray-800 rounded-lg p-5 ring-1 ring-white/10">
        <h2 class="text-lg font-semibold mb-3">Application Summary</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div><div class="text-slate-400 text-xs">Status</div><div class="text-slate-100">${row.status || '—'}</div></div>
          <div><div class="text-slate-400 text-xs">Submitted</div><div class="text-slate-100">${row.submitted_at || row.created_at || '—'}</div></div>
          <div><div class="text-slate-400 text-xs">Sections Approved</div><div class="text-slate-100">${approvedCount}/${totalSections}</div></div>
          <div><div class="text-slate-400 text-xs">Rejected</div><div class="text-slate-100">${rejectedCount}</div></div>
        </div>
        <div class="mt-4 text-sm"><a class="text-blue-400 hover:text-blue-300" target="_blank" href="${fullLink(spFolderRoot)}">Open SharePoint folder</a></div>
      </div>
    </div>

    <div id="tab-files" class="tab-panel hidden mt-4">
      <div class="bg-gray-800 rounded-lg p-5 ring-1 ring-white/10">
        <h2 class="text-lg font-semibold mb-3">Files</h2>
        ${files.length ? `<ul class="space-y-2">${files.map(f => `<li class="flex items-center justify-between">
          <span class="text-sm text-slate-300">${f.field_name} • ${f.original_filename}</span>
          <a class="text-sm text-blue-400 hover:text-blue-300" target="_blank" href="${fullLink(f.upload_url)}">Open</a>
        </li>`).join('')}</ul>` : '<p class="text-sm text-slate-400">No files recorded.</p>'}
      </div>
    </div>

    <div id="tab-company" class="tab-panel hidden mt-4">
      <div class="bg-gray-800 rounded-lg p-5 ring-1 ring-white/10">
        <h2 class="text-lg font-semibold mb-3">Company & Contact</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <dl class="text-sm text-slate-300 space-y-2">
            <div class="flex justify-between"><dt>Company</dt><dd class="text-slate-100">${row.company_name || '—'}</dd></div>
            <div class="flex justify-between"><dt>Trading name</dt><dd class="text-slate-100">${row.trading_name || '—'}</dd></div>
            <div class="flex justify-between"><dt>Registration No</dt><dd class="text-slate-100">${row.registration_number || '—'}</dd></div>
            <div class="flex justify-between"><dt>VAT No</dt><dd class="text-slate-100">${row.vat_number || '—'}</dd></div>
            <div class="flex justify-between"><dt>Years trading</dt><dd class="text-slate-100">${row.years_trading || '—'}</dd></div>
            <div class="flex justify-between"><dt>Registered address</dt><dd class="text-slate-100">${row.registered_address || '—'}</dd></div>
          </dl>
          <dl class="text-sm text-slate-300 space-y-2">
            <div class="flex justify-between"><dt>Contact</dt><dd class="text-slate-100">${row.contact_name || '—'}${row.contact_title? ' • '+row.contact_title : ''}</dd></div>
            <div class="flex justify-between"><dt>Email</dt><dd class="text-slate-100">${row.email || '—'}</dd></div>
            <div class="flex justify-between"><dt>Phone</dt><dd class="text-slate-100">${row.phone || '—'}</dd></div>
            <div class="flex justify-between"><dt>Website</dt><dd class="text-slate-100">${row.company_website ? ('<a class=\"text-blue-400\" href=\"'+row.company_website+'\" target=\"_blank\">'+row.company_website+'</a>') : '—'}</dd></div>
            <div class="flex justify-between"><dt>Specializations</dt><dd class="text-slate-100">${row.specializations || '—'}</dd></div>
            <div class="flex justify-between"><dt>Software</dt><dd class="text-slate-100">${row.software_tools || '—'}</dd></div>
          </dl>
        </div>
        <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <dl class="text-sm text-slate-300 space-y-2">
            <div class="flex justify-between"><dt>Projects / month</dt><dd class="text-slate-100">${row.projects_per_month || '—'}</dd></div>
            <div class="flex justify-between"><dt>Team size</dt><dd class="text-slate-100">${row.team_size || '—'}</dd></div>
          </dl>
          <dl class="text-sm text-slate-300 space-y-2">
            <div class="flex justify-between"><dt>Principal contractor</dt><dd class="text-slate-100">${row.principal_contractor ? 'Yes' : 'No'}</dd></div>
            <div class="flex justify-between"><dt>Principal designer</dt><dd class="text-slate-100">${row.principal_designer ? 'Yes' : 'No'}</dd></div>
          </dl>
          <dl class="text-sm text-slate-300 space-y-2">
            <div class="flex justify-between"><dt>MCS</dt><dd class="text-slate-100">${row.mcs_approved ? 'Yes' : 'No'}</dd></div>
            <div class="flex justify-between"><dt>NICEIC</dt><dd class="text-slate-100">${row.niceic_contractor ? 'Yes' : 'No'}</dd></div>
          </dl>
        </div>
        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <dl class="text-sm text-slate-300 space-y-2">
            <div class="flex justify-between"><dt>Public Liability</dt><dd class="text-slate-100">${row.public_liability_insurance ? 'Yes' : 'No'}${row.public_liability_expiry? ' • exp '+row.public_liability_expiry : ''}</dd></div>
            <div class="flex justify-between"><dt>Employers Liability</dt><dd class="text-slate-100">${row.employers_liability_insurance ? 'Yes' : 'No'}${row.employers_liability_expiry? ' • exp '+row.employers_liability_expiry : ''}</dd></div>
            <div class="flex justify-between"><dt>Prof. Indemnity</dt><dd class="text-slate-100">${row.professional_indemnity_insurance ? 'Yes' : 'No'}${row.professional_indemnity_expiry? ' • exp '+row.professional_indemnity_expiry : ''}</dd></div>
          </dl>
          <dl class="text-sm text-slate-300 space-y-2">
            <div class="flex justify-between"><dt>H&S Policy</dt><dd class="text-slate-100">${row.health_safety_policy_date || '—'}</dd></div>
            <div class="flex justify-between"><dt>Environmental Policy</dt><dd class="text-slate-100">${row.environmental_policy_date || '—'}</dd></div>
            <div class="flex justify-between"><dt>Modern Slavery Policy</dt><dd class="text-slate-100">${row.modern_slavery_policy_date || '—'}</dd></div>
            <div class="flex justify-between"><dt>Substance Misuse Policy</dt><dd class="text-slate-100">${row.substance_misuse_policy_date || '—'}</dd></div>
            <div class="flex justify-between"><dt>Right to Work</dt><dd class="text-slate-100">${row.right_to_work_method || '—'}</dd></div>
          </dl>
        </div>
      </div>
    </div>
    <div id="tab-reviews" class="tab-panel hidden mt-4">
      <div class="bg-gray-800 rounded-lg p-5 ring-1 ring-white/10">
        <h2 class="text-lg font-semibold mb-3">Section Reviews</h2>
        <div id="reviews" class="text-sm text-slate-300">Loading…</div>
        <div class="mt-4 flex items-center gap-3">
          <input id="reviewer" placeholder="Your name" class="w-48 rounded-md bg-slate-700/30 px-3 py-2 text-sm ring-1 ring-slate-600/50 text-white" />
          <input id="reviewNote" placeholder="Optional note" class="flex-1 rounded-md bg-slate-700/30 px-3 py-2 text-sm ring-1 ring-slate-600/50 text-white" />
        </div>
      </div>
    </div>

    <div id="tab-notes" class="tab-panel hidden mt-4">
      <div class="bg-gray-800 rounded-lg p-5 ring-1 ring-white/10">
        <h2 class="text-lg font-semibold mb-3">Operations Notes</h2>
        <div class="flex items-center gap-3">
          <input id="noteAuthor" placeholder="Your name" class="w-48 rounded-md bg-slate-700/30 px-3 py-2 text-sm ring-1 ring-slate-600/50 text-white" />
          <input id="noteText" placeholder="Add a note…" class="flex-1 rounded-md bg-slate-700/30 px-3 py-2 text-sm ring-1 ring-slate-600/50 text-white" />
          <button onclick="addNote()" class="px-3 py-2 bg-blue-600 rounded text-sm">Add</button>
        </div>
        <ul id="notes" class="mt-3 space-y-2 text-sm text-slate-300"></ul>
      </div>
    </div>

    <div class="text-xs text-slate-500">API: <a class="underline" href="/api/application/${row.id}" target="_blank">/api/application/${row.id}</a></div>
  </div>

  <!-- Delete modal -->
  <div id="delModal" class="fixed inset-0 z-50 hidden">
    <div class="absolute inset-0 bg-black/60" onclick="closeDelete()"></div>
    <div class="absolute inset-0 flex items-center justify-center p-6">
      <div class="w-full max-w-md rounded-lg bg-slate-800 ring-1 ring-white/10 p-6">
        <h3 class="text-lg font-semibold mb-2">Delete application</h3>
        <p class="text-sm text-slate-300">Are you sure you want to delete <b>${row.company_name || ('Application '+row.id)}</b>? This action cannot be undone.</p>
        <div class="mt-6 flex justify-end gap-3">
          <button class="px-4 py-2 rounded bg-slate-700 hover:bg-slate-600" onclick="closeDelete()">Cancel</button>
          <button class="px-4 py-2 rounded bg-red-600 hover:bg-red-500" onclick="confirmDelete()">Delete</button>
        </div>
      </div>
    </div>
  </div>
  <script>
    const appId = ${row.id};
    const sections = ${JSON.stringify(['company','contact','services','roles','insurance','compliance','files'])};
    const tabButtons = document.querySelectorAll('.tab-btn');
    const panels = { overview: document.getElementById('tab-overview'), company: document.getElementById('tab-company'), files: document.getElementById('tab-files'), reviews: document.getElementById('tab-reviews'), notes: document.getElementById('tab-notes') };
    function setTab(name){ Object.keys(panels).forEach(k=>{ panels[k].classList.toggle('hidden', k!==name); }); tabButtons.forEach(b=>{ const active = b.getAttribute('data-tab')===name; b.classList.toggle('border-indigo-500', active); b.classList.toggle('text-white', active); }); }
    tabButtons.forEach(b=> b.addEventListener('click', ()=> setTab(b.getAttribute('data-tab'))));
    setTab('overview');

    async function loadReviews() {
      const res = await fetch('/api/application/' + appId + '/reviews');
      const data = await res.json();
      const el = document.getElementById('reviews');
      if (!data.success) { el.textContent = 'Failed to load reviews'; return; }
      const map = data.reviews;
      el.innerHTML = sections.map(function(s){
        const st = (map[s] && map[s].status) || 'pending';
        const badge = st === 'approved' ? 'bg-green-600' : (st === 'rejected' ? 'bg-red-600' : 'bg-slate-600');
        return '<div class="flex items-center justify-between border-b border-slate-700/50 py-2">'
          + '<div class="flex items-center gap-3">'
          +   '<span class="inline-block px-2 py-0.5 rounded text-xs ' + badge + '">' + st + '</span>'
          +   '<span class="text-slate-200 capitalize">' + s + '</span>'
          + '</div>'
          + '<div class="flex items-center gap-2">'
          +   '<button onclick="review(\\'' + s + '\\',\\'approved\\')" class="px-2 py-1 bg-green-600 rounded text-xs">Approve</button>'
          +   '<button onclick="review(\\'' + s + '\\',\\'rejected\\')" class="px-2 py-1 bg-red-600 rounded text-xs">Reject</button>'
          + '</div>'
          + '</div>';
      }).join('');
    }

    async function approveAll() {
      const reviewer = document.getElementById('reviewer')?.value || '';
      const note = 'Bulk approved';
      await fetch('/api/application/' + appId + '/approve-all', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer, note })
      });
      location.reload();
    }

    function openDelete(){ document.getElementById('delModal').classList.remove('hidden'); }
    function closeDelete(){ document.getElementById('delModal').classList.add('hidden'); }
    async function confirmDelete(){
      const res = await fetch('/api/application/' + appId + '/delete', { method: 'POST' });
      if (res.ok) { window.location.href = '/operations'; }
      else { alert('Failed to delete'); closeDelete(); }
    }

    async function review(section, status) {
      const reviewer = document.getElementById('reviewer').value;
      const note = document.getElementById('reviewNote').value;
      await fetch('/api/application/' + appId + '/review', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ section, status, reviewer, note })
      });
      document.getElementById('reviewNote').value='';
      await loadReviews();
    }

    async function loadNotes() {
      const res = await fetch('/api/application/' + appId + '/notes');
      const data = await res.json();
      const el = document.getElementById('notes');
      if (!data.success) { el.innerHTML = '<li>Failed to load notes</li>'; return; }
      el.innerHTML = (data.notes || []).map(function(n){
        return '<li class="flex items-start justify-between">'
          + '<span class="text-slate-300">' + (n.author ? ('<b>' + n.author + ':</b> ') : '') + n.note + '</span>'
          + '<span class="text-slate-500 text-xs">' + n.created_at + '</span>'
          + '</li>';
      }).join('');
    }

    async function addNote() {
      const author = document.getElementById('noteAuthor').value;
      const note = document.getElementById('noteText').value;
      if (!note.trim()) return;
      await fetch('/api/application/' + appId + '/note', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author, note })
      });
      document.getElementById('noteText').value='';
      await loadNotes();
    }

    loadReviews();
    loadNotes();
  </script>
</body>
</html>`;

    return new Response(html, { headers: { 'Content-Type': 'text/html', ...corsHeaders } });
  } catch (e) {
    return new Response('Error rendering page', { status: 500, headers: { 'Content-Type': 'text/plain', ...corsHeaders } });
  }
}

async function migrateFilesEndpoint(request, env, ctx) {
  try {
    const body = await request.json();
    const code = (body.invitationCode || body.code || '').toString().toUpperCase();
    if (!code || code.length !== 8) {
      return new Response(JSON.stringify({ success: false, message: 'invitationCode (8 chars) required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    let appRow = await env.epc_form_data
      .prepare('SELECT id, status FROM applications WHERE invitation_code = ? ORDER BY id DESC LIMIT 1')
      .bind(code)
      .first();

    if (!appRow) {
      await env.epc_form_data
        .prepare("INSERT INTO applications (invitation_code, status, submitted_at) VALUES (?, 'submitted', CURRENT_TIMESTAMP)")
        .bind(code)
        .run();
      appRow = await env.epc_form_data
        .prepare('SELECT id, status FROM applications WHERE invitation_code = ? ORDER BY id DESC LIMIT 1')
        .bind(code)
        .first();
    }

    ctx.waitUntil(migrateDraftFilesToSharePoint(code, appRow.id, env));

    return new Response(JSON.stringify({ success: true, message: 'Migration scheduled', applicationId: appRow.id }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (e) {
    return new Response(JSON.stringify({ success: false, error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

async function statusEndpoint(request, env) {
  try {
    const url = new URL(request.url);
    const code = (url.searchParams.get('invitationCode') || '').toUpperCase();
    if (!code || code.length !== 8) {
      return new Response(JSON.stringify({ success: false, message: 'invitationCode query param (8 chars) required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    const app = await env.epc_form_data
      .prepare('SELECT id, invitation_code, status, submitted_at, updated_at FROM applications WHERE invitation_code = ? ORDER BY id DESC LIMIT 1')
      .bind(code)
      .first();

    let draftCount = 0;
    let drafts = [];
    try {
      const res = await env.epc_form_data
        .prepare('SELECT id, field_name, r2_key, original_filename FROM draft_files WHERE invitation_code = ?')
        .bind(code)
        .all();
      drafts = res.results || [];
      draftCount = drafts.length;
    } catch {}

    let files = [];
    if (app?.id) {
      try {
        const res2 = await env.epc_form_data
          .prepare('SELECT id, field_name, original_filename, upload_url FROM application_files WHERE application_id = ? ORDER BY id DESC')
          .bind(app.id)
          .all();
        files = res2.results || [];
      } catch {}
    }

    return new Response(JSON.stringify({ success: true, invitationCode: code, application: app || null, draftCount, drafts, files }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (e) {
    return new Response(JSON.stringify({ success: false, error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

const VALID_SECTIONS = ['company','contact','services','roles','insurance','compliance','files'];

async function getReviews(appId, env) {
  try {
    const res = await env.epc_form_data
      .prepare('SELECT section, status, reviewer, note, updated_at FROM application_section_reviews WHERE application_id = ?')
      .bind(appId)
      .all();
    const map = Object.fromEntries(VALID_SECTIONS.map(s => [s, { status: 'pending' }]));
    (res.results || []).forEach(r => { map[r.section] = r; });
    return new Response(JSON.stringify({ success: true, reviews: map }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

async function postReview(appId, request, env, ctx) {
  try {
    const body = await request.json();
    const section = String(body.section || '').toLowerCase();
    const status = String(body.status || '').toLowerCase();
    const reviewer = body.reviewer || null;
    const note = body.note || null;
    if (!VALID_SECTIONS.includes(section)) {
      return new Response(JSON.stringify({ success: false, message: 'Invalid section' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }
    if (!['approved','rejected','pending'].includes(status)) {
      return new Response(JSON.stringify({ success: false, message: 'Invalid status' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }
    await env.epc_form_data.prepare(`
      INSERT INTO application_section_reviews (application_id, section, status, reviewer, note, updated_at)
      VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT(application_id, section) DO UPDATE SET
        status=excluded.status,
        reviewer=excluded.reviewer,
        note=excluded.note,
        updated_at=CURRENT_TIMESTAMP
    `).bind(appId, section, status, reviewer, note).run();

    // Fetch app row for notifications
    const appRow = await env.epc_form_data.prepare('SELECT * FROM applications WHERE id = ?').bind(appId).first();
    if (appRow) ctx.waitUntil(sendReviewNotification(appRow, section, status, note, env));

    return new Response(JSON.stringify({ success: true }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    console.error('postReview error:', e);
    return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

async function getNotes(appId, env) {
  try {
    const res = await env.epc_form_data
      .prepare('SELECT id, author, note, created_at FROM application_notes WHERE application_id = ? ORDER BY id DESC')
      .bind(appId)
      .all();
    return new Response(JSON.stringify({ success: true, notes: res.results || [] }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

async function postNote(appId, request, env) {
  try {
    const body = await request.json();
    const author = body.author || null;
    const note = body.note || '';
    if (!note.trim()) return new Response(JSON.stringify({ success: false, message: 'note required' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    await env.epc_form_data.prepare('INSERT INTO application_notes (application_id, author, note) VALUES (?, ?, ?)').bind(appId, author, note).run();
    return new Response(JSON.stringify({ success: true }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

async function approveAllHandler(appId, request, env, ctx) {
  try {
    const body = await request.json().catch(() => ({}));
    const reviewer = body.reviewer || 'Ops';
    const note = body.note || 'Bulk approved';
    const sections = ['company','contact','services','roles','insurance','compliance','files'];
    for (const s of sections) {
      await env.epc_form_data.prepare(`
        INSERT INTO application_section_reviews (application_id, section, status, reviewer, note, updated_at)
        VALUES (?, ?, 'approved', ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(application_id, section) DO UPDATE SET
          status='approved', reviewer=excluded.reviewer, note=excluded.note, updated_at=CURRENT_TIMESTAMP
      `).bind(appId, s, reviewer, note).run();
    }
    // Optionally mark application completed
    await env.epc_form_data.prepare('UPDATE applications SET status = \"completed\" WHERE id = ?').bind(appId).run();
    // Notify
    const appRow = await env.epc_form_data.prepare('SELECT * FROM applications WHERE id = ?').bind(appId).first();
    if (appRow) await sendReviewNotification(appRow, 'all', 'approved', note, env);
    return new Response(JSON.stringify({ success: true }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    console.error('approveAll error:', e);
    return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

async function deleteApplicationHandler(appId, env, ctx) {
  try {
    const appRow = await env.epc_form_data.prepare('SELECT * FROM applications WHERE id = ?').bind(appId).first();
    if (!appRow) return new Response(JSON.stringify({ success:false, message:'Not found' }), { status:404, headers:{ 'Content-Type':'application/json', ...corsHeaders } });
    await env.epc_form_data.prepare('DELETE FROM applications WHERE id = ?').bind(appId).run();
    // Notify
    await sendReviewNotification(appRow, 'all', 'deleted', 'Application deleted', env);
    return new Response(JSON.stringify({ success:true }), { headers:{ 'Content-Type':'application/json', ...corsHeaders } });
  } catch (e) {
    console.error('deleteApplication error:', e);
    return new Response(JSON.stringify({ success:false, error:e.message }), { status:500, headers:{ 'Content-Type':'application/json', ...corsHeaders } });
  }
}

// Save draft data (UPSERT)
async function saveDraftHandler(request, env) {
  try {
    const body = await request.json();
    const code = (body.invitationCode || '').toUpperCase();
    const formData = body.formData || {};
    const currentStep = body.currentStep || 1;
    if (!code || code.length !== 8) {
      return new Response(JSON.stringify({ success: false, message: 'invitationCode (8 chars) required' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }
    await env.epc_form_data.prepare(`
      INSERT INTO draft_data (invitation_code, form_data, current_step, last_saved)
      VALUES (?, ?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT(invitation_code) DO UPDATE SET
        form_data = excluded.form_data,
        current_step = excluded.current_step,
        last_saved = CURRENT_TIMESTAMP
    `).bind(code, JSON.stringify(formData), currentStep).run();

    return new Response(JSON.stringify({ success: true, lastSaved: new Date().toISOString() }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    console.error('saveDraft error:', e);
    return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

// Load draft data by invitation code
async function loadDraftHandler(request, env) {
  try {
    const url = new URL(request.url);
    const code = (url.searchParams.get('invitationCode') || '').toUpperCase();
    if (!code || code.length !== 8) {
      return new Response(JSON.stringify({ success: false, message: 'invitationCode (8 chars) required' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }
    const row = await env.epc_form_data.prepare('SELECT form_data, current_step, last_saved FROM draft_data WHERE invitation_code = ?').bind(code).first();
    if (!row) return new Response(JSON.stringify({ success: true, data: null }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    let formData;
    try { formData = JSON.parse(row.form_data); } catch { formData = {}; }
    return new Response(JSON.stringify({ success: true, data: { formData, currentStep: row.current_step, lastSaved: row.last_saved } }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    console.error('loadDraft error:', e);
    return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

// Clear draft by invitation code
async function clearDraftHandler(request, env) {
  try {
    const body = await request.json();
    const code = (body.invitationCode || '').toUpperCase();
    if (!code || code.length !== 8) {
      return new Response(JSON.stringify({ success: false, message: 'invitationCode (8 chars) required' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }
    await env.epc_form_data.prepare('DELETE FROM draft_data WHERE invitation_code = ?').bind(code).run();
    return new Response(JSON.stringify({ success: true }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    console.error('clearDraft error:', e);
    return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

// Handle form submission - store in Redis and send to SharePoint
async function handleSubmit(request, env) {
  try {
    const formData = await request.json();
    
    // Generate reference number
    const refNum = 'EPC' + Date.now();
    
    // Add metadata
    const applicationData = {
      ...formData,
      referenceNumber: refNum,
      submittedAt: new Date().toISOString(),
      status: 'pending'
    };

    // Store in Redis
    await storeInRedis(env, refNum, applicationData);
    
    // TODO: Send to SharePoint (lightweight notification only)
    
    return new Response(JSON.stringify({
      success: true,
      referenceNumber: refNum,
      message: 'Application submitted successfully'
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
    
  } catch (error) {
    console.error('Submit error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Failed to submit application'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

// Handle file upload during draft: store in R2 and record in D1; do NOT upload to SharePoint yet
async function handleFileUploadToR2(request, env) {
  try {
    const contentType = request.headers.get('content-type') || '';

    let invitationCode, fieldName, fileName, bytes, mimeType, size;

    if (contentType.includes('multipart/form-data')) {
      const form = await request.formData();
      const file = form.get('file');
      invitationCode = (form.get('invitationCode') || '').toString();
      fieldName = (form.get('fieldName') || '').toString();

      if (!file || !invitationCode || !fieldName) {
        return new Response(JSON.stringify({ success: false, message: 'file, invitationCode, and fieldName are required' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }

      fileName = file.name;
      mimeType = file.type || 'application/octet-stream';
      size = file.size || undefined;
      bytes = await file.arrayBuffer();
    } else {
      // Legacy JSON format: { invitationCode, fieldName, fileName, contentType, fileContent (base64) }
      const body = await request.json();
      invitationCode = body.invitationCode || body.code;
      fieldName = body.fieldName;
      fileName = body.fileName;
      mimeType = body.contentType || 'application/octet-stream';
      const b64 = body.fileContent;
      if (!invitationCode || !fieldName || !fileName || !b64) {
        return new Response(JSON.stringify({ success: false, message: 'invitationCode, fieldName, fileName, fileContent required' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
      const binary = atob(b64);
      const arr = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) arr[i] = binary.charCodeAt(i);
      bytes = arr.buffer;
      size = arr.byteLength;
    }

    const clean = (s) => (s || '').toString().replace(/[^a-zA-Z0-9_.-]/g, '_');
    const ts = new Date().toISOString().split('T')[0];
    let subfolder = 'documents';
    const f = (fieldName || '').toLowerCase();
    if (f.includes('logo') || f.includes('image')) subfolder = 'logos';
    else if (f.includes('certificate') || f.includes('cert')) subfolder = 'certificates';
    else if (f.includes('financial') || f.includes('insurance')) subfolder = 'financial';

    const r2Key = `draft/EPC-Applications/${clean(invitationCode)}/${subfolder}/${ts}_${clean(fieldName)}_${clean(fileName)}`;

    // Put into R2
    await env.EPC_PARTNER_FILES.put(r2Key, bytes, {
      httpMetadata: { contentType: mimeType },
    });

    // Record in D1 draft_files
    try {
      await env.epc_form_data.prepare(`
        INSERT INTO draft_files (invitation_code, field_name, r2_key, original_filename, content_type, file_size)
        VALUES (?, ?, ?, ?, ?, ?)
      `).bind(
        invitationCode,
        fieldName,
        r2Key,
        fileName,
        mimeType,
        size || null
      ).run();
    } catch (e) {
      console.warn('⚠️ Failed to record draft file in D1:', e);
    }

    return new Response(JSON.stringify({
      success: true,
      message: 'File stored in portal storage (R2) for draft',
      r2Key,
      uploadedAt: new Date().toISOString()
    }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });

  } catch (error) {
    console.error('💥 Draft file upload error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Failed to upload file: ' + error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}
// Get all applications from D1 (recent first)
async function getApplicationsD1(env) {
  try {
    const res = await env.epc_form_data
      .prepare(`SELECT id, invitation_code, company_name, email, status, submitted_at, created_at,
                       coverage, coverage_regions, coverage_region,
                       principal_contractor, principal_designer, mcs_approved, niceic_contractor,
                       partner_logo_url
                FROM applications
                ORDER BY COALESCE(submitted_at, created_at) DESC
                LIMIT 50`)
      .all();
    const rows = res.results || [];
    const applications = rows.map(r => ({
      id: r.id,
      invitationCode: r.invitation_code,
      companyName: r.company_name,
      email: r.email,
      status: r.status,
      submittedAt: r.submitted_at || r.created_at,
      coverage: r.coverage,
      coverageRegions: r.coverage_regions,
      coverageRegion: r.coverage_region,
      principalContractor: r.principal_contractor,
      principalDesigner: r.principal_designer,
      mcsApproved: r.mcs_approved,
      niceicContractor: r.niceic_contractor,
      logoUrl: r.partner_logo_url
    }));
    return new Response(JSON.stringify({ success: true, applications }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    console.error('Get applications (D1) error:', e);
    return new Response(JSON.stringify({ success: false, applications: [] }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

// Get single application from D1 by id (with files)
async function getApplicationD1(env, id) {
  try {
    const row = await env.epc_form_data
      .prepare('SELECT * FROM applications WHERE id = ?')
      .bind(parseInt(id))
      .first();
    if (!row) {
      return new Response(JSON.stringify({ success: false, error: 'Application not found' }), { status: 404, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }
    const filesRes = await env.epc_form_data
      .prepare('SELECT id, field_name, original_filename, upload_url FROM application_files WHERE application_id = ? ORDER BY id DESC')
      .bind(row.id)
      .all();
    const files = filesRes.results || [];
    return new Response(JSON.stringify({ success: true, application: row, files }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    console.error('Get application (D1) error:', e);
    return new Response(JSON.stringify({ success: false, error: 'Failed to retrieve application' }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

// JSON API wrapper that accepts id or invitation code
async function getApplicationAPI(env, idOrCode) {
  try {
    let row = null;
    if (/^[A-Za-z0-9]{8}$/.test(idOrCode)) {
      row = await env.epc_form_data.prepare('SELECT * FROM applications WHERE invitation_code = ? ORDER BY id DESC LIMIT 1').bind(idOrCode.toUpperCase()).first();
    }
    if (!row && /^\d+$/.test(idOrCode)) {
      row = await env.epc_form_data.prepare('SELECT * FROM applications WHERE id = ?').bind(parseInt(idOrCode)).first();
    }
    if (!row) return new Response(JSON.stringify({ success: false, error: 'Application not found' }), { status: 404, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    const filesRes = await env.epc_form_data.prepare('SELECT id, field_name, original_filename, upload_url FROM application_files WHERE application_id = ? ORDER BY id DESC').bind(row.id).all();
    return new Response(JSON.stringify({ success: true, application: row, files: filesRes.results || [] }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  } catch (e) {
    console.error('getApplicationAPI error:', e);
    return new Response(JSON.stringify({ success: false, error: 'Failed to retrieve application' }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } });
  }
}

// Handle file upload to SharePoint and store metadata in Redis
async function handleFileUpload(request, env) {
  try {
    const uploadData = await request.json();
    
    // Log the file upload attempt
    console.log(`📁 Processing file upload: ${uploadData.fileName}`);
    console.log(`📍 Folder: ${uploadData.folderPath}`);
    
    // SharePoint configuration
    const sharePointConfig = {
      siteUrl: 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners',
      clientId: 'bbbfe394-7cff-4ac9-9e01-33cbf116b930',
      tenant: 'saberrenewables.onmicrosoft.com'
    };
    
    // Upload to SharePoint
    const sharePointResult = await uploadToSharePoint(uploadData, sharePointConfig, env);
    
    if (!sharePointResult.success) {
      console.error('❌ SharePoint upload failed:', sharePointResult.error);
      
      // Still store in Redis for backup
      const redis = await connectRedis(env.REDIS_URL);
      const fileKey = `epc:${uploadData.invitationCode}:file:${uploadData.fieldName}`;
      await redis.set(fileKey, JSON.stringify({
        ...uploadData.metadata,
        fileName: uploadData.fileName,
        fieldName: uploadData.fieldName,
        folderPath: uploadData.folderPath,
        contentType: uploadData.contentType,
        fileContent: uploadData.fileContent, // Store base64 content as backup
        status: 'sharepoint_failed',
        error: sharePointResult.error
      }));
      await redis.quit();
      
      return new Response(JSON.stringify({
        success: false,
        error: 'SharePoint upload failed: ' + sharePointResult.error,
        backup: 'File stored in Redis for recovery'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }
    
    // Store successful upload metadata in Redis
    const fileMetadata = {
      fileName: uploadData.fileName,
      originalName: uploadData.metadata.originalName,
      size: uploadData.metadata.size,
      uploadedAt: uploadData.metadata.uploadedAt,
      fieldName: uploadData.fieldName,
      folderPath: uploadData.folderPath,
      contentType: uploadData.contentType,
      sharePointUrl: sharePointResult.fileUrl,
      sharePointId: sharePointResult.sharePointId,
      status: 'uploaded_to_sharepoint'
    };
    
    const redis = await connectRedis(env.REDIS_URL);
    const fileKey = `epc:${uploadData.invitationCode}:file:${uploadData.fieldName}`;
    await redis.set(fileKey, JSON.stringify(fileMetadata));
    await redis.quit();
    
    console.log(`✅ File uploaded to SharePoint and metadata stored in Redis`);
    
    return new Response(JSON.stringify({
      success: true,
      message: 'File uploaded successfully to SharePoint',
      fileUrl: sharePointResult.fileUrl,
      sharePointId: sharePointResult.sharePointId
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
    
  } catch (error) {
    console.error('💥 File upload error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Failed to process file upload: ' + error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

// Upload file to SharePoint
async function uploadToSharePoint(uploadData, config, env) {
  try {
    // Get access token for SharePoint
    const accessToken = await getSharePointAccessToken(config, env);
    
    if (!accessToken) {
      return { success: false, error: 'Failed to get SharePoint access token' };
    }
    
    // Create folder if it doesn't exist
    await createSharePointFolder(uploadData.folderPath, config, accessToken);
    
    // Upload file - properly encode the URL with spaces
    const folderPath = `/sites/SaberEPCPartners/Shared%20Documents/${uploadData.folderPath}`;
    const uploadUrl = `${config.siteUrl}/_api/web/GetFolderByServerRelativeUrl('${folderPath}')/Files/Add(url='${encodeURIComponent(uploadData.fileName)}',overwrite=true)`;
    
    const fileBuffer = Buffer.from(uploadData.fileContent, 'base64');
    
    const uploadResponse = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/json;odata=verbose',
        'Content-Type': uploadData.contentType,
        'Content-Length': fileBuffer.length.toString()
      },
      body: fileBuffer
    });
    
    if (!uploadResponse.ok) {
      const errorText = await uploadResponse.text();
      console.error('SharePoint upload error:', uploadResponse.status, errorText);
      return { success: false, error: `Upload failed: ${uploadResponse.status} ${errorText}` };
    }
    
    const result = await uploadResponse.json();
    
    return {
      success: true,
      fileUrl: result.d.ServerRelativeUrl,
      sharePointId: result.d.UniqueId
    };
    
  } catch (error) {
    console.error('SharePoint upload error:', error);
    return { success: false, error: error.message };
  }
}

// Get SharePoint access token
async function getSharePointAccessToken(config, env) {
  try {
    // Use client credentials flow for SharePoint (prefers certificate auth if configured)
    const tokenUrl = `https://login.microsoftonline.com/${env.SHAREPOINT_TENANT}/oauth2/v2.0/token`;
    const resourceHost = `${config.tenant.replace('.onmicrosoft.com', '')}.sharepoint.com`;
    const scope = `https://${resourceHost}/.default`;

    // 1) Certificate-based auth (preferred)
    if (env.SP_CERT_PRIVATE_KEY) {
      try {
        const clientId = env.SHAREPOINT_CLIENT_ID;
        const now = Math.floor(Date.now() / 1000);
        // Build JWT header with cert identifiers
        const header = { alg: 'RS256', typ: 'JWT' };
        // Prefer computing x5t/x5t#S256 from the provided PEM cert (SP_CERT_X5C)
        try {
          if (env.SP_CERT_X5C) {
            const der = certPemToDer(env.SP_CERT_X5C);
            const x5tSha1 = await sha1Base64Url(der);
            header['x5t'] = x5tSha1;
            const x5tS256 = await sha256Base64Url(der);
            header['x5t#S256'] = x5tS256;
          }
        } catch (e) {
          console.warn('Failed to compute x5t/x5t#S256 from PEM, falling back to provided thumbprint:', e);
          if (env.SP_CERT_THUMBPRINT) header['x5t'] = env.SP_CERT_THUMBPRINT;
        }
        if (!header['x5t'] && env.SP_CERT_THUMBPRINT) header['x5t'] = env.SP_CERT_THUMBPRINT;
        if (env.SP_CERT_KID) header['kid'] = env.SP_CERT_KID;
        const claims = {
          iss: clientId,
          sub: clientId,
          aud: tokenUrl,
          jti: crypto.randomUUID(),
          nbf: now - 5,
          exp: now + 10 * 60
        };

        // Add x5c chain if provided (PEM). When set, Azure can identify the cert more reliably
        if (env.SP_CERT_X5C) {
          try {
            const x5cEntry = pemToBase64Der(env.SP_CERT_X5C);
            if (x5cEntry) header.x5c = [x5cEntry];
          } catch (e) {
            console.warn('Failed to add x5c header:', e);
          }
        }

        const clientAssertion = await signJwtWithPem(header, claims, env.SP_CERT_PRIVATE_KEY);

        const certParams = new URLSearchParams();
        certParams.append('grant_type', 'client_credentials');
        certParams.append('client_id', clientId);
        certParams.append('scope', scope);
        certParams.append('client_assertion_type', 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer');
        certParams.append('client_assertion', clientAssertion);

        const resp = await fetch(tokenUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: certParams
        });
        if (!resp.ok) {
          const t = await resp.text();
          console.error('Token request (cert) failed:', resp.status, t);
        } else {
          const data = await resp.json();
          console.log('✅ SharePoint access token obtained via certificate');
          return data.access_token;
        }
      } catch (e) {
        console.error('Certificate-based token retrieval failed, will try client secret if available:', e);
      }
    }

    // 2) Client secret fallback
    if (!env.SHAREPOINT_CLIENT_SECRET) {
      console.log('⚠️  SharePoint client secret not configured');
      return null;
    }
    const params = new URLSearchParams();
    params.append('grant_type', 'client_credentials');
    params.append('client_id', env.SHAREPOINT_CLIENT_ID);
    params.append('client_secret', env.SHAREPOINT_CLIENT_SECRET);
    params.append('scope', scope);

    const response = await fetch(tokenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params
    });
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Token request (secret) failed:', response.status, errorText);
      return null;
    }
    const tokenData = await response.json();
    console.log('✅ SharePoint access token obtained via client secret');
    return tokenData.access_token;
  
  } catch (error) {
    console.error('Failed to get SharePoint access token:', error);
    return null;
  }
}

function base64UrlEncode(input) {
  return btoa(String.fromCharCode(...new Uint8Array(input)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');
}

async function signJwtWithPem(header, payload, pemPrivateKey) {
  const enc = new TextEncoder();
  const headerStr = btoa(JSON.stringify(header))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');
  const payloadStr = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');
  const data = `${headerStr}.${payloadStr}`;

  const pkcs8 = pemToArrayBuffer(pemPrivateKey);
  const key = await crypto.subtle.importKey(
    'pkcs8',
    pkcs8,
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const signature = await crypto.subtle.sign(
    'RSASSA-PKCS1-v1_5',
    key,
    enc.encode(data)
  );
  const sigStr = base64UrlEncode(signature);
  return `${data}.${sigStr}`;
}

function pemToArrayBuffer(pem) {
  const b64 = pem.replace(/-----BEGIN PRIVATE KEY-----/g, '')
    .replace(/-----END PRIVATE KEY-----/g, '')
    .replace(/\s+/g, '');
  const raw = atob(b64);
  const arr = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
  return arr.buffer;
}

function pemToBase64Der(pemCert) {
  // Accept either full PEM or just the base64 content
  const b64 = pemCert.includes('BEGIN CERTIFICATE') ? pemCert.replace(/-----BEGIN CERTIFICATE-----/g, '')
    .replace(/-----END CERTIFICATE-----/g, '')
    .replace(/\s+/g, '') : pemCert.trim();
  return b64;
}

function certPemToDer(pemCert) {
  const b64 = pemToBase64Der(pemCert);
  const raw = atob(b64);
  const arr = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
  return arr.buffer;
}

async function sha1Base64Url(arrayBuffer) {
  const digest = await crypto.subtle.digest('SHA-1', arrayBuffer);
  return base64UrlEncode(digest);
}

async function sha256Base64Url(arrayBuffer) {
  const digest = await crypto.subtle.digest('SHA-256', arrayBuffer);
  return base64UrlEncode(digest);
}

// Create SharePoint folder if it doesn't exist
async function createSharePointFolder(folderPath, config, accessToken) {
  // Create a single folder (no parents). Expects path relative to "Shared Documents".
  try {
    const folderUrl = `${config.siteUrl}/_api/web/folders`;
    const serverRelative = `/sites/SaberEPCPartners/Shared%20Documents/${folderPath}`;

    const resp = await fetch(folderUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/json;odata=verbose'
      },
      body: JSON.stringify({ '__metadata': { 'type': 'SP.Folder' }, 'ServerRelativeUrl': serverRelative })
    });
    if (!resp.ok) {
      const text = await resp.text();
      if (resp.status === 409 || text.includes('already exists')) return true;
      console.warn('⚠️ Failed to create folder:', folderPath, resp.status, text);
      return false;
    }
    return true;
  } catch (e) {
    console.error('Failed to create SharePoint folder:', e);
    return false;
  }
}

async function ensureSharePointFolderPath(fullPathRelativeToSharedDocs, config, accessToken) {
  // Create each segment one-by-one. Accepts either encoded or unencoded.
  const decode = (s) => decodeURIComponent(s);
  const parts = fullPathRelativeToSharedDocs.split('/').filter(Boolean);
  let current = '';
  for (const part of parts) {
    if (current) current += '/';
    current += encodeURIComponent(decode(part));
    const ok = await createSharePointFolder(current, config, accessToken);
    if (!ok) return false;
  }
  return true;
}

// Upload a buffer (ArrayBuffer) to SharePoint
async function uploadBufferToSharePoint(folderPath, fileName, contentType, bytes, config, accessToken) {
  const encodedFolder = `/sites/SaberEPCPartners/Shared%20Documents/${folderPath}`;
  const uploadUrl = `${config.siteUrl}/_api/web/GetFolderByServerRelativeUrl('${encodedFolder}')/Files/Add(url='${encodeURIComponent(fileName)}',overwrite=true)`;
  const resp = await fetch(uploadUrl, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Accept': 'application/json;odata=verbose',
      'Content-Type': contentType || 'application/octet-stream'
    },
    body: bytes
  });
  if (!resp.ok) {
    const t = await resp.text();
    return { success: false, error: `Upload failed: ${resp.status} ${t}` };
  }
  const result = await resp.json();
  return {
    success: true,
    fileUrl: result.d.ServerRelativeUrl,
    sharePointId: result.d.UniqueId
  };
}

// Store application in Redis
async function storeInRedis(env, referenceNumber, data) {
  const redis = await connectRedis(env.REDIS_URL);
  await redis.set('epc:' + referenceNumber, JSON.stringify(data));
  await redis.quit();
}

// Connect to Redis
async function connectRedis(redisUrl) {
  const url = new URL(redisUrl);
  const socket = connect({
    hostname: url.hostname,
    port: parseInt(url.port) || 6379,
  });

  const writer = socket.writable.getWriter();
  const reader = socket.readable.getReader();

  // Authenticate if password provided
  if (url.password) {
    const authCmd = `AUTH ${url.username || 'default'} ${url.password}\r\n`;
    await writer.write(new TextEncoder().encode(authCmd));
    
    const authResponse = await reader.read();
    const authResult = new TextDecoder().decode(authResponse.value);
    if (!authResult.includes('+OK')) {
      throw new Error('Redis authentication failed');
    }
  }

  return {
    async get(key) {
      const cmd = `GET ${key}\r\n`;
      await writer.write(new TextEncoder().encode(cmd));
      
      const response = await reader.read();
      const result = new TextDecoder().decode(response.value);
      
      if (result.startsWith('$-1')) return null;
      if (result.startsWith('$')) {
        const lines = result.split('\r\n');
        return lines[1] || null;
      }
      return null;
    },

    async set(key, value) {
      const cmd = `SET ${key} "${value.replace(/"/g, '\\"')}"\r\n`;
      await writer.write(new TextEncoder().encode(cmd));
      
      const response = await reader.read();
      const result = new TextDecoder().decode(response.value);
      return result.includes('+OK');
    },

    async keys(pattern) {
      const cmd = `KEYS ${pattern}\r\n`;
      await writer.write(new TextEncoder().encode(cmd));
      
      const response = await reader.read();
      const result = new TextDecoder().decode(response.value);
      
      if (result.startsWith('*0')) return [];
      if (result.startsWith('*')) {
        const lines = result.split('\r\n');
        const keys = [];
        for (let i = 1; i < lines.length; i += 2) {
          if (lines[i] && lines[i].startsWith('$') && lines[i + 1]) {
            keys.push(lines[i + 1]);
          }
        }
        return keys;
      }
      return [];
    },

    async quit() {
      try {
        await writer.write(new TextEncoder().encode('QUIT\r\n'));
        await writer.close();
        await reader.cancel();
      } catch (e) {
        // Ignore connection close errors
      }
    }
  };
}

// Validate invitation codes: check D1 first, then hardcoded fallback for development
async function validateInvitation(request, env) {
  try {
    const { invitationCode } = await request.json();
    
    console.log('🔍 Validating invitation code:', invitationCode);

    if (!invitationCode || invitationCode.length !== 8) {
      return new Response(JSON.stringify({
        valid: false,
        message: 'Invitation code must be exactly 8 characters'
      }), {
        status: 400,
        headers: { 
          "content-type": "application/json",
          ...corsHeaders
        }
      });
    }

    const upperCode = invitationCode.toUpperCase();

    // 1) Try D1 database first for production readiness
    try {
      if (env.epc_form_data && typeof env.epc_form_data.prepare === 'function') {
        const row = await env.epc_form_data
          .prepare("SELECT title, company_name, contact_email, status FROM invitations WHERE auth_code = ?")
          .bind(upperCode)
          .first();

        if (row) {
          // Enforce active status for usability
          if (row.status && String(row.status).toLowerCase() !== 'active') {
            return new Response(JSON.stringify({
              valid: false,
              message: `Invitation code is ${row.status}`
            }), {
              status: 404,
              headers: { "content-type": "application/json", ...corsHeaders }
            });
          }

          return new Response(JSON.stringify({
            valid: true,
            message: 'Valid invitation code',
            invitation: {
              code: upperCode,
              title: row.title || '',
              companyName: row.company_name,
              contactEmail: row.contact_email,
              notes: 'Synced from Power Automate'
            },
            source: 'd1'
          }), {
            headers: { "content-type": "application/json", ...corsHeaders }
          });
        }
      }
    } catch (d1err) {
      console.error('D1 lookup failed in validate-invitation:', d1err);
      // Continue to hardcoded fallback
    }

    // No hardcoded test codes in production - all invitations must come from SharePoint

    // If not found in hardcoded list, return invalid
    return new Response(JSON.stringify({
      valid: false,
      message: 'Invalid or expired invitation code',
      source: 'validation_failed'
    }), {
      status: 404,
      headers: { 
        "content-type": "application/json",
        ...corsHeaders
      }
    });
    
  } catch (error) {
    console.error('💥 Invitation validation error:', error);
    return new Response(JSON.stringify({
      valid: false,
      message: 'Unable to validate invitation code at this time',
      error: 'Validation service error'
    }), {
      status: 500,
      headers: { 
        "content-type": "application/json",
        ...corsHeaders
      }
    });
  }
}

// Sync invitation from Power Automate to D1 database
async function syncInvitation(request, env) {
  try {
    const invitationData = await request.json();
    
    console.log('📥 Sync invitation request from Power Automate:', invitationData);

    // Extract the AuthCode and other fields from Power Automate
    const authCode = invitationData.AuthCode || invitationData.authCode;
    const title = invitationData.Title || invitationData.title || '';
    const companyName = invitationData.CompanyName || invitationData.companyName || invitationData.Company;
    const contactEmail = invitationData.ContactEmail || invitationData.contactEmail || invitationData.Email;
    const notes = invitationData.Notes || invitationData.notes || '';

    if (!authCode || authCode.length !== 8) {
      return new Response(JSON.stringify({
        success: false,
        message: 'AuthCode must be exactly 8 characters',
        received: invitationData
      }), {
        status: 400,
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }

    if (!companyName || !contactEmail) {
      return new Response(JSON.stringify({
        success: false,
        message: 'CompanyName and ContactEmail are required',
        received: invitationData
      }), {
        status: 400,
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }

    // Try to save to D1 database (will fail gracefully if not available)
    try {
      const now = new Date().toISOString();
      await env.epc_form_data.prepare(`
        INSERT OR REPLACE INTO invitations (
          auth_code, title, company_name, contact_email, 
          notes, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        authCode.toUpperCase(),
        title,
        companyName,
        contactEmail,
        notes,
        'active',
        now,
        now
      ).run();
      
      console.log(`✅ Invitation synced to D1: ${authCode} -> ${companyName}`);
      
      return new Response(JSON.stringify({
        success: true,
        message: 'Invitation synced successfully to D1 database',
        invitation: {
          authCode: authCode.toUpperCase(),
          title,
          companyName,
          contactEmail,
          notes,
          status: 'active'
        },
        syncedAt: now
      }), {
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
      
    } catch (d1Error) {
      console.error('⚠️ D1 sync failed, logging invitation for manual processing:', d1Error);
      
      // Log to console for manual processing later
      console.log('MANUAL_INVITATION_SYNC_REQUIRED:', JSON.stringify({
        authCode: authCode.toUpperCase(),
        title,
        companyName,
        contactEmail,
        notes,
        timestamp: new Date().toISOString(),
        powerAutomateData: invitationData
      }));
      
      return new Response(JSON.stringify({
        success: true,
        message: 'Invitation logged for processing (D1 unavailable)',
        invitation: {
          authCode: authCode.toUpperCase(),
          title,
          companyName,
          contactEmail,
          notes,
          status: 'logged_for_processing'
        },
        note: 'Will be manually synced when D1 is available'
      }), {
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
    
  } catch (error) {
    console.error('💥 Sync invitation error:', error);
    return new Response(JSON.stringify({
      success: false,
      message: 'Failed to sync invitation',
      error: error.message
    }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }
}

// Submit application: create D1 application and migrate draft files from R2 to SharePoint in background
async function submitEpcApplication(request, env, ctx) {
  try {
    const payload = await request.json();

    // Flatten and validate
    const app = flattenApplicationPayload(payload);
    const invitationCode = app.invitation_code;
    if (!invitationCode || invitationCode.length !== 8) {
      return new Response(JSON.stringify({ success: false, message: 'invitationCode (8 chars) is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Create application record (minimal fields populated)
    let appId = null;
    try {
      const { columns, values, placeholders } = buildApplicationsInsert(app);
      await env.epc_form_data.prepare(`
        INSERT INTO applications (${columns.join(', ')})
        VALUES (${placeholders.join(', ')})
      `).bind(...values).run();
      const row = await env.epc_form_data.prepare('SELECT id FROM applications WHERE invitation_code = ? ORDER BY id DESC LIMIT 1').bind(invitationCode).first();
      appId = row?.id;
    } catch (e) {
      console.error('Failed to create application row:', e);
      return new Response(JSON.stringify({ success: false, message: 'Failed to create application record' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Kick off background migration of draft files
    ctx.waitUntil(migrateDraftFilesToSharePoint(invitationCode, appId, env));

    // Send notifications (best-effort)
    ctx.waitUntil(sendSubmissionNotifications(app, appId, env));

    return new Response(JSON.stringify({
      success: true,
      message: 'Application submitted. Files migration scheduled.',
      applicationId: appId,
      status: 'submitted'
    }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });

  } catch (error) {
    console.error('💥 submitEpcApplication error:', error);
    return new Response(JSON.stringify({ success: false, message: 'Submission failed', error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

async function migrateDraftFilesToSharePoint(invitationCode, applicationId, env) {
  try {
    const sharePointConfig = {
      siteUrl: 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners',
      clientId: env.SHAREPOINT_CLIENT_ID,
      tenant: 'saberrenewables.onmicrosoft.com'
    };

    const token = await getSharePointAccessToken(sharePointConfig, env);
    if (!token) {
      console.error('No SharePoint token. Leaving files in R2 for later migration.');
      await env.epc_form_data.prepare(`UPDATE applications SET status = 'submitted' WHERE id = ?`).bind(applicationId).run();
      return;
    }

    // Ensure target base folder exists: EPC Applications/<INVITATION_CODE>
    const baseFolder = `EPC Applications/${invitationCode}`;
    await ensureSharePointFolderPath(baseFolder, sharePointConfig, token);

    // Select draft files for this invitation
    const iter = await env.epc_form_data.prepare(`
      SELECT id, field_name, r2_key, original_filename, content_type, file_size
      FROM draft_files WHERE invitation_code = ?
    `).bind(invitationCode).all();

    const rows = iter?.results || [];
    for (const row of rows) {
      try {
        // Derive subfolder from r2_key or field_name
        let subfolder = 'documents';
        const f = (row.field_name || '').toLowerCase();
        if (f.includes('logo') || f.includes('image')) subfolder = 'logos';
        else if (f.includes('certificate') || f.includes('cert')) subfolder = 'certificates';
        else if (f.includes('financial') || f.includes('insurance')) subfolder = 'financial';

        const spFolder = `EPC Applications/${invitationCode}/${subfolder}`;
        await ensureSharePointFolderPath(spFolder, sharePointConfig, token);

        // Read the object from R2
        const obj = await env.EPC_PARTNER_FILES.get(row.r2_key);
        if (!obj) {
          console.warn('R2 object missing, skipping:', row.r2_key);
          continue;
        }
        const bytes = await obj.arrayBuffer();

        // Upload to SharePoint
        const upload = await uploadBufferToSharePoint(spFolder, row.original_filename, row.content_type, bytes, sharePointConfig, token);
        if (!upload.success) {
          console.error('Failed to upload to SharePoint:', row.original_filename, upload.error);
          continue;
        }

        // Record in application_files
        try {
          await env.epc_form_data.prepare(`
            INSERT INTO application_files (
              application_id, field_name, original_filename, stored_filename, file_size, content_type, upload_url, sharepoint_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
          `).bind(
            applicationId,
            row.field_name,
            row.original_filename,
            row.r2_key,
            row.file_size,
            row.content_type,
            upload.fileUrl,
            upload.sharePointId
          ).run();
        } catch (e) {
          console.warn('Could not record application file in D1:', e);
        }

        // If this looks like a logo, cache it on applications for fast header render
        try {
          const fn = (row.field_name || '').toLowerCase();
          if (fn.includes('logo')) {
            await env.epc_form_data.prepare('UPDATE applications SET partner_logo_url = ?, partner_logo_sp_id = ? WHERE id = ?')
              .bind(upload.fileUrl, upload.sharePointId, applicationId)
              .run();
          }
        } catch (e) { console.warn('Failed to cache partner logo:', e); }

        // Optionally clean up R2 draft object and D1 draft row
        await env.EPC_PARTNER_FILES.delete(row.r2_key);
        await env.epc_form_data.prepare(`DELETE FROM draft_files WHERE id = ?`).bind(row.id).run();

      } catch (fileErr) {
        console.error('Error migrating file:', row?.original_filename, fileErr);
      }
    }

    await env.epc_form_data.prepare(`UPDATE applications SET status = 'processing' WHERE id = ?`).bind(applicationId).run();

  } catch (e) {
    console.error('migrateDraftFilesToSharePoint error:', e);
  }
}

async function sendSubmissionNotifications(app, appId, env) {
  try {
    const from = env.NOTIFY_FROM_EMAIL;
    const internalTo = env.NOTIFY_INTERNAL_TO;
    const applicantTo = app.email;
    const subject = `EPC Application Submitted - ${app.company_name || app.companyName || app.invitation_code}`;
    const opLink = `https://epc.saberrenewable.energy/operations/${encodeURIComponent(app.invitation_code || '')}`;
    const html = `
      <div style="font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;">
        <h2>EPC Partner Application Submitted</h2>
        <p><strong>Company:</strong> ${escapeHtml(app.company_name || app.companyName || '')}</p>
        <p><strong>Contact:</strong> ${escapeHtml(app.contact_name || '')} • ${escapeHtml(app.email || '')}</p>
        <p><strong>Invitation Code:</strong> ${escapeHtml(app.invitation_code || '')}</p>
        <p><strong>Submitted:</strong> ${escapeHtml(app.submitted_at || new Date().toISOString())}</p>
        <p style="margin-top:12px"><a href="${opLink}" style="color:#3b82f6;text-decoration:none">Open in Operations</a></p>
      </div>`;

    if (from && internalTo) {
      await sendMailViaGraph(env, from, internalTo, subject, html);
    }
    if (from && isValidEmail(applicantTo)) {
      await sendMailViaGraph(env, from, applicantTo, 'Thanks for submitting your EPC application', `
        <div style="font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;">
          <p>Thank you for submitting your EPC Partner application.</p>
          <p>We will review your information and contact you if anything further is required.</p>
          <p>Reference: ${escapeHtml(app.invitation_code || '')}</p>
        </div>`);
    }

    // Teams channel webhook (optional, if configured)
    if (env.TEAMS_WEBHOOK_URL) {
      await sendTeamsWebhook(env, {
        title: 'New EPC Application Submitted',
        company: app.company_name || app.companyName || 'Unknown',
        contact: app.contact_name || '',
        email: app.email || '',
        invitationCode: app.invitation_code || '',
        applicationId: appId
      });
    }
  } catch (e) {
    console.error('sendSubmissionNotifications error:', e);
  }
}

function escapeHtml(s) {
  return String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
}

function isValidEmail(e) { return /.+@.+\..+/.test(String(e||'')); }

async function getGraphAccessTokenForMail(env) {
  try {
    if (!env.SP_CERT_PRIVATE_KEY || !env.SHAREPOINT_TENANT || !env.SHAREPOINT_CLIENT_ID) return null;
    const tokenUrl = `https://login.microsoftonline.com/${env.SHAREPOINT_TENANT}/oauth2/v2.0/token`;
    const clientId = env.SHAREPOINT_CLIENT_ID;
    const now = Math.floor(Date.now()/1000);
    const header = { alg: 'RS256', typ: 'JWT' };
    if (env.SP_CERT_X5C) {
      try {
        const der = certPemToDer(env.SP_CERT_X5C);
        header['x5t'] = await sha1Base64Url(der);
        header['x5t#S256'] = await sha256Base64Url(der);
      } catch {}
    } else if (env.SP_CERT_THUMBPRINT) header['x5t'] = env.SP_CERT_THUMBPRINT;
    if (env.SP_CERT_KID) header['kid'] = env.SP_CERT_KID;
    const claims = {
      iss: clientId,
      sub: clientId,
      aud: tokenUrl,
      jti: crypto.randomUUID(),
      nbf: now - 5,
      exp: now + 10*60
    };
    const assertion = await signJwtWithPem(header, claims, env.SP_CERT_PRIVATE_KEY);
    const params = new URLSearchParams();
    params.append('grant_type','client_credentials');
    params.append('client_id', clientId);
    params.append('scope','https://graph.microsoft.com/.default');
    params.append('client_assertion_type','urn:ietf:params:oauth:client-assertion-type:jwt-bearer');
    params.append('client_assertion', assertion);
    const resp = await fetch(tokenUrl, { method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body: params });
    if (!resp.ok) { console.error('Graph token failed:', resp.status, await resp.text()); return null; }
    const data = await resp.json();
    return data.access_token;
  } catch (e) {
    console.error('getGraphAccessTokenForMail error:', e);
    return null;
  }
}

async function sendMailViaGraph(env, fromEmail, toEmail, subject, html) {
  const token = await getGraphAccessTokenForMail(env);
  if (!token) { console.warn('No Graph token for mail; skipping send'); return; }
  const url = `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(fromEmail)}/sendMail`;
  const toList = Array.isArray(toEmail)
    ? toEmail
    : String(toEmail || '')
        .split(/[;,\s]+/)
        .map(s => s.trim())
        .filter(isValidEmail);
  const body = {
    message: {
      subject,
      body: { contentType: 'HTML', content: html },
      toRecipients: toList.map(a => ({ emailAddress: { address: a } }))
    },
    saveToSentItems: false
  };
  const resp = await fetch(url, { method:'POST', headers:{ 'Authorization':`Bearer ${token}`, 'Content-Type':'application/json' }, body: JSON.stringify(body) });
  if (!resp.ok) {
    console.error('Graph sendMail failed:', resp.status, await resp.text());
  } else {
    console.log(`✉️  Email sent to ${toEmail}`);
  }
}

async function sendTeamsWebhook(env, data) {
  try {
    const url = env.TEAMS_WEBHOOK_URL;
    if (!url) return;
    const card = {
      '@type': 'MessageCard',
      '@context': 'https://schema.org/extensions',
      summary: 'New EPC application submitted',
      themeColor: '2EB67D',
      title: data.title || 'EPC Update',
      text: `**Company:** ${escapeHtml(data.company)}  \n**Contact:** ${escapeHtml(data.contact)}  \n**Email:** ${escapeHtml(data.email)}  \n**Invitation:** ${escapeHtml(data.invitationCode)}`,
      potentialAction: [
        {
          '@type': 'OpenUri',
          name: 'Open Operations',
          targets: [{ os: 'default', uri: 'https://epc.saberrenewable.energy/operations' }]
        }
      ]
    };
    const resp = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(card) });
    if (!resp.ok) {
      console.error('Teams webhook failed:', resp.status, await resp.text());
    } else {
      console.log('📣 Teams notification sent');
    }
  } catch (e) {
    console.error('sendTeamsWebhook error:', e);
  }
}

async function sendReviewNotification(app, section, status, note, env) {
  try {
    const from = env.NOTIFY_FROM_EMAIL;
    const internalTo = env.NOTIFY_INTERNAL_TO;
    const pretty = section.charAt(0).toUpperCase() + section.slice(1);
    const subject = `EPC Application ${app.invitation_code}: ${pretty} ${status}`;
    const opLink = `https://epc.saberrenewable.energy/operations/${encodeURIComponent(app.invitation_code || '')}`;
    const html = `
      <div style="font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;">
        <h2>Section ${pretty} ${status}</h2>
        <p><strong>Invitation:</strong> ${escapeHtml(app.invitation_code || '')}</p>
        <p><strong>Company:</strong> ${escapeHtml(app.company_name || '')}</p>
        ${note ? `<p><strong>Note:</strong> ${escapeHtml(note)}</p>` : ''}
        <p style="margin-top:12px"><a href="${opLink}" style="color:#3b82f6;text-decoration:none">Open in Operations</a></p>
      </div>`;
    if (from && internalTo) await sendMailViaGraph(env, from, internalTo, subject, html);
    if (env.TEAMS_WEBHOOK_URL) {
      await sendTeamsWebhook(env, {
        title: `Section ${pretty} ${status}`,
        company: app.company_name || 'Unknown',
        contact: app.contact_name || '',
        email: app.email || '',
        invitationCode: app.invitation_code || ''
      });
    }
  } catch (e) {
    console.error('sendReviewNotification error:', e);
  }
}

function toBool(v) { return v === true || v === 'true' || v === 1 || v === '1'; }

function flattenApplicationPayload(payload) {
  const d = payload || {};
  const sub = d.submission || {};
  const svc = d.servicesExperience || {};
  const roles = d.rolesCapabilities || {};
  const cert = d.certifications || {};
  const ins = d.insurance || {};
  const comp = d.compliance || {};
  const agr = d.agreement || {};

  const invitationCode = (sub.invitationCode || d.invitationCode || d.InvitationCode || '').toString().toUpperCase();

  return {
    invitation_code: invitationCode,
    status: 'submitted',
    submitted_at: new Date().toISOString(),

    // Company info
    company_name: d.companyName || null,
    trading_name: d.tradingName || null,
    registration_number: d.registrationNumber || null,
    vat_number: d.vatNumber || null,
    registered_address: d.registeredAddress || null,
    head_office: d.headOffice || null,
    parent_company: d.parentCompany || null,
    years_trading: d.yearsTrading || null,

    // Contact
    contact_name: d.contactName || null,
    contact_title: d.contactTitle || null,
    email: d.email || null,
    phone: d.phone || null,
    company_website: d.companyWebsite || null,

    // Services & experience
    specializations: svc.specializations || null,
    software_tools: svc.softwareTools || null,
    projects_per_month: svc.averageProjectsPerMonth || d.projectsPerMonth || null,
    team_size: svc.teamSize || d.teamSize || null,
    years_experience: svc.yearsExperience || d.yearsExperience || null,
    services: svc.services || d.services || null,
    coverage: svc.coverage || d.coverage || null,
    coverage_region: svc.coverageRegion || d.coverageRegion || null,
    coverage_regions: JSON.stringify(svc.coverageRegions || d.coverageRegions || []),
    resources_per_project: svc.resourcesPerProject || d.resourcesPerProject || null,
    client_reference: svc.clientReference || d.clientReference || null,

    // Roles & certifications
    principal_contractor: toBool(roles.principalContractor),
    principal_designer: toBool(roles.principalDesigner),
    principal_contractor_scale: roles.principalContractorScale || null,
    principal_designer_scale: roles.principalDesignerScale || null,
    internal_staff_percentage: roles.internalStaffPercentage || null,
    subcontract_percentage: roles.subcontractPercentage || null,
    niceic_contractor: toBool(cert.niceicContractor),
    mcs_approved: toBool(cert.mcsApproved),
    accreditations: cert.accreditations || null,
    certification_details: cert.certificationDetails || null,
    iso_standards: cert.isoStandards || null,
    named_principal_designer: roles.namedPrincipalDesigner || null,
    principal_designer_qualifications: roles.principalDesignerQualifications || null,
    training_records_summary: roles.trainingRecordsSummary || null,

    // Insurance & compliance
    public_liability_insurance: toBool(ins.publicLiabilityInsurance),
    public_liability_expiry: ins.publicLiabilityExpiry || null,
    public_liability_indemnity: toBool(ins.publicLiabilityIndemnity),
    employers_liability_insurance: toBool(ins.employersLiabilityInsurance),
    employers_liability_expiry: ins.employersLiabilityExpiry || null,
    professional_indemnity_insurance: toBool(ins.professionalIndemnityInsurance),
    professional_indemnity_expiry: ins.professionalIndemnityExpiry || null,
    hse_notices_last_5_years: comp.hseNoticesLast5Years || null,
    pending_prosecutions: comp.pendingProsecutions || null,
    riddor_incident_count: comp.riddorIncidentCount || null,
    riddor_incident_details: comp.riddorIncidentDetails || null,
    cdm_management_evidence: comp.cdmManagementEvidence || null,
    near_miss_procedure: comp.nearMissProcedure || null,
    quality_procedure_evidence: comp.qualityProcedureEvidence || null,
    hseq_incidents: comp.hseqIncidents || null,
    riddor_incidents: comp.riddorIncidents || null,

    // Policy & Dates
    health_safety_policy_date: comp.healthSafetyPolicyDate || null,
    environmental_policy_date: comp.environmentalPolicyDate || null,
    modern_slavery_policy_date: comp.modernSlaveryPolicyDate || null,
    substance_misuse_policy_date: comp.substanceMisusePolicyDate || null,
    right_to_work_method: comp.rightToWorkMethod || null,
    gdpr_policy_date: comp.gdprPolicyDate || null,
    cyber_incident_last_3_years: comp.cyberIncidentLast3Years || null,
    legal_clarifications: comp.legalClarifications || null,

    // Agreement
    agree_to_terms: toBool(agr.agreeToTerms),
    agree_to_codes: toBool(agr.agreeToCodes),
    data_processing_consent: toBool(agr.dataProcessingConsent),
    marketing_consent: toBool(agr.marketingConsent),
    nationwide_coverage: toBool(agr.nationwideCoverage),
    contracts_reviewed: toBool(agr.contractsReviewed),
    received_contract_pack: toBool(agr.receivedContractPack),

    // Submission notes
    additional_information: d.submission?.additionalInformation || null,
    notes: d.submission?.notes || null,
    clarifications: d.submission?.clarifications || null
  };
}

function buildApplicationsInsert(app) {
  const columns = Object.keys(app);
  const values = columns.map(k => app[k]);
  const placeholders = columns.map(() => '?');
  return { columns, values, placeholders };
}

// Partner Portal Authentication Handlers

async function partnerTestLoginHandler(request, env) {
  try {
    const { email } = await request.json();

    if (!email) {
      return new Response(JSON.stringify({ success: false, error: 'Email required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Check if partner exists and is completed
    const partner = await env.epc_form_data.prepare(`
      SELECT id, company_name, email
      FROM applications
      WHERE email = ? AND status = 'completed'
    `).bind(email).first();

    if (!partner) {
      return new Response(JSON.stringify({
        success: false,
        error: 'No approved partner account found for this email'
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // For testing, create a simple token (in production this would be JWT or similar)
    const token = `test-token-${partner.id}-${Date.now()}`;

    return new Response(JSON.stringify({
      success: true,
      token: token,
      partner: {
        id: partner.id,
        email: partner.email,
        companyName: partner.company_name,
        canAccessProjects: true
      }
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (error) {
    console.error('Test login error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Login failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

async function partnerLoginHandler(request, env) {
  try {
    const { email } = await request.json();

    if (!email) {
      return new Response(JSON.stringify({ success: false, error: 'Email required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Check if partner exists and is completed (simplified for testing)
    const partner = await env.epc_form_data.prepare(`
      SELECT id, company_name, email
      FROM applications
      WHERE email = ? AND status = 'completed'
    `).bind(email).first();

    if (!partner) {
      return new Response(JSON.stringify({
        success: false,
        error: 'No approved partner account found for this email'
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Generate magic link token
    const token = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + 15 * 60 * 1000); // 15 minutes

    // Store session token
    await env.DB.prepare(`
      INSERT INTO partner_sessions (partner_id, session_token, email, expires_at)
      VALUES (?, ?, ?, ?)
    `).bind(partner.id, token, email, expiresAt.toISOString()).run();

    // Send magic link email via Power Automate
    const magicLink = `https://epc.saberrenewable.energy/partner/auth?token=${token}`;

    try {
      await fetch(env.POWER_AUTOMATE_PARTNER_LOGIN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: email,
          companyName: partner.company_name,
          magicLink: magicLink
        })
      });
    } catch (emailError) {
      console.error('Failed to send magic link email:', emailError);
    }

    return new Response(JSON.stringify({
      success: true,
      message: 'Magic link sent to your email address'
    }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Partner login error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Login failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function validatePartnerAuth(request, env) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return { valid: false };
  }

  const token = authHeader.substring(7);

  // For testing, handle simple tokens
  if (token.startsWith('test-token-')) {
    const parts = token.split('-');
    if (parts.length >= 3) {
      const partnerId = parts[2];

      // Get partner data
      const partner = await env.epc_form_data.prepare(`
        SELECT id, company_name, email
        FROM applications
        WHERE id = ? AND status = 'completed'
      `).bind(partnerId).first();

      if (partner) {
        return {
          valid: true,
          partner: {
            partnerId: partner.id,
            email: partner.email,
            companyName: partner.company_name,
            canAccessProjects: true
          }
        };
      }
    }
  }

  return { valid: false };
}

async function partnerAuthCheckHandler(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get('token');

  if (!token) {
    return new Response('Missing token', { status: 400 });
  }

  try {
    const session = await env.DB.prepare(`
      SELECT ps.*, a.company_name, a.email, a.can_access_projects
      FROM partner_sessions ps
      JOIN applications a ON ps.partner_id = a.id
      WHERE ps.session_token = ? AND ps.expires_at > datetime('now')
    `).bind(token).first();

    if (!session) {
      return new Response('Invalid or expired token', { status: 401 });
    }

    // Extend session expiry
    const newExpiry = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours
    await env.DB.prepare(`
      UPDATE partner_sessions
      SET expires_at = ?, last_active = datetime('now')
      WHERE session_token = ?
    `).bind(newExpiry.toISOString(), token).run();

    return new Response(JSON.stringify({
      success: true,
      partner: {
        id: session.partner_id,
        email: session.email,
        companyName: session.company_name,
        canAccessProjects: session.can_access_projects
      },
      token: token
    }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Partner auth check error:', error);
    return new Response('Authentication failed', { status: 500 });
  }
}

async function partnerLogoutHandler(request, env) {
  const partner = await validatePartnerAuth(request, env);
  if (!partner) {
    return new Response(JSON.stringify({ success: false, error: 'Not authenticated' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const authHeader = request.headers.get('Authorization');
  const token = authHeader.substring(7);

  try {
    await env.DB.prepare(`
      DELETE FROM partner_sessions WHERE session_token = ?
    `).bind(token).run();

    return new Response(JSON.stringify({ success: true }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Partner logout error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Logout failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function getPartnerProfileHandler(request, env) {
  const partner = await validatePartnerAuth(request, env);
  if (!partner) {
    return new Response(JSON.stringify({ error: 'Not authenticated' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const profile = await env.DB.prepare(`
      SELECT
        id, company_name, trading_name, email, phone, company_website,
        specializations, coverage_regions, services, team_size, years_experience,
        partner_approved, can_access_projects, approved_at
      FROM applications
      WHERE id = ?
    `).bind(partner.partnerId).first();

    return new Response(JSON.stringify({ success: true, profile }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Get partner profile error:', error);
    return new Response(JSON.stringify({ error: 'Failed to fetch profile' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function getPartnerProjectsHandler(partner, env) {
  try {
    const projects = await env.epc_form_data.prepare(`
      SELECT
        p.id, p.project_name, p.tender_id as project_code, p.description,
        p.location, p.project_type, p.tender_status as status, p.created_at,
        pp.id as invitation_id, pp.role, pp.status as invitation_status,
        pp.invited_at, pp.accepted_at
      FROM projects p
      JOIN project_partners pp ON p.id = pp.project_id
      WHERE pp.partner_id = ?
      ORDER BY pp.invited_at DESC
    `).bind(partner.partnerId).all();

    return new Response(JSON.stringify({
      success: true,
      projects: projects.results
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  } catch (error) {
    console.error('Get partner projects error:', error);
    return new Response(JSON.stringify({ error: 'Failed to fetch projects' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

async function updatePartnerInvitationHandler(partner, invitationId, request, env) {
  try {
    const { status } = await request.json();

    if (!['accepted', 'declined'].includes(status)) {
      return new Response(JSON.stringify({ error: 'Invalid status' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Verify this invitation belongs to the authenticated partner
    const invitation = await env.epc_form_data.prepare(`
      SELECT id, partner_id, status as current_status
      FROM project_partners
      WHERE id = ? AND partner_id = ?
    `).bind(invitationId, partner.partnerId).first();

    if (!invitation) {
      return new Response(JSON.stringify({ error: 'Invitation not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    if (invitation.current_status !== 'invited') {
      return new Response(JSON.stringify({ error: 'Invitation cannot be modified' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Update the invitation status
    const updateData = {
      status,
      updated_at: new Date().toISOString()
    };

    if (status === 'accepted') {
      updateData.accepted_at = new Date().toISOString();
    }

    const updateQuery = status === 'accepted'
      ? `UPDATE project_partners SET status = ?, accepted_at = ?, updated_at = ? WHERE id = ?`
      : `UPDATE project_partners SET status = ?, updated_at = ? WHERE id = ?`;

    const bindParams = status === 'accepted'
      ? [status, updateData.accepted_at, updateData.updated_at, invitationId]
      : [status, updateData.updated_at, invitationId];

    await env.epc_form_data.prepare(updateQuery).bind(...bindParams).run();

    return new Response(JSON.stringify({
      success: true,
      message: `Invitation ${status} successfully`
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (error) {
    console.error('Update partner invitation error:', error);
    return new Response(JSON.stringify({ error: 'Failed to update invitation' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

async function partnerUploadDocumentHandler(partner, request, env) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');
    const projectId = formData.get('projectId');
    const partnerId = formData.get('partnerId');
    const partnerName = formData.get('partnerName');
    const tenderId = formData.get('tenderId');
    const folder = formData.get('folder');
    const folderName = formData.get('folderName');

    if (!file || !projectId || !folder) {
      return new Response(JSON.stringify({ success: false, error: 'Missing required fields' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Verify partner has access to this project
    const projectAccess = await env.epc_form_data.prepare(`
      SELECT pp.id
      FROM project_partners pp
      WHERE pp.project_id = ? AND pp.partner_id = ? AND pp.status = 'accepted'
    `).bind(projectId, partner.partnerId).first();

    if (!projectAccess) {
      return new Response(JSON.stringify({ success: false, error: 'Access denied to this project' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Create structured path: tenderId/partnerName/folder/filename
    const sanitizedPartnerName = partnerName.replace(/[^a-zA-Z0-9-_\s]/g, '').replace(/\s+/g, '_');
    const sanitizedFolderName = folderName.replace(/[^a-zA-Z0-9-_\s]/g, '').replace(/\s+/g, '_');
    const timestamp = Date.now();
    const fileExtension = file.name.split('.').pop();
    const sanitizedFileName = `${file.name.replace(/[^a-zA-Z0-9-_\.\s]/g, '').replace(/\s+/g, '_')}`;

    const r2Key = `documents/${tenderId}/${sanitizedPartnerName}/${sanitizedFolderName}/${timestamp}_${sanitizedFileName}`;

    // Convert file to array buffer
    const fileBuffer = await file.arrayBuffer();

    // Upload to R2
    await env.EPC_DOCUMENTS.put(r2Key, fileBuffer, {
      httpMetadata: {
        contentType: file.type,
      },
    });

    // Sync to SharePoint (disabled for staging reliability)
    let sharepointResult = {
      success: false,
      error: env.ENVIRONMENT === 'production' ? 'SharePoint not configured' : 'SharePoint disabled in staging'
    };
    console.log(`📝 Document uploaded to R2: ${r2Key} (SharePoint sync: ${env.ENVIRONMENT})`);

    const sharepointPath = sharepointResult?.sharePointUrl || `${tenderId}/${sanitizedPartnerName}/${folderName}/${file.name}`;

    // Record in database
    const documentRecord = await env.epc_form_data.prepare(`
      INSERT INTO project_documents (
        project_id, partner_id, document_name, document_type,
        original_filename, file_size, content_type, storage_path,
        sharepoint_path, sharepoint_id, sync_status,
        uploaded_by, uploaded_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    `).bind(
      projectId,
      partner.partnerId,
      folder,
      folder,
      file.name,
      file.size,
      file.type,
      r2Key,
      sharepointResult?.sharePointUrl || null,
      sharepointResult?.sharePointId || null,
      sharepointResult?.success ? 'synced' : 'pending',
      partner.email
    ).run();

    return new Response(JSON.stringify({
      success: true,
      document: {
        id: documentRecord.meta.last_row_id,
        name: file.name,
        size: file.size,
        folder: folderName,
        path: r2Key,
        sharepointPath: sharepointPath,
        syncStatus: sharepointResult?.success ? 'synced' : 'pending',
        syncError: sharepointResult?.success ? null : sharepointResult?.error
      }
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (error) {
    console.error('Partner document upload error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Upload failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

async function getPartnerProjectDocumentsHandler(partner, projectId, env) {
  try {
    // Verify partner has access to this project
    const projectAccess = await env.epc_form_data.prepare(`
      SELECT pp.id
      FROM project_partners pp
      WHERE pp.project_id = ? AND pp.partner_id = ? AND pp.status = 'accepted'
    `).bind(projectId, partner.partnerId).first();

    if (!projectAccess) {
      return new Response(JSON.stringify({ success: false, error: 'Access denied to this project' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Get documents uploaded by this partner for this project
    const documents = await env.epc_form_data.prepare(`
      SELECT id, document_name, document_type, original_filename,
             file_size, content_type, uploaded_at
      FROM project_documents
      WHERE project_id = ? AND partner_id = ?
      ORDER BY uploaded_at DESC
    `).bind(projectId, partner.partnerId).all();

    return new Response(JSON.stringify({
      success: true,
      documents: documents.results
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (error) {
    console.error('Get partner project documents error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Failed to fetch documents' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

async function getPartnerProjectDetailHandler(request, env) {
  const partner = await validatePartnerAuth(request, env);
  if (!partner) {
    return new Response(JSON.stringify({ error: 'Not authenticated' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const url = new URL(request.url);
  const projectId = url.pathname.split('/').pop();

  try {
    // Verify partner has access to this project
    const projectAccess = await env.DB.prepare(`
      SELECT pp.role, pp.status, p.*
      FROM project_partners pp
      JOIN projects p ON pp.project_id = p.id
      WHERE pp.project_id = ? AND pp.partner_id = ? AND pp.status = 'accepted'
    `).bind(projectId, partner.partnerId).first();

    if (!projectAccess) {
      return new Response(JSON.stringify({ error: 'Project not found or access denied' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Get project deliverables
    const deliverables = await env.DB.prepare(`
      SELECT * FROM project_deliverables
      WHERE project_id = ?
      ORDER BY folder_path, deliverable_name
    `).bind(projectId).all();

    // Get partner's uploads for this project
    const uploads = await env.DB.prepare(`
      SELECT * FROM partner_uploads
      WHERE project_id = ? AND partner_id = ?
      ORDER BY uploaded_at DESC
    `).bind(projectId, partner.partnerId).all();

    return new Response(JSON.stringify({
      success: true,
      project: projectAccess,
      deliverables,
      uploads
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Get partner project detail error:', error);
    return new Response(JSON.stringify({ error: 'Failed to fetch project details' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Replace document with new version
async function replacePartnerDocumentHandler(partner, documentId, request, env) {
  try {
    // Get current document
    const currentDoc = await env.epc_form_data.prepare(`
      SELECT pd.*, pp.project_id
      FROM project_documents pd
      JOIN project_partners pp ON pd.project_id = pp.project_id
      WHERE pd.id = ? AND pp.partner_id = ? AND pp.status = 'accepted'
    `).bind(documentId, partner.partnerId).first();

    if (!currentDoc) {
      return new Response(JSON.stringify({ success: false, error: 'Document not found or access denied' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    const formData = await request.formData();
    const file = formData.get('file');

    if (!file) {
      return new Response(JSON.stringify({ success: false, error: 'No file provided' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Archive current version in SharePoint (disabled for staging)
    console.log(`📝 Document replacement: ${documentId} (SharePoint disabled in ${env.ENVIRONMENT})`);

    // Create new version
    const timestamp = Date.now();
    const fileExtension = file.name.split('.').pop();
    const sanitizedFileName = `${file.name.replace(/[^a-zA-Z0-9-_\.\s]/g, '').replace(/\s+/g, '_')}`;
    const r2Key = currentDoc.storage_path.replace(/\/[^/]*$/, `/v${timestamp}_${sanitizedFileName}`);

    const fileBuffer = await file.arrayBuffer();

    // Upload new version to R2
    await env.EPC_DOCUMENTS.put(r2Key, fileBuffer, {
      httpMetadata: { contentType: file.type },
    });

    // Upload new version to SharePoint (disabled for staging)
    const sharepointResult = {
      success: false,
      error: `SharePoint disabled in ${env.ENVIRONMENT}`
    };

    // Update document record
    await env.epc_form_data.prepare(`
      UPDATE project_documents
      SET original_filename = ?, file_size = ?, content_type = ?,
          storage_path = ?, sharepoint_path = ?, sharepoint_id = ?,
          sync_status = ?, version = version + 1, uploaded_at = datetime('now')
      WHERE id = ?
    `).bind(
      file.name,
      file.size,
      file.type,
      r2Key,
      sharepointResult?.sharePointUrl,
      sharepointResult?.sharePointId,
      sharepointResult?.success ? 'synced' : 'pending',
      documentId
    ).run();

    return new Response(JSON.stringify({
      success: true,
      message: 'Document replaced successfully',
      syncStatus: sharepointResult?.success ? 'synced' : 'pending'
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (error) {
    console.error('Document replacement error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Failed to replace document' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

// Delete document
async function deletePartnerDocumentHandler(partner, documentId, env) {
  try {
    // Get document details
    const doc = await env.epc_form_data.prepare(`
      SELECT pd.*, pp.project_id
      FROM project_documents pd
      JOIN project_partners pp ON pd.project_id = pp.project_id
      WHERE pd.id = ? AND pp.partner_id = ? AND pp.status = 'accepted'
    `).bind(documentId, partner.partnerId).first();

    if (!doc) {
      return new Response(JSON.stringify({ success: false, error: 'Document not found or access denied' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Delete from SharePoint (disabled for staging)
    if (doc.sharepoint_path) {
      console.log(`📝 Would delete from SharePoint: ${doc.sharepoint_path} (disabled in ${env.ENVIRONMENT})`);
    }

    // Delete from R2
    await env.EPC_DOCUMENTS.delete(doc.storage_path);

    // Mark as deleted in database (soft delete)
    await env.epc_form_data.prepare(`
      UPDATE project_documents
      SET status = 'deleted', deleted_at = datetime('now'), deleted_by = ?
      WHERE id = ?
    `).bind(partner.email, documentId).run();

    return new Response(JSON.stringify({ success: true, message: 'Document deleted successfully' }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (error) {
    console.error('Document deletion error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Failed to delete document' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

// Get document versions from SharePoint
async function getDocumentVersionsHandler(partner, documentId, env) {
  try {
    const doc = await env.epc_form_data.prepare(`
      SELECT pd.*, pp.project_id
      FROM project_documents pd
      JOIN project_partners pp ON pd.project_id = pp.project_id
      WHERE pd.id = ? AND pp.partner_id = ? AND pp.status = 'accepted'
    `).bind(documentId, partner.partnerId).first();

    if (!doc) {
      return new Response(JSON.stringify({ success: false, error: 'Document not found or access denied' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    const versions = [];

    if (doc.sharepoint_path) {
      console.log(`📝 Would get versions from SharePoint: ${doc.sharepoint_path} (disabled in ${env.ENVIRONMENT})`);
      // versions.push(...sharepointVersions);
    }

    return new Response(JSON.stringify({ success: true, versions }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (error) {
    console.error('Get versions error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Failed to get document versions' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

// Download document
async function downloadPartnerDocumentHandler(partner, documentId, env) {
  try {
    const doc = await env.epc_form_data.prepare(`
      SELECT pd.*, pp.project_id
      FROM project_documents pd
      JOIN project_partners pp ON pd.project_id = pp.project_id
      WHERE pd.id = ? AND pp.partner_id = ? AND pp.status = 'accepted'
    `).bind(documentId, partner.partnerId).first();

    if (!doc) {
      return new Response('Document not found or access denied', { status: 404 });
    }

    // Get file from R2
    const object = await env.EPC_DOCUMENTS.get(doc.storage_path);

    if (!object) {
      return new Response('File not found in storage', { status: 404 });
    }

    return new Response(object.body, {
      headers: {
        'Content-Type': doc.content_type,
        'Content-Disposition': `attachment; filename="${doc.original_filename}"`,
        'Content-Length': doc.file_size
      }
    });

  } catch (error) {
    console.error('Document download error:', error);
    return new Response('Failed to download document', { status: 500 });
  }
}

// Sync documents from SharePoint
async function syncSharePointDocumentsHandler(partner, projectId, request, env) {
  try {
    // Verify partner has access to this project
    const projectAccess = await env.epc_form_data.prepare(`
      SELECT pp.id, p.project_code
      FROM project_partners pp
      JOIN projects p ON pp.project_id = p.id
      WHERE pp.project_id = ? AND pp.partner_id = ? AND pp.status = 'accepted'
    `).bind(projectId, partner.partnerId).first();

    if (!projectAccess) {
      return new Response(JSON.stringify({ success: false, error: 'Access denied to this project' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // SharePoint sync disabled for staging reliability
    const syncResult = {
      success: false,
      error: `SharePoint sync disabled in ${env.ENVIRONMENT}`
    };
    console.log(`📝 SharePoint sync requested for ${projectAccess.project_code}/${partner.companyName} (disabled)`);

    return new Response(JSON.stringify(syncResult), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });

  } catch (error) {
    console.error('SharePoint sync error:', error);
    return new Response(JSON.stringify({ success: false, error: 'Sync failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}
