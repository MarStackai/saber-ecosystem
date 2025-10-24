/**
 * SharePoint Document Library Sync
 * Handles two-way synchronization between Cloudflare R2 and SharePoint document libraries
 * Includes version control and document oversight features
 */

class SharePointDocumentSync {
  constructor(env) {
    this.env = env
    this.siteUrl = 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners'
    this.documentLibrary = 'Shared Documents' // Using Shared Documents as per existing working implementation
    this.clientId = 'bbbfe394-7cff-4ac9-9e01-33cbf116b930'
  }

  /**
   * Get SharePoint access token using certificate authentication
   */
  async getAccessToken() {
    try {
      const certificate = this.env.SHAREPOINT_CERTIFICATE
      const certificatePassword = this.env.SHAREPOINT_CERTIFICATE_PASSWORD
      const tenantId = this.env.SHAREPOINT_TENANT_ID

      const tokenUrl = `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`

      const formData = new FormData()
      formData.append('client_id', this.clientId)
      formData.append('scope', 'https://graph.microsoft.com/.default')
      formData.append('client_assertion_type', 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer')
      formData.append('client_assertion', await this.createClientAssertion())
      formData.append('grant_type', 'client_credentials')

      const response = await fetch(tokenUrl, {
        method: 'POST',
        body: formData
      })

      const tokenData = await response.json()
      return tokenData.access_token
    } catch (error) {
      console.error('Failed to get SharePoint access token:', error)
      throw error
    }
  }

  /**
   * Create JWT client assertion for certificate authentication
   */
  async createClientAssertion() {
    // This would use the certificate to create a JWT assertion
    // For now, return a placeholder - would need proper JWT library in Workers
    return 'placeholder-jwt-assertion'
  }

  /**
   * Create folder structure in SharePoint for a tender
   * Follows the exact EPC_Tender_Docs template structure
   */
  async createTenderFolderStructure(tenderId, partnerName = null) {
    try {
      const accessToken = await this.getAccessToken()
      const baseHeaders = {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }

      // Create base tender folder: EPC_Tender_Docs/{tenderId}/{partnerName} or just EPC_Tender_Docs/{tenderId}
      const baseFolderPath = partnerName
        ? `EPC_Tender_Docs/${tenderId}/${partnerName}`
        : `EPC_Tender_Docs/${tenderId}`

      await this.createSharePointFolder(baseFolderPath, baseHeaders)

      // Create all the subfolders based on the exact template structure
      const folderStructure = [
        'EPC Uploads',
        'EPC Uploads/01. Design',
        'EPC Uploads/02. Grid',
        'EPC Uploads/02. Grid/G99 Application',
        'EPC Uploads/02. Grid/G99 Offer',
        'EPC Uploads/03. Planning',
        'EPC Uploads/03. Planning/Planning Application',
        'EPC Uploads/03. Planning/Planning Decision',
        'EPC Uploads/04. Project Delivery',
        'EPC Uploads/04. Project Delivery/01. EPC Contract',
        'EPC Uploads/04. Project Delivery/02. O&M Contract',
        'EPC Uploads/04. Project Delivery/03. Final Design',
        'EPC Uploads/04. Project Delivery/04. Pre-construction Pack',
        'EPC Uploads/04. Project Delivery/05. EPC Invoices',
        'EPC Uploads/04. Project Delivery/06. Handover Pack',
        'EPC Uploads/05. Survey',
        'EPC Uploads/05. Survey/Site Survey',
        'EPC Uploads/05. Survey/Media'
      ]

      for (const folder of folderStructure) {
        const fullFolderPath = `${baseFolderPath}/${folder}`
        await this.createSharePointFolder(fullFolderPath, baseHeaders)
      }

      console.log(`✅ Created SharePoint folder structure for ${baseFolderPath}`)
      return { success: true, path: baseFolderPath }

    } catch (error) {
      console.error('Failed to create SharePoint folder structure:', error)
      return { success: false, error: error.message }
    }
  }

  /**
   * Create a folder in SharePoint document library
   */
  async createSharePointFolder(folderPath, headers) {
    const encodedPath = encodeURIComponent(folderPath)
    const createFolderUrl = `${this.siteUrl}/_api/web/folders`

    const folderData = {
      '__metadata': { 'type': 'SP.Folder' },
      'ServerRelativeUrl': `/sites/SaberEPCPartners/${folderPath}`
    }

    const response = await fetch(createFolderUrl, {
      method: 'POST',
      headers: {
        ...headers,
        'X-RequestDigest': await this.getFormDigest(headers)
      },
      body: JSON.stringify(folderData)
    })

    if (!response.ok && response.status !== 409) { // 409 = folder already exists
      throw new Error(`Failed to create folder ${folderPath}: ${response.statusText}`)
    }

    return response.status === 409 ? 'exists' : 'created'
  }

  /**
   * Check if folder exists in SharePoint
   */
  async checkFolderExists(folderPath, headers) {
    try {
      const checkUrl = `${this.siteUrl}/_api/web/GetFolderByServerRelativeUrl('/sites/SaberEPCPartners/${this.documentLibrary}/${folderPath}')`

      const response = await fetch(checkUrl, {
        method: 'GET',
        headers
      })

      return response.ok
    } catch (error) {
      return false
    }
  }

  /**
   * Get form digest for SharePoint operations
   */
  async getFormDigest(headers) {
    const digestUrl = `${this.siteUrl}/_api/contextinfo`

    const response = await fetch(digestUrl, {
      method: 'POST',
      headers
    })

    const data = await response.json()
    return data.FormDigestValue
  }

  /**
   * Upload document to SharePoint with versioning support
   */
  async uploadToSharePoint(tenderId, partnerName, folderPath, fileName, fileBuffer, metadata = {}) {
    try {
      const accessToken = await this.getAccessToken()
      const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/json'
      }

      // Ensure folder structure exists (only create once per tender)
      const basePath = partnerName
        ? `EPC_Tender_Docs/${tenderId}/${partnerName}`
        : `EPC_Tender_Docs/${tenderId}`

      // Only create folder structure if it doesn't exist
      const folderExists = await this.checkFolderExists(basePath, headers)
      if (!folderExists) {
        await this.createTenderFolderStructure(tenderId, partnerName)
      }

      // Upload file - use the EPC_Tender_Docs structure
      const sharePointPath = `${this.documentLibrary}/${basePath}/EPC Uploads/${folderPath}`
      const uploadUrl = `${this.siteUrl}/_api/web/GetFolderByServerRelativeUrl('${encodeURIComponent(sharePointPath)}')/Files/add(url='${encodeURIComponent(fileName)}',overwrite=true)`

      const uploadResponse = await fetch(uploadUrl, {
        method: 'POST',
        headers: {
          ...headers,
          'X-RequestDigest': await this.getFormDigest(headers),
          'Content-Type': 'application/octet-stream'
        },
        body: fileBuffer
      })

      if (!uploadResponse.ok) {
        throw new Error(`SharePoint upload failed: ${uploadResponse.statusText}`)
      }

      const uploadResult = await uploadResponse.json()

      // Update file metadata if provided
      if (Object.keys(metadata).length > 0) {
        await this.updateFileMetadata(uploadResult.ServerRelativeUrl, metadata, headers)
      }

      console.log(`✅ Uploaded ${fileName} to SharePoint: ${sharePointPath}`)

      return {
        success: true,
        sharePointUrl: uploadResult.ServerRelativeUrl,
        sharePointId: uploadResult.UniqueId,
        version: '1.0'
      }

    } catch (error) {
      console.error('SharePoint upload error:', error)
      return { success: false, error: error.message }
    }
  }

