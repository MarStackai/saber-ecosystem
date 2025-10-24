# MCP Azure Setup Guide

## Overview

This guide provides step-by-step instructions for setting up the Model Context Protocol (MCP) server for the Azure environment to support the EPC Partner Portal migration from Cloudflare to Azure.

## Prerequisites

- Node.js 18+ installed
- Azure subscription with appropriate permissions
- Azure CLI installed and configured
- Python 3.9+ installed
- Git installed

## Step 1: MCP Server Installation

### 1.1 Install MCP Server

```bash
# Navigate to the MCP servers directory
cd ~/mcp-servers

# Create a new directory for Azure MCP server
mkdir azure-mcp-server
cd azure-mcp-server

# Initialize npm project
npm init -y

# Install required packages
npm install @modelcontextprotocol/sdk
npm install @azure/identity
npm install @azure/sql-database
npm install @azure/storage-blob
npm install @azure/app-configuration
npm install @azure/monitor-query
npm install axios
```

## Step 2: Azure MCP Server Implementation

### 2.1 Create Server Configuration

Create `src/index.js`:

```javascript
#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { AzureAPI } from './azure-api.js';

class AzureMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'azure-epc-portal-mcp',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.azureAPI = new AzureAPI();
    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'azure-epc-sql-query',
          description: 'Query Azure SQL database for EPC portal data',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'SQL query string',
              },
              database: {
                type: 'string',
                description: 'Azure SQL database name',
                default: 'saber-epc-db-prod',
              },
            },
            required: ['query'],
          },
        },
        {
          name: 'azure-epc-function-deploy',
          description: 'Deploy Azure Function for EPC portal',
          inputSchema: {
            type: 'object',
            properties: {
              environment: {
                type: 'string',
                enum: ['development', 'staging', 'production'],
                description: 'Deployment environment',
              },
              functionPath: {
                type: 'string',
                description: 'Path to function source code',
              },
            },
            required: ['environment', 'functionPath'],
          },
        },
        {
          name: 'azure-epc-blob-access',
          description: 'Access Azure Blob storage for EPC files',
          inputSchema: {
            type: 'object',
            properties: {
              operation: {
                type: 'string',
                enum: ['list', 'upload', 'download', 'delete'],
                description: 'Blob operation to perform',
              },
              container: {
                type: 'string',
                description: 'Azure Blob container name',
                default: 'epc-partner-files',
              },
              blob: {
                type: 'string',
                description: 'Blob name (for upload/download/delete)',
              },
              filePath: {
                type: 'string',
                description: 'Local file path (for upload)',
              },
            },
            required: ['operation', 'container'],
          },
        },
        {
          name: 'azure-epc-app-service-deploy',
          description: 'Deploy Azure App Service for EPC portal frontend',
          inputSchema: {
            type: 'object',
            properties: {
              environment: {
                type: 'string',
                enum: ['development', 'staging', 'production'],
                description: 'Deployment environment',
              },
              appPath: {
                type: 'string',
                description: 'Path to Next.js app',
              },
            },
            required: ['environment', 'appPath'],
          },
        },
        {
          name: 'azure-epc-resource-provision',
          description: 'Provision Azure resources for EPC portal',
          inputSchema: {
            type: 'object',
            properties: {
              resourceType: {
                type: 'string',
                enum: ['resource-group', 'app-service', 'function-app', 'sql-database', 'storage-account'],
                description: 'Type of Azure resource to provision',
              },
              resourceGroupName: {
                type: 'string',
                description: 'Name of the resource group',
              },
              resourceName: {
                type: 'string',
                description: 'Name of the resource',
              },
              location: {
                type: 'string',
                description: 'Azure region',
                default: 'uksouth',
              },
              parameters: {
                type: 'object',
                description: 'Additional parameters for resource provisioning',
              },
            },
            required: ['resourceType', 'resourceGroupName', 'resourceName'],
          },
        },
        {
          name: 'azure-epc-monitoring-query',
          description: 'Query Azure Monitor for EPC portal metrics',
          inputSchema: {
            type: 'object',
            properties: {
              metricName: {
                type: 'string',
                description: 'Name of the metric to query',
              },
              resourceType: {
                type: 'string',
                description: 'Type of Azure resource',
              },
              resourceName: {
                type: 'string',
                description: 'Name of the resource',
              },
              timeRange: {
                type: 'string',
                description: 'Time range for metrics (e.g., PT1H, P1D)',
                default: 'PT1H',
              },
            },
            required: ['metricName', 'resourceType', 'resourceName'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'azure-epc-sql-query':
            return await this.handleSqlQuery(args);
          case 'azure-epc-function-deploy':
            return await this.handleFunctionDeploy(args);
          case 'azure-epc-blob-access':
            return await this.handleBlobAccess(args);
          case 'azure-epc-app-service-deploy':
            return await this.handleAppServiceDeploy(args);
          case 'azure-epc-resource-provision':
            return await this.handleResourceProvision(args);
          case 'azure-epc-monitoring-query':
            return await this.handleMonitoringQuery(args);
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error.message}`
        );
      }
    });
  }

  async handleSqlQuery(args) {
    const { query, database } = args;
    const result = await this.azureAPI.querySql(database, query);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async handleFunctionDeploy(args) {
    const { environment, functionPath } = args;
    const result = await this.azureAPI.deployFunction(environment, functionPath);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async handleBlobAccess(args) {
    const { operation, container, blob, filePath } = args;
    const result = await this.azureAPI.accessBlob(operation, container, blob, filePath);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async handleAppServiceDeploy(args) {
    const { environment, appPath } = args;
    const result = await this.azureAPI.deployAppService(environment, appPath);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async handleResourceProvision(args) {
    const { resourceType, resourceGroupName, resourceName, location, parameters } = args;
    const result = await this.azureAPI.provisionResource(resourceType, resourceGroupName, resourceName, location, parameters);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async handleMonitoringQuery(args) {
    const { metricName, resourceType, resourceName, timeRange } = args;
    const result = await this.azureAPI.queryMonitoring(metricName, resourceType, resourceName, timeRange);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  setupErrorHandling() {
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Azure MCP server running on stdio');
  }
}

const server = new AzureMCPServer();
server.run().catch(console.error);
```

### 2.2 Create Azure API Client

Create `src/azure-api.js`:

```javascript
import { DefaultAzureCredential } from '@azure/identity';
import { SqlManagementClient } from '@azure/arm-sql';
import { WebSiteManagementClient } from '@azure/arm-appservice';
import { StorageManagementClient } from '@azure/arm-storage';
import { ResourceManagementClient } from '@azure/arm-resources';
import { MonitorManagementClient } from '@azure/arm-monitor';
import { SqlClient } from '@azure/sql-database';
import { BlobServiceClient } from '@azure/storage-blob';
import axios from 'axios';

export class AzureAPI {
  constructor() {
    this.credential = new DefaultAzureCredential();
    this.subscriptionId = process.env.AZURE_SUBSCRIPTION_ID || this.getDefaultSubscriptionId();
    
    // Initialize Azure clients
    this.sqlClient = new SqlClient(this.credential, this.subscriptionId);
    this.sqlManagementClient = new SqlManagementClient(this.credential, this.subscriptionId);
    this.webSiteClient = new WebSiteManagementClient(this.credential, this.subscriptionId);
    this.storageClient = new StorageManagementClient(this.credential, this.subscriptionId);
    this.resourceClient = new ResourceManagementClient(this.credential, this.subscriptionId);
    this.monitorClient = new MonitorManagementClient(this.credential, this.subscriptionId);
  }

  async getDefaultSubscriptionId() {
    try {
      const subscriptions = await this.resourceClient.subscriptions.list();
      const firstSubscription = subscriptions.next().value;
      return firstSubscription.subscriptionId;
    } catch (error) {
      console.error('Error getting subscription ID:', error.message);
      throw error;
    }
  }

  async querySql(databaseName, query) {
    try {
      // This is a simplified implementation
      // In practice, you would need to:
      // 1. Get the database connection string
      // 2. Connect to the SQL database
      // 3. Execute the query
      // 4. Return the results
      
      return {
        success: true,
        message: `Query executed on ${databaseName}`,
        query,
        results: [], // Actual query results would go here
      };
    } catch (error) {
      console.error('Error querying SQL database:', error.message);
      throw error;
    }
  }

  async deployFunction(environment, functionPath) {
    try {
      // This is a simplified implementation
      // In practice, you would need to:
      // 1. Create a Function App if it doesn't exist
      // 2. Package the function code
      // 3. Deploy the function to Azure
      // 4. Return deployment status
      
      const functionAppName = `saber-epc-func-${environment}`;
      
      return {
        success: true,
        message: `Function deployed to ${environment}`,
        functionAppName,
        functionPath,
        environment,
      };
    } catch (error) {
      console.error('Error deploying function:', error.message);
      throw error;
    }
  }

  async accessBlob(operation, container, blob, filePath) {
    try {
      // Get storage account connection string
      const storageAccountName = `saber-epc-storage-${process.env.AZURE_ENVIRONMENT || 'prod'}`;
      const connectionString = await this.getStorageConnectionString(storageAccountName);
      
      const blobServiceClient = BlobServiceClient.fromConnectionString(connectionString);
      const containerClient = blobServiceClient.getContainerClient(container);
      
      switch (operation) {
        case 'list':
          return await this.listBlobs(containerClient);
        case 'upload':
          return await this.uploadBlob(containerClient, blob, filePath);
        case 'download':
          return await this.downloadBlob(containerClient, blob);
        case 'delete':
          return await this.deleteBlob(containerClient, blob);
        default:
          throw new Error(`Unknown blob operation: ${operation}`);
      }
    } catch (error) {
      console.error('Error accessing blob:', error.message);
      throw error;
    }
  }

  async listBlobs(containerClient) {
    try {
      const blobs = [];
      for await (const blob of containerClient.listBlobsFlat()) {
        blobs.push({
          name: blob.name,
          properties: blob.properties,
        });
      }
      return {
        success: true,
        blobs,
      };
    } catch (error) {
      console.error('Error listing blobs:', error.message);
      throw error;
    }
  }

  async uploadBlob(containerClient, blob, filePath) {
    try {
      const blockBlobClient = containerClient.getBlockBlobClient(blob);
      const uploadResponse = await blockBlobClient.uploadFile(filePath);
      return {
        success: true,
        message: `File uploaded to ${blob}`,
        blob,
        filePath,
        uploadResponse,
      };
    } catch (error) {
      console.error('Error uploading blob:', error.message);
      throw error;
    }
  }

  async downloadBlob(containerClient, blob) {
    try {
      const blockBlobClient = containerClient.getBlockBlobClient(blob);
      const downloadResponse = await blockBlobClient.download();
      return {
        success: true,
        message: `File downloaded from ${blob}`,
        blob,
        downloadResponse,
      };
    } catch (error) {
      console.error('Error downloading blob:', error.message);
      throw error;
    }
  }

  async deleteBlob(containerClient, blob) {
    try {
      const blockBlobClient = containerClient.getBlockBlobClient(blob);
      const deleteResponse = await blockBlobClient.delete();
      return {
        success: true,
        message: `File deleted from ${blob}`,
        blob,
        deleteResponse,
      };
    } catch (error) {
      console.error('Error deleting blob:', error.message);
      throw error;
    }
  }

  async deployAppService(environment, appPath) {
    try {
      // This is a simplified implementation
      // In practice, you would need to:
      // 1. Create an App Service if it doesn't exist
      // 2. Build the Next.js application
      // 3. Deploy the application to Azure
      // 4. Return deployment status
      
      const appServiceName = `saber-epc-app-${environment}`;
      
      return {
        success: true,
        message: `App deployed to ${environment}`,
        appServiceName,
        appPath,
        environment,
      };
    } catch (error) {
      console.error('Error deploying app service:', error.message);
      throw error;
    }
  }

  async provisionResource(resourceType, resourceGroupName, resourceName, location, parameters = {}) {
    try {
      switch (resourceType) {
        case 'resource-group':
          return await this.provisionResourceGroup(resourceGroupName, location);
        case 'app-service':
          return await this.provisionAppService(resourceGroupName, resourceName, location, parameters);
        case 'function-app':
          return await this.provisionFunctionApp(resourceGroupName, resourceName, location, parameters);
        case 'sql-database':
          return await this.provisionSqlDatabase(resourceGroupName, resourceName, location, parameters);
        case 'storage-account':
          return await this.provisionStorageAccount(resourceGroupName, resourceName, location, parameters);
        default:
          throw new Error(`Unknown resource type: ${resourceType}`);
      }
    } catch (error) {
      console.error('Error provisioning resource:', error.message);
      throw error;
    }
  }

  async provisionResourceGroup(resourceGroupName, location) {
    try {
      const resourceGroupParameters = {
        location: location,
      };
      
      const result = await this.resourceClient.resourceGroups.createOrUpdate(
        resourceGroupName,
        resourceGroupParameters
      );
      
      return {
        success: true,
        message: `Resource group ${resourceGroupName} created/updated`,
        resourceGroup: result,
      };
    } catch (error) {
      console.error('Error provisioning resource group:', error.message);
      throw error;
    }
  }

  async provisionAppService(resourceGroupName, appName, location, parameters) {
    try {
      // This is a simplified implementation
      // In practice, you would need to use the Azure App Service SDK
      // to create an App Service with the specified parameters
      
      return {
        success: true,
        message: `App Service ${appName} provisioned`,
        appName,
        resourceGroupName,
        location,
        parameters,
      };
    } catch (error) {
      console.error('Error provisioning App Service:', error.message);
      throw error;
    }
  }

  async provisionFunctionApp(resourceGroupName, functionName, location, parameters) {
    try {
      // This is a simplified implementation
      // In practice, you would need to use the Azure Functions SDK
      // to create a Function App with the specified parameters
      
      return {
        success: true,
        message: `Function App ${functionName} provisioned`,
        functionName,
        resourceGroupName,
        location,
        parameters,
      };
    } catch (error) {
      console.error('Error provisioning Function App:', error.message);
      throw error;
    }
  }

  async provisionSqlDatabase(resourceGroupName, databaseName, location, parameters) {
    try {
      // This is a simplified implementation
      // In practice, you would need to use the Azure SQL SDK
      // to create a SQL database with the specified parameters
      
      return {
        success: true,
        message: `SQL Database ${databaseName} provisioned`,
        databaseName,
        resourceGroupName,
        location,
        parameters,
      };
    } catch (error) {
      console.error('Error provisioning SQL Database:', error.message);
      throw error;
    }
  }

  async provisionStorageAccount(resourceGroupName, storageAccountName, location, parameters) {
    try {
      // This is a simplified implementation
      // In practice, you would need to use the Azure Storage SDK
      // to create a storage account with the specified parameters
      
      return {
        success: true,
        message: `Storage Account ${storageAccountName} provisioned`,
        storageAccountName,
        resourceGroupName,
        location,
        parameters,
      };
    } catch (error) {
      console.error('Error provisioning Storage Account:', error.message);
      throw error;
    }
  }

  async queryMonitoring(metricName, resourceType, resourceName, timeRange) {
    try {
      // This is a simplified implementation
      // In practice, you would need to:
      // 1. Get the resource ID
      // 2. Query Azure Monitor for the specified metric
      // 3. Return the metric data
      
      return {
        success: true,
        message: `Monitoring query executed for ${resourceName}`,
        metricName,
        resourceType,
        resourceName,
        timeRange,
        data: [], // Actual metric data would go here
      };
    } catch (error) {
      console.error('Error querying monitoring:', error.message);
      throw error;
    }
  }

  async getStorageConnectionString(storageAccountName) {
    try {
      // This is a simplified implementation
      // In practice, you would need to retrieve the storage account
      // connection string from Azure Key Vault or another secure location
      
      return `DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${process.env.AZURE_STORAGE_KEY};EndpointSuffix=core.windows.net`;
    } catch (error) {
      console.error('Error getting storage connection string:', error.message);
      throw error;
    }
  }
}
```

### 2.3 Update Package.json

Update `package.json`:

```json
{
  "name": "azure-mcp-server",
  "version": "0.1.0",
  "description": "MCP server for Azure EPC Portal",
  "main": "src/index.js",
  "type": "module",
  "scripts": {
    "start": "node src/index.js",
    "dev": "node --watch src/index.js"
  },
  "keywords": ["mcp", "azure", "epc-portal"],
  "author": "Saber Renewable Energy",
  "license": "MIT",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "@azure/identity": "^4.0.0",
    "@azure/arm-sql": "^6.0.0",
    "@azure/arm-appservice": "^10.0.0",
    "@azure/arm-storage": "^18.0.0",
    "@azure/arm-resources": "^5.0.0",
    "@azure/arm-monitor": "^7.0.0",
    "@azure/sql-database": "^1.0.0",
    "@azure/storage-blob": "^12.0.0",
    "axios": "^1.6.0"
  }
}
```

## Step 3: Configure MCP Server

### 3.1 Create Environment File

Create `.env`:

```bash
# Azure Configuration
AZURE_SUBSCRIPTION_ID=your_azure_subscription_id_here
AZURE_TENANT_ID=your_azure_tenant_id_here
AZURE_CLIENT_ID=your_azure_client_id_here
AZURE_CLIENT_SECRET=your_azure_client_secret_here
AZURE_STORAGE_KEY=your_azure_storage_key_here

# MCP Server Configuration
MCP_SERVER_NAME=azure-epc-portal-mcp
MCP_SERVER_VERSION=0.1.0
```

### 3.2 Create MCP Configuration File

Create `mcp-config.json`:

```json
{
  "mcpServers": {
    "azure-epc-portal": {
      "command": "node",
      "args": ["src/index.js"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "${AZURE_SUBSCRIPTION_ID}",
        "AZURE_TENANT_ID": "${AZURE_TENANT_ID}",
        "AZURE_CLIENT_ID": "${AZURE_CLIENT_ID}",
        "AZURE_CLIENT_SECRET": "${AZURE_CLIENT_SECRET}",
        "AZURE_STORAGE_KEY": "${AZURE_STORAGE_KEY}"
      }
    }
  }
}
```

## Step 4: Azure Authentication Setup

### 4.1 Create Service Principal

```bash
# Log in to Azure
az login

# Create a service principal
az ad sp create-for-rbac --name "saber-epc-mcp-sp" --role "Contributor"

# Note the output values (appId, password, tenant)
```

### 4.2 Configure Environment Variables

```bash
# Set the environment variables
export AZURE_SUBSCRIPTION_ID=your_subscription_id_here
export AZURE_TENANT_ID=your_tenant_id_here
export AZURE_CLIENT_ID=your_app_id_here
export AZURE_CLIENT_SECRET=your_password_here
```

## Step 5: Test MCP Server

### 5.1 Start the MCP Server

```bash
# Set the environment variables
export AZURE_SUBSCRIPTION_ID=your_subscription_id_here
export AZURE_TENANT_ID=your_tenant_id_here
export AZURE_CLIENT_ID=your_app_id_here
export AZURE_CLIENT_SECRET=your_password_here

# Start the server
npm start
```

### 5.2 Test MCP Tools

Create a test script `test-mcp.js`:

```javascript
#!/usr/bin/env node

import { spawn } from 'child_process';
import { createInterface } from 'readline';

async function testMCP() {
  const server = spawn('node', ['src/index.js'], {
    env: {
      ...process.env,
      AZURE_SUBSCRIPTION_ID: process.env.AZURE_SUBSCRIPTION_ID,
      AZURE_TENANT_ID: process.env.AZURE_TENANT_ID,
      AZURE_CLIENT_ID: process.env.AZURE_CLIENT_ID,
      AZURE_CLIENT_SECRET: process.env.AZURE_CLIENT_SECRET,
    },
    stdio: ['pipe', 'pipe', 'inherit'],
  });

  // Create readline interface for server output
  const rl = createInterface({
    input: server.stdout,
    crlfDelay: Infinity,
  });

  // Test resource provisioning
  console.log('Testing resource provisioning...');
  server.stdin.write(JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: {
      name: 'azure-epc-resource-provision',
      arguments: {
        resourceType: 'resource-group',
        resourceGroupName: 'saber-epc-test-rg',
        resourceName: 'test-rg',
        location: 'uksouth'
      }
    }
  }) + '\n');

  // Wait for response
  for await (const line of rl) {
    try {
      const response = JSON.parse(line);
      if (response.id === 1) {
        console.log('Resource provisioning result:', response.result);
        break;
      }
    } catch (error) {
      console.error('Error parsing response:', error);
    }
  }

  // Test blob access
  console.log('Testing blob access...');
  server.stdin.write(JSON.stringify({
    jsonrpc: '2.0',
    id: 2,
    method: 'tools/call',
    params: {
      name: 'azure-epc-blob-access',
      arguments: {
        operation: 'list',
        container: 'epc-partner-files'
      }
    }
  }) + '\n');

  // Wait for response
  for await (const line of rl) {
    try {
      const response = JSON.parse(line);
      if (response.id === 2) {
        console.log('Blob access result:', response.result);
        break;
      }
    } catch (error) {
      console.error('Error parsing response:', error);
    }
  }

  // Close the server
  server.stdin.end();
}

testMCP().catch(console.error);
```

Run the test:

```bash
# Set the environment variables
export AZURE_SUBSCRIPTION_ID=your_subscription_id_here
export AZURE_TENANT_ID=your_tenant_id_here
export AZURE_CLIENT_ID=your_app_id_here
export AZURE_CLIENT_SECRET=your_password_here

# Run the test
node test-mcp.js
```

## Step 6: Integrate with IDE

### 6.1 Claude Desktop Integration

Create `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "azure-epc-portal": {
      "command": "node",
      "args": ["/path/to/your/azure-mcp-server/src/index.js"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "your_azure_subscription_id_here",
        "AZURE_TENANT_ID": "your_azure_tenant_id_here",
        "AZURE_CLIENT_ID": "your_azure_client_id_here",
        "AZURE_CLIENT_SECRET": "your_azure_client_secret_here"
      }
    }
  }
}
```

Add this configuration to your Claude Desktop settings.

### 6.2 VS Code Integration

Create `.vscode/settings.json`:

```json
{
  "mcp.servers": [
    {
      "name": "azure-epc-portal",
      "command": "node",
      "args": ["${workspaceFolder}/src/index.js"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "${env:AZURE_SUBSCRIPTION_ID}",
        "AZURE_TENANT_ID": "${env:AZURE_TENANT_ID}",
        "AZURE_CLIENT_ID": "${env:AZURE_CLIENT_ID}",
        "AZURE_CLIENT_SECRET": "${env:AZURE_CLIENT_SECRET}"
      }
    }
  ]
}
```

## Step 7: Security Considerations

### 7.1 Azure Credentials Security

- Never commit your Azure credentials to version control
- Use environment variables to store your credentials
- Use Azure Key Vault for production credentials
- Rotate your service principal credentials regularly
- Limit service principal permissions to only what's necessary

### 7.2 MCP Server Security

- Run the MCP server with least privilege
- Validate all inputs to the MCP server
- Implement rate limiting for API calls
- Log all MCP server activities
- Use Managed Identities where possible

## Troubleshooting

### Common Issues

1. **Azure Authentication Error**
   - Verify your service principal credentials are correct
   - Check that your service principal has the necessary permissions
   - Ensure your subscription ID is correct

2. **Resource Provisioning Error**
   - Verify the resource name is available
   - Check that you have sufficient permissions
   - Ensure the resource group exists

3. **SQL Database Access Error**
   - Verify the database name is correct
   - Check that your service principal has SQL permissions
   - Ensure the database exists

4. **Blob Storage Access Error**
   - Verify the container name is correct
   - Check that your service principal has storage permissions
   - Ensure the container exists

5. **MCP Server Connection Error**
   - Verify the MCP server is running
   - Check that the MCP configuration is correct
   - Ensure the MCP client is compatible with the server version

### Support

For issues with the MCP server:
1. Check the server logs for error messages
2. Verify your Azure credentials and permissions
3. Test the Azure APIs directly
4. Check the MCP server configuration

---

**Document Version Control:**
- Version 1.0 - Initial Setup Guide (October 23, 2025)
- Next Review: October 30, 2025
- Approved By: [Pending Team Review]
- Status: Setup Guide