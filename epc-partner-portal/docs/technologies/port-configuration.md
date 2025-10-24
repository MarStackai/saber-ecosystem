# Port Configuration Strategy
**Updated**: 2025-09-23

## Overview
This document outlines the port configuration strategy for the EPC Portal development environment, explaining the rationale behind port 4200 and the overall port allocation strategy.

## The Port 3000 Problem

### Common Conflicts
Ports 3000-3003 are heavily used by popular development tools:
- **Port 3000**: Default for Create React App, Express.js, many Node.js frameworks
- **Port 3001**: Common fallback when 3000 is occupied
- **Port 3002**: Second fallback, browser-sync default
- **Port 3003**: Third fallback, various development tools

### Issues Experienced
1. Unpredictable port assignment (3000, 3001, 3002, 3003)
2. Conflicts with MCP Manager (system service on 3000)
3. Documentation inconsistencies
4. Testing configuration mismatches
5. Developer confusion with multiple projects

## The Port 4200 Solution

### Why 4200?
- **Less Common**: Not a default for major frameworks
- **Angular Heritage**: Familiar to developers (Angular CLI default)
- **Easy to Remember**: Round number, distinctive
- **Safe Range**: 4000-4999 less congested than 3000-3999
- **No System Conflicts**: Avoids common system service ports

### Implementation
```json
// package.json
{
  "scripts": {
    "dev": "next dev -p 4200",
    "start": "next start -p 4200"
  }
}
```

## Complete Port Map

### Development Environment
```yaml
Frontend Services:
  Next.js React App: 4200
  Storybook (if added): 6006

Backend Services:
  Cloudflare Worker (local): 8787
  Cloudflare Worker (staging): 8788

System Services:
  MCP Manager: 3000
  n8n Workflow: 5678
  Portainer: 9000 (HTTP), 9443 (HTTPS)
  Ollama AI: 11434

Database/Storage:
  D1 Database: Via Wrangler (8787)
  R2 Storage: Via Wrangler (8787)
```

### Port Ranges by Purpose
- **3000-3999**: System services and tools
- **4000-4999**: Application frontends
- **5000-5999**: Workflow and automation tools
- **6000-6999**: Documentation and testing tools
- **7000-7999**: Reserved for future microservices
- **8000-8999**: Backend services and APIs
- **9000-9999**: Admin and management interfaces
- **10000+**: Database and infrastructure services

## Configuration Files

### Files Updated for Port 4200
1. `package.json` - Dev and start scripts
2. `.env.development` - Frontend URL
3. `playwright.config.ts` - Test base URL
4. `.vscode/settings.json` - Debug configuration
5. `CLAUDE.md` - Documentation
6. `README.md` - Quick start guide
7. `agents.md` - Development instructions

### Environment Variables
```bash
# Development
FRONTEND_URL=http://localhost:4200
NEXT_PUBLIC_API_URL=http://localhost:8787

# Staging
FRONTEND_URL=https://staging-epc.saberrenewable.energy
NEXT_PUBLIC_API_URL=https://staging-epc.saberrenewable.energy

# Production
FRONTEND_URL=https://epc.saberrenewable.energy
NEXT_PUBLIC_API_URL=https://epc.saberrenewable.energy
```

## VS Code Integration

### Debug Launch Configuration
```json
{
  "name": "Next.js: debug",
  "type": "node",
  "request": "launch",
  "runtimeArgs": ["-p", "4200"],
  "cwd": "${workspaceFolder}/epc-portal-react"
}
```

### Terminal Environment
```json
{
  "terminal.integrated.env.linux": {
    "PORT": "4200"
  }
}
```

## Testing Configuration

### Playwright Setup
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: process.env.TEST_ENV === 'staging'
      ? 'https://staging-epc.saberrenewable.energy'
      : 'http://localhost:4200'
  },
  webServer: {
    command: 'cd epc-portal-react && npm run dev',
    port: 4200,
    reuseExistingServer: !process.env.CI
  }
});
```

## Migration Guide

### For Existing Developers
If you have the old setup (ports 3000-3003):

1. **Stop all services**
   ```bash
   # Kill any running Node processes
   pkill -f "node.*dev"
   ```

2. **Update your repository**
   ```bash
   git pull origin main
   ```

3. **Clean and reinstall**
   ```bash
   cd epc-portal-react
   rm -rf .next node_modules/.cache
   npm install
   ```

4. **Start with new port**
   ```bash
   npm run dev  # Now runs on port 4200
   ```

### For New Developers
Simply follow the setup guide - everything is pre-configured for port 4200.

## Benefits Achieved

### Consistency
- Same port across all environments
- Predictable behavior
- Clear documentation

### Efficiency
- No port hunting
- Faster development startup
- Reduced debugging time

### Scalability
- Room for additional services
- Clear port allocation strategy
- Avoids future conflicts

## Future Considerations

### If Port 4200 Becomes Unavailable
Fallback ports in order of preference:
1. 4201
2. 4300
3. 5200
4. 7200

### Adding New Services
Follow the port range guidelines:
- Frontend apps: 4xxx
- Backend services: 8xxx
- Admin tools: 9xxx

## Troubleshooting

### Check Port Usage
```bash
# Linux/Mac
lsof -i :4200

# Windows
netstat -ano | findstr :4200
```

### Force Kill Process on Port
```bash
# Linux/Mac
kill -9 $(lsof -t -i:4200)

# Windows (as admin)
for /f "tokens=5" %a in ('netstat -ano ^| findstr :4200') do taskkill /PID %a /F
```

### Verify Configuration
```bash
# Check package.json
cat epc-portal-react/package.json | grep "dev"

# Should show:
# "dev": "next dev -p 4200"
```

## Conclusion
The migration to port 4200 provides a stable, conflict-free development environment. This configuration is now standard for the EPC Portal project and should be maintained across all development machines and environments.