  /**
   * Update file metadata in SharePoint
   */
  async updateFileMetadata(serverRelativeUrl, metadata, headers) {
    const metadataUrl = `${this.siteUrl}/_api/web/GetFileByServerRelativeUrl('${encodeURIComponent(serverRelativeUrl)}')/ListItemAllFields`

    const updateData = {
      '__metadata': { 'type': 'SP.Data.Shared_x0020_DocumentsItem' },
      ...metadata
    }

    await fetch(metadataUrl, {
      method: 'PATCH',
      headers: {
        ...headers,
        'X-RequestDigest': await this.getFormDigest(headers),
        'X-HTTP-Method': 'MERGE',
        'IF-MATCH': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    })
  }

  /**
   * Download document from SharePoint
   */
  async downloadFromSharePoint(serverRelativeUrl) {
    try {
      const accessToken = await this.getAccessToken()
      const downloadUrl = `${this.siteUrl}/_api/web/GetFileByServerRelativeUrl('${encodeURIComponent(serverRelativeUrl)}')/$value`

      const response = await fetch(downloadUrl, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to download from SharePoint: ${response.statusText}`)
      }

      return await response.arrayBuffer()

    } catch (error) {
      console.error('SharePoint download error:', error)
      throw error
    }
  }

  /**
   * Get document versions from SharePoint
   */
  async getDocumentVersions(serverRelativeUrl) {
    try {
      const accessToken = await this.getAccessToken()
      const versionsUrl = `${this.siteUrl}/_api/web/GetFileByServerRelativeUrl('${encodeURIComponent(serverRelativeUrl)}')/Versions`

      const response = await fetch(versionsUrl, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Accept': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to get versions: ${response.statusText}`)
      }

      const data = await response.json()
      return data.value.map(version => ({
        versionLabel: version.VersionLabel,
        created: version.Created,
        createdBy: version.CreatedBy?.Title || 'Unknown',
        size: version.Size,
        url: version.Url
      }))

    } catch (error) {
      console.error('Failed to get document versions:', error)
      return []
    }
  }

