# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ecosystem Overview

The Saber Renewable Energy Ecosystem is a multi-project monorepo containing four integrated systems for renewable energy operations. Each project has its own detailed CLAUDE.md file - refer to those for project-specific details.

**Projects:**
- **saber-calculator**: Solar PPA financial modeling (Python/Streamlit)
- **epc-partner-portal**: EPC partner onboarding platform (Next.js/Cloudflare)
- **fit-intelligence**: AI-powered FIT installation analysis (Python/ChromaDB/LLM)
- **saber-business-ops-platform**: Comprehensive ops platform (Azure/.NET/React) - in planning

## Quick Start Commands

### Saber Calculator
```bash
cd saber-calculator
./start_saber_with_tunnels.sh
# MVP Calculator: http://localhost:8501 (or https://ppa.saberrenewable.energy)
# Advanced Calculator: http://localhost:8502 (or https://ppa-advanced.saberrenewable.energy)
```

### EPC Partner Portal
```bash
cd epc-partner-portal/epc-portal-react

# Frontend (port 4200 - IMPORTANT: not 3000)
npm run dev

# Backend Worker (from parent directory)
cd .. && npx wrangler dev --local --port 8787

# Testing
npx playwright test                    # All E2E tests
TEST_ENV=staging npx playwright test   # Staging tests
npm run test:admin                     # Admin portal tests
npm run test:partner                   # Partner portal tests

# Deployment
npm run build                          # Build static export
npx wrangler deploy --env staging      # Deploy to staging
npx wrangler deploy --env production   # Deploy to production
```

### FIT Intelligence
```bash
cd fit-intelligence

# Start API server (uses venv automatically)
./venv/bin/python fit_api_server.py
# Access: http://localhost:5000

# Testing
python test_system.py                  # System accuracy tests
python verify_complete_coverage.py     # ChromaDB coverage check
```

### Business Operations Platform
```bash
cd saber-business-ops-platform
# Currently in planning phase - see docs/ for architecture
```

## Cross-Project Architecture

### Integration Patterns

**Data Flow:**
1. **Calculator → Business Ops**: PPA results feed into project tracking
2. **EPC Portal → Business Ops**: Partner data synchronization
3. **FIT Intelligence → All Systems**: Installation analytics and insights
4. **SharePoint**: Centralized document management for EPC Portal and Business Ops

**Shared Technologies:**
- **Frontend**: React (various frameworks: Next.js, Streamlit)
- **Styling**: Tailwind CSS across all web UIs
- **Cloud**: Azure (Business Ops), Cloudflare (EPC Portal)
- **Data**: SharePoint (document management), SQL/D1 (structured data), ChromaDB (vector search)

### Authentication & Access Control

**EPC Portal:**
- Public portal: Invitation-code based (no auth required)
- Partner portal: Authenticated partner access
- Admin portal: Internal staff only

**FIT Intelligence:**
- API server with Flask (port 5000)
- Proprietary FIT data access controls

**Future (Business Ops):**
- Azure AD B2C for unified SSO
- Role-based access control across all platforms

## Critical Architecture Notes

### EPC Partner Portal Architecture

**Hybrid Static/Edge Pattern:**
- Next.js static export deployed to Cloudflare Pages
- API routes (`/functions/api/*`) run as Cloudflare Workers
- D1 database (SQLite) for data persistence
- R2 buckets for file storage
- SharePoint for communications and business processes

**Key Pattern - D1-First with SharePoint Sync:**
1. All submissions go to D1 immediately (fast, reliable)
2. SharePoint sync happens asynchronously (can retry on failure)
3. Never block user flow waiting for SharePoint

**Port Configuration (CRITICAL):**
- Frontend: Port 4200 (to avoid Node.js tool conflicts)
- Backend Worker: Port 8787
- Never use ports 3000-3003

### FIT Intelligence Architecture

**Vector Search + LLM System:**
- 75,194+ UK renewable energy installations in ChromaDB
- Llama 2 13B (GPU-accelerated, ~11GB VRAM)
- NVIDIA RTX 3090 (24GB VRAM) required for optimal performance
- Warm index for fast geographic filtering (ChromaDB has location limitations)

**Key Components:**
- `fit_api_server.py`: Main production API
- `enhanced_query_parser.py`: Deterministic NLP parsing
- `market_analyst.py`: Comparative/aggregate analysis
- `uk_postcodes.py`: Comprehensive UK geographic mappings

**Critical Patterns:**
- Temperature MUST stay at 0.1 or lower for accuracy
- Always include FIT IDs in responses
- Never allow hallucination - only verified database entries

### Saber Calculator Architecture

**Dual Calculator System:**
- `app.py`: MVP calculator (port 8501)
- `calc-proto-cl.py`: Advanced calculator (port 8502)
- Both use Streamlit with Cloudflare Tunnels for public access
- Live production URLs: ppa.saberrenewable.energy, ppa-advanced.saberrenewable.energy

