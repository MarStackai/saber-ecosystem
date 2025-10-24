// R2 Storage helpers for EPC Portal file management
// Organized folder structure for partner documents

export class R2Helper {
  constructor(r2Bucket) {
    this.bucket = r2Bucket;
  }

  // Generate organized file path based on partner and document type
  generateFilePath(invitationCode, fieldName, fileName) {
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

  // Upload file to R2 with organized structure
  async uploadFile(invitationCode, fieldName, file, metadata = {}) {
    try {
      const fileKey = this.generateFilePath(invitationCode, fieldName, file.name);
      
      // Convert file to ArrayBuffer
      const arrayBuffer = await file.arrayBuffer();
      
      // Upload to R2
      await this.bucket.put(fileKey, arrayBuffer, {
        httpMetadata: {
          contentType: file.type,
          cacheControl: 'max-age=31536000', // 1 year cache
        },
        customMetadata: {
          originalName: file.name,
          fieldName: fieldName,
          invitationCode: invitationCode,
          uploadDate: new Date().toISOString(),
          fileSize: file.size.toString(),
          ...metadata
        }
      });

      console.log(`✅ File uploaded to R2: ${fileKey}`);

      return {
        success: true,
        fileKey: fileKey,
        url: `https://epc-partner-files.7c1df500c062ab6ec160bdc6fd06d4b8.r2.cloudflarestorage.com/${fileKey}`,
        metadata: {
          originalName: file.name,
          fieldName: fieldName,
          size: file.size,
          uploadDate: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('❌ R2 upload error:', error);
      throw error;
    }
  }

  // List files for a specific partner
  async listPartnerFiles(invitationCode) {
    try {
      const prefix = `EPC-Applications/${invitationCode}/`;
      const listed = await this.bucket.list({ prefix });
      
      return listed.objects.map(obj => ({
        key: obj.key,
        size: obj.size,
        etag: obj.etag,
        uploaded: obj.uploaded,
        customMetadata: obj.customMetadata
      }));
    } catch (error) {
      console.error('❌ Error listing partner files:', error);
      return [];
    }
  }

  // Get signed URL for file access
  async getSignedUrl(fileKey, expiryMinutes = 60) {
    try {
      // For now, return public URL - in production you'd implement signed URLs
      const publicUrl = `https://epc-partner-files.7c1df500c062ab6ec160bdc6fd06d4b8.r2.cloudflarestorage.com/${fileKey}`;
      return publicUrl;
    } catch (error) {
      console.error('❌ Error generating signed URL:', error);
      throw error;
    }
  }

  // Delete file from R2
  async deleteFile(fileKey) {
    try {
      await this.bucket.delete(fileKey);
      console.log(`🗑️  Deleted file from R2: ${fileKey}`);
      return { success: true };
    } catch (error) {
      console.error('❌ Error deleting file:', error);
      throw error;
    }
  }

  // Create folder structure markers (optional - R2 creates folders implicitly)
  async initializePartnerFolders(invitationCode) {
    const folders = ['documents', 'logos', 'certificates', 'financial'];
    const results = [];

    for (const folder of folders) {
      try {
        const markerKey = `EPC-Applications/${invitationCode}/${folder}/.folder_marker`;
        await this.bucket.put(markerKey, '', {
          customMetadata: {
            type: 'folder_marker',
            created: new Date().toISOString(),
            invitationCode: invitationCode
          }
        });
        results.push({ folder, success: true });
      } catch (error) {
        console.error(`❌ Error creating folder marker for ${folder}:`, error);
        results.push({ folder, success: false, error: error.message });
      }
    }

    return results;
  }
}

// Helper function to get R2 instance from environment
export function getR2Storage(env) {
  if (env.EPC_PARTNER_FILES) {
    return new R2Helper(env.EPC_PARTNER_FILES);
  }
  
  // Development fallback - log warning
  console.log('⚠️  R2 storage not available, using mock helper');
  return createMockR2Helper();
}

// Mock R2 helper for development
function createMockR2Helper() {
  const mockStorage = new Map();
  
  return {
    async uploadFile(invitationCode, fieldName, file, metadata = {}) {
      const fileKey = `EPC-Applications/${invitationCode}/${fieldName}_${file.name}`;
      mockStorage.set(fileKey, {
        file,
        metadata: {
          originalName: file.name,
          fieldName,
          size: file.size,
          uploadDate: new Date().toISOString(),
          ...metadata
        }
      });
      
      console.log(`📝 Mock: File uploaded: ${fileKey}`);
      return {
        success: true,
        fileKey,
        url: `mock://storage/${fileKey}`,
        metadata: {
          originalName: file.name,
          fieldName,
          size: file.size,
          uploadDate: new Date().toISOString()
        }
      };
    },

    async listPartnerFiles(invitationCode) {
      const prefix = `EPC-Applications/${invitationCode}/`;
      const files = [];
      for (const [key, value] of mockStorage.entries()) {
        if (key.startsWith(prefix)) {
          files.push({
            key,
            size: value.file.size,
            customMetadata: value.metadata
          });
        }
      }
      console.log(`📊 Mock: Listed ${files.length} files for ${invitationCode}`);
      return files;
    },

    async getSignedUrl(fileKey, expiryMinutes = 60) {
      return `mock://storage/${fileKey}?expires=${Date.now() + (expiryMinutes * 60000)}`;
    },

    async deleteFile(fileKey) {
      mockStorage.delete(fileKey);
      console.log(`🗑️  Mock: Deleted file: ${fileKey}`);
      return { success: true };
    },

    async initializePartnerFolders(invitationCode) {
      const folders = ['documents', 'logos', 'certificates', 'financial'];
      console.log(`📁 Mock: Initialized folders for ${invitationCode}:`, folders);
      return folders.map(folder => ({ folder, success: true }));
    }
  };
}