// SharePoint Integration for EPC Partner Onboarding Form
// This script handles the connection between the form and SharePoint

class SharePointConnector {
    constructor(config) {
        this.siteUrl = config.siteUrl || 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners';
        this.listName = config.listName || 'EPC Onboarding';
        this.clientId = config.clientId || 'bbbfe394-7cff-4ac9-9e01-33cbf116b930';
        this.tenant = config.tenant || 'saberrenewables.onmicrosoft.com';
        this.accessToken = null;
    }

    // Initialize MSAL for authentication
    async initialize() {
        // For production, implement MSAL authentication
        // This is a placeholder for the authentication flow
        console.log('Initializing SharePoint connection...');
    }

    // Submit form data to SharePoint list
    async submitForm(formData, files) {
        try {
            // Map form fields to SharePoint columns
            const listItemData = this.mapFormToSharePoint(formData);
            
            // Create list item
            const itemId = await this.createListItem(listItemData);
            
            // Upload attachments if any
            if (files && files.length > 0) {
                await this.uploadAttachments(itemId, files);
            }
            
            return {
                success: true,
                itemId: itemId,
                message: 'Application submitted successfully'
            };
        } catch (error) {
            console.error('SharePoint submission error:', error);
            throw error;
        }
    }

    // Map form fields to SharePoint column names
    mapFormToSharePoint(formData) {
        return {
            'CompanyName': formData.companyName,
            'TradingName': formData.tradingName,
            'RegisteredOffice': formData.registeredOffice,
            'CompanyRegNo': formData.companyRegNo,
            'VATNo': formData.vatNo,
            'YearsTrading': parseInt(formData.yearsTrading),
            'PrimaryContactName': formData.primaryContactName,
            'PrimaryContactEmail': formData.primaryContactEmail,
            'PrimaryContactPhone': formData.primaryContactPhone,
            'CoverageRegion': formData.coverageRegion ? { results: formData.coverageRegion } : null,
            'ISOStandards': formData.isoStandards ? { results: formData.isoStandards } : null,
            'ActsAsPrincipalContractor': formData.actsAsPrincipalContractor,
            'ActsAsPrincipalDesigner': formData.actsAsPrincipalDesigner,
            'HasGDPRPolicy': formData.hasGDPRPolicy,
            'HSEQIncidentsLast5y': parseInt(formData.hsqIncidents) || 0,
            'RIDDORLast3y': parseInt(formData.riddor) || 0,
            'NotesOrClarifications': formData.notes,
            'AgreeToSaberTerms': 'Yes',
            'Status': 'Submitted'
        };
    }

    // Create list item via REST API
    async createListItem(data) {
        const endpoint = `${this.siteUrl}/_api/web/lists/getbytitle('${this.listName}')/items`;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Accept': 'application/json;odata=verbose',
                'Content-Type': 'application/json;odata=verbose',
                'Authorization': `Bearer ${this.accessToken}`,
                'X-RequestDigest': await this.getRequestDigest()
            },
            body: JSON.stringify({
                '__metadata': { 'type': this.getListItemType() },
                ...data
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to create list item: ${response.statusText}`);
        }

        const result = await response.json();
        return result.d.Id;
    }

    // Upload attachments to list item
    async uploadAttachments(itemId, files) {
        for (const file of files) {
            await this.uploadSingleAttachment(itemId, file);
        }
    }

    // Upload single attachment
    async uploadSingleAttachment(itemId, file) {
        const endpoint = `${this.siteUrl}/_api/web/lists/getbytitle('${this.listName}')/items(${itemId})/AttachmentFiles/add(FileName='${file.name}')`;
        
        const arrayBuffer = await this.fileToArrayBuffer(file);
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Accept': 'application/json;odata=verbose',
                'Authorization': `Bearer ${this.accessToken}`,
                'X-RequestDigest': await this.getRequestDigest()
            },
            body: arrayBuffer
        });

        if (!response.ok) {
            console.error(`Failed to upload attachment ${file.name}`);
        }
    }

    // Convert file to array buffer
    fileToArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsArrayBuffer(file);
        });
    }

    // Get request digest for SharePoint REST API
    async getRequestDigest() {
        const endpoint = `${this.siteUrl}/_api/contextinfo`;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Accept': 'application/json;odata=verbose',
                'Authorization': `Bearer ${this.accessToken}`
            }
        });

        const data = await response.json();
        return data.d.GetContextWebInformation.FormDigestValue;
    }

    // Get list item type for metadata
    getListItemType() {
        return `SP.Data.${this.listName.replace(/\s/g, '_x0020_')}ListItem`;
    }

    // Alternative: Submit via Power Automate HTTP endpoint
    async submitViaPowerAutomate(formData, files) {
        // Power Automate flow endpoint (configured in Power Automate)
        const flowUrl = 'https://prod-xx.westeurope.logic.azure.com/workflows/...';
        
        // Prepare data for Power Automate
        const payload = {
            formData: this.mapFormToSharePoint(formData),
            attachments: await this.prepareAttachmentsForFlow(files)
        };
        
        const response = await fetch(flowUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Failed to submit via Power Automate');
        }

        return await response.json();
    }

    // Prepare attachments for Power Automate
    async prepareAttachmentsForFlow(files) {
        const attachments = [];
        
        for (const file of files) {
            const base64 = await this.fileToBase64(file);
            attachments.push({
                name: file.name,
                contentBytes: base64
            });
        }
        
        return attachments;
    }

    // Convert file to base64
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const base64 = e.target.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
}

// Export for use in main script
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SharePointConnector;
}

// Usage example:
/*
const connector = new SharePointConnector({
    siteUrl: 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners',
    listName: 'EPC Onboarding',
    clientId: 'bbbfe394-7cff-4ac9-9e01-33cbf116b930',
    tenant: 'saberrenewables.onmicrosoft.com'
});

await connector.initialize();
const result = await connector.submitForm(formData, uploadedFiles);
*/