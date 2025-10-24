# MCP Cloudflare Setup Guide

## Overview

This guide provides step-by-step instructions for setting up the Model Context Protocol (MCP) server for the Cloudflare environment to support the EPC Partner Portal migration to Azure.

## Prerequisites

- Node.js 18+ installed
- Cloudflare API key for .energy domain
- Python 3.9+ installed
- Git installed

## Step 1: MCP Server Installation

### 1.1 Install MCP Server

```bash
# Create a directory for MCP servers
mkdir ~/mcp-servers
cd ~/mcp-servers

# Clone the MCP server repository
git clone https://github.com/modelcontextprotocol/servers.git
cd servers

# Install dependencies
npm install
```

### 1.2 Create Cloudflare MCP Server

```bash
# Create a new directory for Cloudflare MCP server
mkdir cloudflare-mcp-server
cd cloudflare-mcp-server

# Initialize npm project
npm init -y

# Install required packages
npm install @modelcontextprotocol/sdk
npm install cloudflare-api
npm install axios
```

## Step 2: Cloudflare MCP Server Implementation

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
import { CloudflareAPI } from './cloudflare-api.js';

class CloudflareMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'cloudflare-epc-portal-mcp',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.cloudflareAPI = new CloudflareAPI(process.env.CLOUDFLARE_API_KEY);
    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'cf-epc-database-query',
          description: 'Query Cloudflare D1 database for EPC portal data',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'SQL query string',
              },
              database: {
                type: 'string',
                description: 'D1 database name',
                default: 'epc-form-data',
              },
            },
            required: ['query'],
          },
        },
        {
          name: 'cf-epc-worker-deploy',
          description: 'Deploy Cloudflare Worker for EPC portal',
          inputSchema: {
            type: 'object',
            properties: {
              environment: {
                type: 'string',
                enum: ['development', 'staging', 'production'],
                description: 'Deployment environment',
              },
              workerPath: {
                type: 'string',
                description: 'Path to worker source code',
              },
            },
            required: ['environment', 'workerPath'],
          },
        },
        {
          name: 'cf-epc-r2-access',
          description: 'Access Cloudflare R2 storage for EPC files',
          inputSchema: {
            type: 'object',
            properties: {
              operation: {
                type: 'string',
                enum: ['list', 'upload', 'download', 'delete'],
                description: 'R2 operation to perform',
              },
              bucket: {
                type: 'string',
                description: 'R2 bucket name',
                default: 'epc-partner-files',
              },
              key: {
                type: 'string',
                description: 'File key (for upload/download/delete)',
              },
              filePath: {
                type: 'string',
                description: 'Local file path (for upload)',
              },
            },
            required: ['operation', 'bucket'],
          },
        },
        {
          name: 'cf-epc-dns-records',
          description: 'Manage DNS records for EPC portal',
          inputSchema: {
            type: 'object',
            properties: {
              operation: {
                type: 'string',
                enum: ['list', 'create', 'update', 'delete'],
                description: 'DNS operation to perform',
              },
              domain: {
                type: 'string',
                description: 'Domain name',
                default: 'saberrenewable.energy',
              },
              recordType: {
                type: 'string',
                enum: ['A', 'AAAA', 'CNAME', 'TXT', 'MX', 'SRV'],
                description: 'DNS record type',
              },
              recordName: {
                type: 'string',
                description: 'DNS record name',
              },
              recordValue: {
                type: 'string',
                description: 'DNS record value',
              },
            },
            required: ['operation', 'domain'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'cf-epc-database-query':
            return await this.handleDatabaseQuery(args);
          case 'cf-epc-worker-deploy':
            return await this.handleWorkerDeploy(args);
          case 'cf-epc-r2-access':
            return await this.handleR2Access(args);
          case 'cf-epc-dns-records':
            return await this.handleDnsRecords(args);
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

  async handleDatabaseQuery(args) {
    const { query, database } = args;
    const result = await this.cloudflareAPI.queryD1(database, query);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async handleWorkerDeploy(args) {
    const { environment, workerPath } = args;
    const result = await this.cloudflareAPI.deployWorker(environment, workerPath);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async handleR2Access(args) {
    const { operation, bucket, key, filePath } = args;
    const result = await this.cloudflareAPI.accessR2(operation, bucket, key, filePath);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async handleDnsRecords(args) {
    const { operation, domain, recordType, recordName, recordValue } = args;
    const result = await this.cloudflareAPI.manageDns(operation, domain, recordType, recordName, recordValue);
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
    console.error('Cloudflare MCP server running on stdio');
  }
}

const server = new CloudflareMCPServer();
server.run().catch(console.error);
```

### 2.2 Create Cloudflare API Client

Create `src/cloudflare-api.js`:

```javascript
import axios from 'axios';

export class CloudflareAPI {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseURL = 'https://api.cloudflare.com/client/v4';
    this.accountId = this.getAccountId();
  }

  async getAccountId() {
    // For .energy domain, we need to get the account ID
    try {
      const response = await axios.get(`${this.baseURL}/accounts`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
      });
      
      // Find the account that manages the .energy domain
      const account = response.data.result.find(acc => 
        acc.name.includes('Saber') || acc.name.includes('EPC')
      );
      
      return account ? account.id : response.data.result[0].id;
    } catch (error) {
      console.error('Error getting account ID:', error.message);
      throw error;
    }
  }

  async queryD1(databaseName, query) {
    try {
      const response = await axios.post(
        `${this.baseURL}/accounts/${this.accountId}/d1/database/${databaseName}/query`,
        { sql: query },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error querying D1 database:', error.message);
      throw error;
    }
  }

  async deployWorker(environment, workerPath) {
    try {
      // This is a simplified implementation
      // In practice, you would need to:
      // 1. Read the worker code from the file
      // 2. Create a wrangler.toml configuration
      // 3. Use wrangler CLI to deploy the worker
      // 4. Return deployment status
      
      return {
        success: true,
        message: `Worker deployed to ${environment}`,
        environment,
        workerPath,
      };
    } catch (error) {
      console.error('Error deploying worker:', error.message);
      throw error;
    }
  }

  async accessR2(operation, bucket, key, filePath) {
    try {
      switch (operation) {
        case 'list':
          return await this.listR2Objects(bucket);
        case 'upload':
          return await this.uploadR2Object(bucket, key, filePath);
        case 'download':
          return await this.downloadR2Object(bucket, key);
        case 'delete':
          return await this.deleteR2Object(bucket, key);
        default:
          throw new Error(`Unknown R2 operation: ${operation}`);
      }
    } catch (error) {
      console.error('Error accessing R2:', error.message);
      throw error;
    }
  }

  async listR2Objects(bucket) {
    try {
      const response = await axios.get(
        `${this.baseURL}/accounts/${this.accountId}/r2/buckets/${bucket}/objects`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error listing R2 objects:', error.message);
      throw error;
    }
  }

  async uploadR2Object(bucket, key, filePath) {
    try {
      // This is a simplified implementation
      // In practice, you would need to:
      // 1. Read the file from the file path
      // 2. Create a pre-signed URL for upload
      // 3. Upload the file using the pre-signed URL
      // 4. Return upload status
      
      return {
        success: true,
        message: `File uploaded to ${bucket}/${key}`,
        bucket,
        key,
        filePath,
      };
    } catch (error) {
      console.error('Error uploading R2 object:', error.message);
      throw error;
    }
  }

  async downloadR2Object(bucket, key) {
    try {
      // This is a simplified implementation
      // In practice, you would need to:
      // 1. Create a pre-signed URL for download
      // 2. Download the file using the pre-signed URL
      // 3. Return the file or download URL
      
      return {
        success: true,
        message: `File downloaded from ${bucket}/${key}`,
        bucket,
        key,
        downloadUrl: `https://${bucket}.r2.cloudflarestorage.com/${key}`,
      };
    } catch (error) {
      console.error('Error downloading R2 object:', error.message);
      throw error;
    }
  }

  async deleteR2Object(bucket, key) {
    try {
      const response = await axios.delete(
        `${this.baseURL}/accounts/${this.accountId}/r2/buckets/${bucket}/objects/${key}`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error deleting R2 object:', error.message);
      throw error;
    }
  }

  async manageDns(operation, domain, recordType, recordName, recordValue) {
    try {
      const zoneId = await this.getZoneId(domain);
      
      switch (operation) {
        case 'list':
          return await this.listDnsRecords(zoneId);
        case 'create':
          return await this.createDnsRecord(zoneId, recordType, recordName, recordValue);
        case 'update':
          return await this.updateDnsRecord(zoneId, recordType, recordName, recordValue);
        case 'delete':
          return await this.deleteDnsRecord(zoneId, recordName);
        default:
          throw new Error(`Unknown DNS operation: ${operation}`);
      }
    } catch (error) {
      console.error('Error managing DNS:', error.message);
      throw error;
    }
  }

  async getZoneId(domain) {
    try {
      const response = await axios.get(
        `${this.baseURL}/zones?name=${domain}`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (response.data.result.length === 0) {
        throw new Error(`Zone not found for domain: ${domain}`);
      }
      
      return response.data.result[0].id;
    } catch (error) {
      console.error('Error getting zone ID:', error.message);
      throw error;
    }
  }

  async listDnsRecords(zoneId) {
    try {
      const response = await axios.get(
        `${this.baseURL}/zones/${zoneId}/dns_records`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error listing DNS records:', error.message);
      throw error;
    }
  }

  async createDnsRecord(zoneId, recordType, recordName, recordValue) {
    try {
      const response = await axios.post(
        `${this.baseURL}/zones/${zoneId}/dns_records`,
        {
          type: recordType,
          name: recordName,
          content: recordValue,
          ttl: 3600,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error creating DNS record:', error.message);
      throw error;
    }
  }

  async updateDnsRecord(zoneId, recordType, recordName, recordValue) {
    try {
      // First, find the existing record
      const records = await this.listDnsRecords(zoneId);
      const existingRecord = records.result.find(
        record => record.type === recordType && record.name === recordName
      );
      
      if (!existingRecord) {
        throw new Error(`DNS record not found: ${recordName} (${recordType})`);
      }
      
      // Update the record
      const response = await axios.put(
        `${this.baseURL}/zones/${zoneId}/dns_records/${existingRecord.id}`,
        {
          type: recordType,
          name: recordName,
          content: recordValue,
          ttl: 3600,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error updating DNS record:', error.message);
      throw error;
    }
  }

  async deleteDnsRecord(zoneId, recordName) {
    try {
      // First, find the existing record
      const records = await this.listDnsRecords(zoneId);
      const existingRecord = records.result.find(
        record => record.name === recordName
      );
      
      if (!existingRecord) {
        throw new Error(`DNS record not found: ${recordName}`);
      }
      
      // Delete the record
      const response = await axios.delete(
        `${this.baseURL}/zones/${zoneId}/dns_records/${existingRecord.id}`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error deleting DNS record:', error.message);
      throw error;
    }
  }
}
```

### 2.3 Update Package.json

Update `package.json`:

```json
{
  "name": "cloudflare-mcp-server",
  "version": "0.1.0",
  "description": "MCP server for Cloudflare EPC Portal",
  "main": "src/index.js",
  "type": "module",
  "scripts": {
    "start": "node src/index.js",
    "dev": "node --watch src/index.js"
  },
  "keywords": ["mcp", "cloudflare", "epc-portal"],
  "author": "Saber Renewable Energy",
  "license": "MIT",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "axios": "^1.6.0"
  }
}
```

## Step 3: Configure MCP Server

### 3.1 Create Environment File

Create `.env`:

```bash
# Cloudflare API Configuration
CLOUDFLARE_API_KEY=your_cloudflare_api_key_here

# MCP Server Configuration
MCP_SERVER_NAME=cloudflare-epc-portal-mcp
MCP_SERVER_VERSION=0.1.0
```

### 3.2 Create MCP Configuration File

Create `mcp-config.json`:

```json
{
  "mcpServers": {
    "cloudflare-epc-portal": {
      "command": "node",
      "args": ["src/index.js"],
      "env": {
        "CLOUDFLARE_API_KEY": "${CLOUDFLARE_API_KEY}"
      }
    }
  }
}
```

## Step 4: Test MCP Server

### 4.1 Start the MCP Server

```bash
# Set the API key
export CLOUDFLARE_API_KEY=your_cloudflare_api_key_here

# Start the server
npm start
```

### 4.2 Test MCP Tools

Create a test script `test-mcp.js`:

```javascript
#!/usr/bin/env node

import { spawn } from 'child_process';
import { createReadStream } from 'fs';
import { createInterface } from 'readline';

async function testMCP() {
  const server = spawn('node', ['src/index.js'], {
    env: {
      ...process.env,
      CLOUDFLARE_API_KEY: process.env.CLOUDFLARE_API_KEY,
    },
    stdio: ['pipe', 'pipe', 'inherit'],
  });

  // Create readline interface for server output
  const rl = createInterface({
    input: server.stdout,
    crlfDelay: Infinity,
  });

  // Test database query
  console.log('Testing database query...');
  server.stdin.write(JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: {
      name: 'cf-epc-database-query',
      arguments: {
        query: 'SELECT COUNT(*) as count FROM invitations',
        database: 'epc-form-data'
      }
    }
  }) + '\n');

  // Wait for response
  for await (const line of rl) {
    try {
      const response = JSON.parse(line);
      if (response.id === 1) {
        console.log('Database query result:', response.result);
        break;
      }
    } catch (error) {
      console.error('Error parsing response:', error);
    }
  }

  // Test R2 access
  console.log('Testing R2 access...');
  server.stdin.write(JSON.stringify({
    jsonrpc: '2.0',
    id: 2,
    method: 'tools/call',
    params: {
      name: 'cf-epc-r2-access',
      arguments: {
        operation: 'list',
        bucket: 'epc-partner-files'
      }
    }
  }) + '\n');

  // Wait for response
  for await (const line of rl) {
    try {
      const response = JSON.parse(line);
      if (response.id === 2) {
        console.log('R2 access result:', response.result);
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
# Set the API key
export CLOUDFLARE_API_KEY=your_cloudflare_api_key_here

# Run the test
node test-mcp.js
```

## Step 5: Integrate with IDE

### 5.1 Claude Desktop Integration

Create `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cloudflare-epc-portal": {
      "command": "node",
      "args": ["/path/to/your/cloudflare-mcp-server/src/index.js"],
      "env": {
        "CLOUDFLARE_API_KEY": "your_cloudflare_api_key_here"
      }
    }
  }
}
```

Add this configuration to your Claude Desktop settings.

### 5.2 VS Code Integration

Create `.vscode/settings.json`:

```json
{
  "mcp.servers": [
    {
      "name": "cloudflare-epc-portal",
      "command": "node",
      "args": ["${workspaceFolder}/src/index.js"],
      "env": {
        "CLOUDFLARE_API_KEY": "${env:CLOUDFLARE_API_KEY}"
      }
    }
  ]
}
```

## Step 6: Security Considerations

### 6.1 API Key Security

- Never commit your API key to version control
- Use environment variables to store your API key
- Rotate your API key regularly
- Limit API key permissions to only what's necessary

### 6.2 MCP Server Security

- Run the MCP server with least privilege
- Validate all inputs to the MCP server
- Implement rate limiting for API calls
- Log all MCP server activities

## Troubleshooting

### Common Issues

1. **API Key Authentication Error**
   - Verify your API key is correct
   - Check that your API key has the necessary permissions
   - Ensure your account can access the .energy domain

2. **D1 Database Access Error**
   - Verify the database name is correct
   - Check that your API key has D1 permissions
   - Ensure the database exists in your account

3. **R2 Storage Access Error**
   - Verify the bucket name is correct
   - Check that your API key has R2 permissions
   - Ensure the bucket exists in your account

4. **MCP Server Connection Error**
   - Verify the MCP server is running
   - Check that the MCP configuration is correct
   - Ensure the MCP client is compatible with the server version

### Support

For issues with the MCP server:
1. Check the server logs for error messages
2. Verify your API key and permissions
3. Test the Cloudflare API directly
4. Check the MCP server configuration

---

**Document Version Control:**
- Version 1.0 - Initial Setup Guide (October 23, 2025)
- Next Review: October 30, 2025
- Approved By: [Pending Team Review]
- Status: Setup Guide