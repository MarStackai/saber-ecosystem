# EPC Portal Development Setup Guide
**Last Updated**: 2025-09-23

## 🚀 Port Configuration

### Important: Port 4200
The frontend development server runs on **port 4200** to avoid conflicts with commonly used ports 3000-3003.

### Service Port Allocation
| Service | Port | Description |
|---------|------|-------------|
| **Frontend (Next.js)** | 4200 | React application |
| **Backend (Wrangler)** | 8787 | Cloudflare Worker |
| **Staging Worker** | 8788 | Staging environment |
| **MCP Manager** | 3000 | System service |
| **n8n** | 5678 | Workflow automation |
| **Portainer** | 9000/9443 | Docker management |
| **Ollama** | 11434 | AI model service |

## 📋 Prerequisites

### Required Software
- Node.js 18+
- npm or yarn
- Cloudflare Wrangler CLI
- Git
- VS Code (recommended)

### Cloudflare Account Setup
1. Create a Cloudflare account
2. Set up API token with permissions:
   - Account: Cloudflare Pages:Edit
   - Account: Cloudflare Workers Scripts:Edit
   - Zone: DNS:Edit
   - Account: Workers R2 Storage:Edit
   - Account: D1:Edit

## 🛠️ Initial Setup

### 1. Clone Repository
```bash
git clone https://github.com/MarStackai/saber-epc-portal.git
cd saber-epc-portal
```

### 2. Install Dependencies
```bash
# Install root dependencies
npm install

# Install React app dependencies
cd epc-portal-react
npm install
cd ..
```

### 3. Environment Configuration
Create `.env.local` in the React app directory:
```bash
cd epc-portal-react
cp .env.example .env.local
```

Edit `.env.local` with your values:
```env
NEXT_PUBLIC_API_URL=http://localhost:8787
NEXT_PUBLIC_WORKER_URL=http://localhost:8787
```

### 4. Database Setup
```bash
# Create local D1 database
npx wrangler d1 create epc-form-data

# Run migrations
npx wrangler d1 execute epc-form-data --local --file=./schema.sql
```

### 5. Configure Wrangler
Update `wrangler.toml` with your account ID:
```toml
account_id = "YOUR_ACCOUNT_ID"
```

## 🚦 Starting Development Servers

### Quick Start (All Services)
```bash
# Terminal 1: Frontend (port 4200)
cd epc-portal-react && npm run dev

# Terminal 2: Backend Worker (port 8787)
npx wrangler dev --local --port 8787

# Terminal 3: Staging Worker (optional, port 8788)
npx wrangler dev --env staging --port 8788
```

### Individual Services

#### Frontend Development Server
```bash
cd epc-portal-react
npm run dev
# Runs on http://localhost:4200
```

#### Backend Worker
```bash
npx wrangler dev --local --port 8787
# API available at http://localhost:8787
```

#### Staging Environment
```bash
npx wrangler dev --env staging --port 8788
# Staging at http://localhost:8788
```

## 🧪 Testing

### Run Tests
```bash
# Quick smoke tests
npm run test:quick

# Full test suite
npm test

# Staging tests
TEST_ENV=staging npm test

# Interactive UI
npm run test:ui
```

### Test URLs
- Development: http://localhost:4200
- Form with test code: http://localhost:4200/form?invitationCode=TEST001
- Admin portal: http://localhost:4200/admin
- Partner login: http://localhost:4200/partner/login

### Test Invitation Codes
- `TEST001`
- `TEST2024`
- `DEMO2024`

## 📦 Deployment

### Deploy to Staging
```bash
npm run deploy:staging
# Or manually:
./scripts/deploy-staging.sh
```

### Deploy to Production
```bash
npm run deploy:production
# Or manually:
./scripts/deploy-production.sh
```

## 🔧 VS Code Configuration

The project includes VS Code settings for optimal development:

### Debug Configuration
Press `F5` to start debugging with the Next.js app on port 4200.

### Recommended Extensions
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Prisma (for D1 schema)
- PowerShell (for deployment scripts)

### Workspace Settings
Located in `.vscode/settings.json`:
- Auto-format on save
- Port 4200 for terminal
- Proper TypeScript configuration
- Tailwind CSS support

## 🏗️ Project Structure

```
saber-epc-portal/
├── epc-portal-react/       # Next.js frontend (port 4200)
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities and helpers
│   │   └── styles/        # CSS and Tailwind
│   └── package.json       # Configured for port 4200
├── src/                    # Cloudflare Worker
│   ├── index.js           # Main worker file
│   └── lib/               # Worker utilities
├── scripts/               # Deployment scripts
├── tests/                 # Playwright tests
├── wrangler.toml         # Worker configuration
└── schema.sql            # D1 database schema
```

## 🐛 Troubleshooting

### Port Conflicts
If port 4200 is already in use:
1. Check what's using it: `lsof -i :4200`
2. Kill the process or choose a different port in `package.json`

### Cache Issues
```bash
# Clear Next.js cache
cd epc-portal-react
rm -rf .next node_modules/.cache

# Reinstall and restart
npm install
npm run dev
```

### Worker Connection Issues
1. Ensure Worker is running on port 8787
2. Check `.env.local` has correct URLs
3. Verify CORS settings in Worker

### Database Issues
```bash
# Reset local database
rm -rf .wrangler/state/v3/d1/

# Recreate and migrate
npx wrangler d1 execute epc-form-data --local --file=./schema.sql
```

## 📚 Additional Resources

### Documentation
- [CLAUDE.md](../CLAUDE.md) - Development rules and guidelines
- [README.md](../README.md) - Project overview
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Deployment guide
- [agents.md](../agents.md) - AI agent roles

### External Links
- [Next.js Documentation](https://nextjs.org/docs)
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [Cloudflare D1](https://developers.cloudflare.com/d1/)
- [Playwright Testing](https://playwright.dev/)

## 💡 Tips

1. **Always use port 4200** for frontend development
2. **Check CLAUDE.md** before making changes
3. **Test on staging** before production deployment
4. **Use the TodoWrite tool** for task tracking
5. **Document significant changes** in appropriate files

## 🆘 Getting Help

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review error logs in the console
3. Check GitHub issues for similar problems
4. Consult CLAUDE.md for development rules
5. Use the development status file for context