### Business Operations Platform Architecture

**Status**: Comprehensive planning complete - 17 detailed specification documents ready for implementation

**Enterprise Architecture:**
- **Frontend**: React 18 with TypeScript, Next.js 15, Tailwind CSS 4.1+, Zustand state management
- **Backend**: .NET 8 with ASP.NET Core, Entity Framework Core, RESTful APIs with OpenAPI 3.0
- **Cloud Platform**: Microsoft Azure (UK South primary, UK West secondary)
- **Database**: Azure SQL (8 vCores, 1TB), Azure Cosmos DB, Redis Cache
- **Authentication**: Azure AD B2C with JWT tokens, MFA, RBAC
- **Infrastructure**: Azure App Service, AKS (Kubernetes), Virtual Networks with hub-and-spoke topology

**Four Core Modules:**

1. **Calculator Module**:
   - Multi-technology support (Solar PV, CHP, Wind, Battery)
   - Financial modeling (PPA pricing, IRR, NPV, LCOE, 25-year cash flow)
   - AI-enhanced optimization and recommendations
   - Professional PDF/Excel report generation
   - <10 second calculation time target

2. **FIT Intelligence Module**:
   - 5M+ UK FIT installations tracked
   - Natural language search with advanced filtering
   - PPA opportunity identification
   - Repowering feasibility assessment
   - Market intelligence and trend analysis
   - <2 second search latency target

3. **Partner Management Module**:
   - Comprehensive EPC partner lifecycle management
   - Automated onboarding workflows
   - Performance tracking and KPI monitoring
   - Resource capacity planning
   - Capability assessment and certification tracking
   - 1000+ partners supported

4. **Project Management Module**:
   - End-to-end project lifecycle management
   - Resource allocation and scheduling
   - Budget tracking and financial management
   - Risk management and issue tracking
   - Client portal and communication tools
   - 1000+ active projects supported

**AI/ML Architecture - Specialist Model Routing:**

The platform uses a sophisticated multi-model AI architecture with four specialized LLMs:

1. **Llama3.2-3B (Classifier)** - Request routing and classification
   - Routes requests to appropriate specialist models
   - Classifies calculation types and FIT installations
   - Determines analysis priorities
   - Gateway for all AI requests

2. **Qwen2.5-14B-Instruct (Reasoner)** - Technical analysis and complex reasoning
   - Analyzes renewable energy project requirements
   - Evaluates technical feasibility
   - Generates technical recommendations
   - Complex financial modeling logic

3. **Qwen-Math-7B (Financial Calculator)** - Precise financial calculations
   - PPA price calculations
   - IRR, NPV, LCOE computations
   - Cash flow modeling and sensitivity analysis

4. **Llama3.1-8B-Instruct (Communicator)** - Natural language generation
   - Generates user-friendly explanations
   - Creates narrative reports
   - Produces client-facing communications
   - Generates documentation

**AI Request Flow:**
```
Business Service → AI Router → Llama3.2 Classifier
  → Routes to specialist (Qwen2.5/Qwen-Math/Llama3.1)
  → RAG Service enhances with knowledge base
  → Results aggregated and returned
```

**RAG (Retrieval Augmented Generation):**
- Vector database for embedding storage
- Knowledge base: Technical docs, FIT database (5M+ records), financial parameters
- Semantic search with cosine similarity
- Dynamic context window based on task complexity

**Integration Strategy:**

1. **With saber-calculator**:
   - API-based integration with backward compatibility
   - Legacy calculator remains operational during transition
   - New platform calls legacy for baseline calculations
   - AI enhancements applied on top of legacy results
   - Gradual migration path for partner acceptance

2. **With epc-partner-portal**:
   - Single sign-on via Azure AD B2C
   - Partner management data synchronized bidirectionally
   - Shared document repository
   - Unified notifications and communications

3. **With fit-intelligence**:
   - FIT database consumed by Business Ops FIT module
   - AI analysis enhances existing FIT intelligence
   - Opportunity recommendations and scoring
   - Real-time sync of FIT data

**Azure Deployment Architecture:**

- **Network**: Hub-and-spoke VNet topology, ExpressRoute for hybrid connectivity, Azure Firewall
- **Compute**: Premium P3v2 App Service (4 vCPU, 16GB RAM, auto-scale 1-10 instances), AKS for containers
- **Database**: Zone-redundant SQL with geo-replication, read replicas, 35-day backup retention
- **Storage**: Blob Storage with lifecycle management (Hot→Cool→Archive), Azure Files for shares
- **Security**: Key Vault for secrets, WAF, DDoS Protection Standard, comprehensive monitoring
- **AI Services**: Azure OpenAI (GPT-4, GPT-3.5-Turbo), Machine Learning workspace, multiple model deployments

