// Native Pages Function for EPC application submission
// Replaces src/app/api/epc-application/route.js to bypass Next.js adapter issues
// Updated for simplified SharePoint workflow

// Helper function to submit application to D1 database
async function submitApplicationToD1(db, invitationCode, requestData, files) {
  const now = new Date().toISOString();
  const referenceNumber = `EPC-${Date.now()}-${invitationCode.substring(0, 4).toUpperCase()}`;

  try {
    // Store in applications table
    const applicationData = {
      invitation_code: invitationCode,
      reference_number: referenceNumber,
      submission_date: now,
      status: 'pending',
      form_data: JSON.stringify(requestData),
      files_data: JSON.stringify(files || {}),
      processing_notes: 'Submitted via React Portal'
    };

    await db.prepare(`
      INSERT INTO applications (
        invitation_code, reference_number, submission_date, status,
        form_data, files_data, processing_notes,
        company_name, primary_contact_name, primary_contact_email,
        company_website, company_phone, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      applicationData.invitation_code,
      applicationData.reference_number,
      applicationData.submission_date,
      applicationData.status,
      applicationData.form_data,
      applicationData.files_data,
      applicationData.processing_notes,
      requestData.companyInfo?.companyName || requestData.companyName || '',
      requestData.primaryContact?.name || requestData.contactName || '',
      requestData.primaryContact?.email || requestData.email || '',
      requestData.companyInfo?.website || requestData.website || '',
      requestData.companyInfo?.phone || requestData.phone || '',
      now,
      now
    ).run();

    console.log(`✅ Application stored in D1: ${referenceNumber}`);
    return { success: true, referenceNumber };
  } catch (error) {
    console.error('❌ D1 storage error:', error);
    throw error;
  }
}

// Helper function to create SharePoint Operations Handoff item
async function createOperationsHandoff(requestData, referenceNumber, invitationCode) {
  const handoffData = {
    // Basic company info for operations review
    CompanyName: requestData.companyInfo?.companyName || requestData.companyName || '',
    PrimaryContactName: requestData.primaryContact?.name || requestData.contactName || '',
    PrimaryContactEmail: requestData.primaryContact?.email || requestData.email || '',
    PrimaryContactPhone: requestData.companyInfo?.phone || requestData.phone || '',
    InvitationCode: invitationCode,
    ApplicationSubmissionDate: new Date().toISOString(),
    
    // Link back to full application data
    PortalApplicationLink: {
      Url: `https://cb781b90.saber-epc-portal.pages.dev/admin/application/${referenceNumber}`,
      Description: `View Full Application: ${referenceNumber}`
    },
    ApplicationReference: referenceNumber,
    
    // Set initial review status
    ReviewStatus: 'Pending Review',
    ReviewPriority: 'Normal',
    FinalStatus: 'Active',
    
    // System notes
    OperationsNotes: `Application submitted via EPC Partner Portal on ${new Date().toLocaleDateString()}. Full form data and file uploads stored in Cloudflare D1/R2. Review required.`
  };

  try {
    // Create SharePoint list item via existing API
    const response = await fetch('https://epc-api-worker.robjamescarroll.workers.dev/create-operations-handoff', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Saber-EPC-Portal/1.0'
      },
      body: JSON.stringify(handoffData),
      signal: AbortSignal.timeout(10000) // 10 second timeout
    });

    if (!response.ok) {
      throw new Error(`SharePoint API error: ${response.status}`);
    }

    const result = await response.json();
    console.log('✅ Operations handoff created:', result);
    return result;
  } catch (error) {
    console.error('❌ Operations handoff creation failed:', error);
    throw error;
  }
}

// Helper function to update invitation status
async function updateInvitationStatus(invitationCode) {
  try {
    const updateData = {
      InvitationCode: invitationCode,
      InvitationStatus: 'Completed',
      ApplicationSubmitted: true,
      SubmissionDate: new Date().toISOString()
    };

    const response = await fetch('https://epc-api-worker.robjamescarroll.workers.dev/update-invitation-status', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Saber-EPC-Portal/1.0'
      },
      body: JSON.stringify(updateData),
      signal: AbortSignal.timeout(5000) // 5 second timeout
    });

    if (response.ok) {
      const result = await response.json();
      console.log('✅ Invitation status updated:', result);
      return result;
    } else {
      console.error('⚠️ Invitation status update failed:', response.status);
    }
  } catch (error) {
    console.error('⚠️ Invitation status update error:', error);
  }
}

