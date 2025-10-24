// Native Pages Function for file upload
// Replaces src/app/api/upload-file/route.js to bypass Next.js adapter issues

// Generate organized file path based on partner and document type
function generateFilePath(invitationCode, fieldName, fileName) {
  const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  
  // Determine folder based on field type
  let subfolder = 'documents';
  if (fieldName.toLowerCase().includes('logo') || fieldName.toLowerCase().includes('image')) {
    subfolder = 'logos';
  } else if (fieldName.toLowerCase().includes('certificate') || fieldName.toLowerCase().includes('cert')) {
    subfolder = 'certificates';
  } else if (fieldName.toLowerCase().includes('financial') || fieldName.toLowerCase().includes('insurance')) {
    subfolder = 'financial';
  }

  // Clean filename for storage
  const cleanFileName = fileName.replace(/[^a-zA-Z0-9.-]/g, '_');
  const fileKey = `EPC-Applications/${invitationCode}/${subfolder}/${timestamp}_${fieldName}_${cleanFileName}`;
  
  return fileKey;
}

export async function onRequest(context) {
  const { request, env } = context;
  
  if (request.method === 'POST') {
    try {
      const formData = await request.formData()
      const file = formData.get('file')
      const invitationCode = formData.get('invitationCode')
      const fieldName = formData.get('fieldName')
      
      if (!file || !invitationCode || !fieldName) {
        return new Response(JSON.stringify({
          success: false, 
          message: 'File, invitation code, and field name are required' 
        }), {
          status: 400,
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })
      }

      console.log(`📁 Uploading ${fieldName} for invitation: ${invitationCode}`)
      console.log(`📄 File: ${file.name} (${file.size} bytes)`)

      // Generate organized file path
      const fileKey = generateFilePath(invitationCode, fieldName, file.name);
      
      // Create metadata object
      const uploadMetadata = {
        invitationCode: invitationCode,
        fieldName: fieldName,
        originalName: file.name,
        contentType: file.type,
        uploadDate: new Date().toISOString(),
        userAgent: request.headers.get('user-agent'),
        uploadIP: request.headers.get('cf-connecting-ip'),
        size: file.size
      };
      
      // Upload to R2 storage
      const uploadResult = await env.EPC_PARTNER_FILES.put(fileKey, file, {
        httpMetadata: {
          contentType: file.type,
          contentDisposition: `inline; filename="${file.name}"`
        },
        customMetadata: uploadMetadata
      });

      if (!uploadResult) {
        return new Response(JSON.stringify({
          success: false, 
          message: 'Failed to upload file to storage. Please try again.' 
        }), {
          status: 500,
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })
      }

      // Record file upload in D1 database
      try {
        await env.epc_form_data.prepare(`
          INSERT INTO application_files (
            invitation_code, field_name, original_filename, file_size, 
            content_type, storage_path, upload_date
          ) VALUES (?, ?, ?, ?, ?, ?, ?)
        `).bind(
          invitationCode,
          fieldName,
          file.name,
          file.size,
          file.type,
          fileKey,
          new Date().toISOString()
        ).run()
        
        console.log(`📝 File upload recorded in D1: ${fileKey}`)
      } catch (dbError) {
        console.warn('⚠️  Could not record file in D1 (using fallback):', dbError.message)
        // Continue without failing - file is uploaded to R2 successfully
      }

      console.log('✅ File uploaded successfully to R2:', fileKey)

      return new Response(JSON.stringify({
        success: true,
        message: 'File uploaded successfully',
        fileKey: fileKey,
        fieldName: fieldName,
        metadata: uploadMetadata,
        storagePath: fileKey
      }), {
        headers: { 
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      })

    } catch (error) {
      console.error('💥 File upload error:', error)
      return new Response(JSON.stringify({
        success: false, 
        message: 'Internal server error during file upload.',
        error: error.message
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
      message: 'File Upload API endpoint',
      usage: 'POST multipart/form-data with file, invitationCode, and fieldName'
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