  /**
   * Delete document from SharePoint
   */
  async deleteFromSharePoint(serverRelativeUrl) {
    try {
      const accessToken = await this.getAccessToken()
      const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/json'
      }

      const deleteUrl = `${this.siteUrl}/_api/web/GetFileByServerRelativeUrl('${encodeURIComponent(serverRelativeUrl)}')`

      const response = await fetch(deleteUrl, {
        method: 'DELETE',
        headers: {
          ...headers,
          'X-RequestDigest': await this.getFormDigest(headers),
          'IF-MATCH': '*'
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to delete from SharePoint: ${response.statusText}`)
      }

      return { success: true }

    } catch (error) {
      console.error('SharePoint delete error:', error)
      return { success: false, error: error.message }
    }
  }

  /**
   * Sync documents from SharePoint to R2 (pull sync)
   */
  async syncFromSharePoint(tenderId, partnerName) {
    try {
      const accessToken = await this.getAccessToken()
      const folderPath = `${this.documentLibrary}/${tenderId}/${partnerName}`
      const listItemsUrl = `${this.siteUrl}/_api/web/GetFolderByServerRelativeUrl('${encodeURIComponent(folderPath)}')/Files`

      const response = await fetch(listItemsUrl, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Accept': 'application/json'
        }
      })

      if (!response.ok) {
        return { success: false, error: 'Folder not found in SharePoint' }
      }

      const data = await response.json()
      const syncResults = []

      for (const file of data.value) {
        try {
          // Download file from SharePoint
          const fileBuffer = await this.downloadFromSharePoint(file.ServerRelativeUrl)

          // Upload to R2
          const r2Key = `documents/${tenderId}/${partnerName}/${file.Name}`
          await this.env.EPC_DOCUMENTS.put(r2Key, fileBuffer, {
            httpMetadata: {
              contentType: file.MimeType || 'application/octet-stream'
            },
            customMetadata: {
              source: 'sharepoint',
              sharePointId: file.UniqueId,
              syncedAt: new Date().toISOString()
            }
          })

          syncResults.push({ file: file.Name, status: 'synced' })

        } catch (fileError) {
          console.error(`Failed to sync file ${file.Name}:`, fileError)
          syncResults.push({ file: file.Name, status: 'failed', error: fileError.message })
        }
      }

      return { success: true, results: syncResults }

    } catch (error) {
      console.error('SharePoint sync error:', error)
      return { success: false, error: error.message }
    }
  }

  /**
   * Get document metadata and permissions from SharePoint
   */
  async getDocumentMetadata(serverRelativeUrl) {
    try {
      const accessToken = await this.getAccessToken()
      const metadataUrl = `${this.siteUrl}/_api/web/GetFileByServerRelativeUrl('${encodeURIComponent(serverRelativeUrl)}')/ListItemAllFields`

      const response = await fetch(metadataUrl, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Accept': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to get metadata: ${response.statusText}`)
      }

      const data = await response.json()
      return {
        id: data.Id,
        title: data.Title,
        created: data.Created,
        modified: data.Modified,
        createdBy: data.Author?.Title,
        modifiedBy: data.Editor?.Title,
        fileSize: data.File_x0020_Size,
        version: data.OData__UIVersionString,
        checkoutUser: data.CheckoutUser?.Title,
        approval: data.OData__ModerationStatus
      }

    } catch (error) {
      console.error('Failed to get document metadata:', error)
      return null
    }
  }
}

export default SharePointDocumentSync