**Implementation Timeline:**
- **Phase 1 (Weeks 1-8)**: Foundation - Infrastructure, core architecture, basic modules
- **Phase 2 (Weeks 9-16)**: Core Development - Advanced modules, AI/ML integration
- **Phase 3 (Weeks 17-24)**: Enhancement - Performance optimization, security hardening, UAT
- **Phase 4 (Weeks 25-32)**: Deployment - Production deployment, training, go-live support

**Total Duration**: 32 weeks (8 months)
**Team Size**: 26 people (PM, dev, QA, DevOps, design, support)
**Budget**: £500,000

**Key Architectural Patterns:**
- Microservices with independent deployability
- API-first design with OpenAPI 3.0 documentation
- Cloud-native PaaS-first approach
- Security-first with Zero Trust architecture
- Polyglot persistence (SQL + NoSQL)
- Event-driven communication via Azure Service Bus

**Documentation:**
- 17 comprehensive specification documents in `/docs` folder
- Complete API specifications with all endpoints defined
- Detailed database schema with 50+ tables
- Azure infrastructure fully specified
- Testing framework and quality gates defined

## Development Standards

### Port Assignments
- **8501**: Saber Calculator MVP
- **8502**: Saber Calculator Advanced
- **4200**: EPC Portal Frontend (NEVER 3000)
- **8787**: EPC Portal Worker (local dev)
- **8788**: EPC Portal Staging Worker
- **5000**: FIT Intelligence API

### Testing Approach

**EPC Portal:**
- Playwright for modern E2E testing (preferred)
- Puppeteer for legacy tests (consider migrating)
- Multi-environment testing: local, staging, production

**FIT Intelligence:**
- Automated accuracy tests with `test_system.py`
- Geographic accuracy: 98% target
- FIT ID coverage: 100% required

### Environment Management

**EPC Portal:**
- `.env.development`, `.env.staging`, `.env.production`
- `wrangler.toml` with three environment configs
- Secrets managed via Cloudflare dashboard (never commit)

**FIT Intelligence:**
- Python virtual environment: `./venv`
- Ollama for local LLM deployment
- ChromaDB persistent storage in `./chroma_db/`

## Project-Specific Documentation

**For detailed information, see each project's CLAUDE.md:**
- [epc-partner-portal/CLAUDE.md](epc-partner-portal/CLAUDE.md) - Comprehensive portal architecture
- [epc-partner-portal/epc-portal-react/CLAUDE.md](epc-partner-portal/epc-portal-react/CLAUDE.md) - Frontend specifics
- [fit-intelligence/CLAUDE.md](fit-intelligence/CLAUDE.md) - FIT Intelligence platform details

**Architecture documentation:**
- [docs/Saber_Business_Ops_System_Architecture.md](docs/Saber_Business_Ops_System_Architecture.md)
- [docs/Saber_Business_Ops_Azure_Deployment_Architecture.md](docs/Saber_Business_Ops_Azure_Deployment_Architecture.md)
- [docs/Saber_Business_Ops_API_Specifications.md](docs/Saber_Business_Ops_API_Specifications.md)

## Common Troubleshooting

### Port Conflicts
```bash
# EPC Portal port 4200 already in use
lsof -ti:4200 | xargs kill -9

# Kill all Streamlit processes (Calculator)
pkill -f streamlit
```

### Cloudflare Workers Issues (EPC Portal)
```bash
# D1/R2 bindings not available in development
# Expected behavior - mock helpers activate automatically
# Test with actual bindings:
npx wrangler dev --local --port 8787
```

### GPU/VRAM Issues (FIT Intelligence)
```bash
# Check Ollama GPU usage
ollama ps

# Verify GPU is detected
nvidia-smi
```

### SharePoint Authentication (EPC Portal)
- Verify Azure AD app registration exists
- Client ID: bbbfe394-7cff-4ac9-9e01-33cbf116b930
- Use device login for interactive testing
- Certificate auth for automated scripts

## Key Reminders

1. **EPC Portal uses D1, NOT Redis** - migration completed
2. **EPC Portal frontend runs on port 4200** - never use 3000
3. **FIT Intelligence requires GPU** - NVIDIA RTX 3090 or equivalent
4. **SharePoint is for communications** - not primary data storage for EPC Portal
5. **Each project has its own CLAUDE.md** - refer to those for detailed guidance
6. **Business Ops Platform is in planning phase** - 17 comprehensive specification documents ready, 32-week implementation timeline defined
7. **Business Ops uses 4 specialist AI models** - Llama3.2 (classifier), Qwen2.5 (reasoner), Qwen-Math (calculator), Llama3.1 (communicator)
8. **Never commit secrets** - use environment variables and cloud secret management
9. **Integration strategy defined** - Business Ops will integrate all 3 existing systems with backward compatibility