// Helper function to clear draft
async function clearDraft(db, invitationCode) {
  try {
    await db.prepare(`
      DELETE FROM draft_data 
      WHERE invitation_code = ?
    `).bind(invitationCode).run();

    console.log(`✅ Draft cleared: ${invitationCode}`);
    return { success: true };
  } catch (error) {
    console.error('❌ Draft clear error:', error);
    throw error;
  }
}

// Helper function to update application status
async function updateApplicationStatus(db, invitationCode, status, notes = null) {
  try {
    await db.prepare(`
      UPDATE applications 
      SET status = ?, updated_at = ?, processing_notes = COALESCE(?, processing_notes)
      WHERE invitation_code = ?
    `).bind(
      status,
      new Date().toISOString(),
      notes,
      invitationCode
    ).run();

    console.log(`✅ Application status updated: ${invitationCode} -> ${status}`);
  } catch (error) {
    console.error('❌ Status update error:', error);
    throw error;
  }
}

export async function onRequest(context) {
  const { request, env } = context;
  
  if (request.method === 'POST') {
    try {
      const requestData = await request.json()
      
      console.log('📋 EPC Application submitted:', {
        companyName: requestData.companyInfo?.companyName || requestData.companyName,
        email: requestData.primaryContact?.email || requestData.email,
        invitationCode: requestData.submission?.invitationCode || requestData.invitationCode,
        timestamp: new Date().toISOString()
      })

      // Extract invitation code
      const invitationCode = requestData.submission?.invitationCode || 
                            requestData.invitationCode || 
                            `temp-${Date.now()}`

      // Step 1: Store complete application in D1 database
      console.log('📦 Step 1: Storing application in D1...')
      const d1Result = await submitApplicationToD1(
        env.epc_form_data, 
        invitationCode, 
        requestData, 
        requestData.files || {}
      )
      
      console.log('✅ D1 storage complete:', d1Result.referenceNumber)

      // Step 2: Create operations handoff item in SharePoint
      console.log('📤 Step 2: Creating operations handoff...')
      try {
        const handoffResult = await createOperationsHandoff(
          requestData, 
          d1Result.referenceNumber, 
          invitationCode
        )
        console.log('✅ Operations handoff created successfully')

        // Step 3: Update invitation status
        console.log('📧 Step 3: Updating invitation status...')
        await updateInvitationStatus(invitationCode)

        // Step 4: Update application status to completed
        await updateApplicationStatus(
          env.epc_form_data, 
          invitationCode, 
          'submitted', 
          'Application submitted and operations handoff created'
        )

        // Step 5: Clear draft after successful submission
        try {
          await clearDraft(env.epc_form_data, invitationCode)
          console.log('✅ Draft cleared after successful submission')
        } catch (draftError) {
          console.error('⚠️ Failed to clear draft:', draftError)
        }
        
        return new Response(JSON.stringify({
          success: true,
          message: 'Application submitted successfully! Operations team has been notified.',
          referenceNumber: d1Result.referenceNumber,
          applicationId: d1Result.referenceNumber,
          processingStatus: 'submitted_to_operations',
          nextSteps: 'You will receive an email confirmation shortly. Our operations team will review your application and contact you within 2-3 business days.'
        }), {
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })
        
      } catch (handoffError) {
        console.error('⚠️ Operations handoff failed, application still stored:', handoffError)
        
        // Update status to indicate manual handoff needed
        await updateApplicationStatus(
          env.epc_form_data, 
          invitationCode, 
          'pending_handoff', 
          'Application submitted but operations handoff needs manual processing'
        )
        
        return new Response(JSON.stringify({
          success: true,
          message: 'Application received and saved successfully!',
          referenceNumber: d1Result.referenceNumber,
          applicationId: d1Result.referenceNumber,
          processingStatus: 'queued_for_review',
          nextSteps: 'Your application has been saved. You will receive confirmation once our team processes it.'
        }), {
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })
      }
      
    } catch (error) {
      console.error('💥 Critical error in EPC application submission:', error)
      return new Response(JSON.stringify({
        success: false, 
        message: 'Unable to process your application at this time. Please try again in a few minutes.',
        error: 'Submission processing error'
      }), {
        status: 500,
        headers: { 
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      })
    }
  } else if (request.method === 'GET') {
    return new Response(JSON.stringify({
      message: 'EPC Application Submission API',
      usage: 'POST with application data to submit',
      workflow: 'D1 storage → SharePoint handoff → Email notifications',
      version: '2.0 (Simplified SharePoint Integration)'
    }), {
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      }
    })
  } else {
    return new Response(JSON.stringify({
      message: 'Method not allowed'
    }), {
      status: 405,
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      }
    })
  }
}