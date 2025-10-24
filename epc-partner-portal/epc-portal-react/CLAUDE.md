# EPC Partner Portal - Architecture & Context

## 🚀 **PORT CONFIGURATION** (Updated 2025-09-23)
**IMPORTANT**: Frontend runs on **PORT 4200** to avoid conflicts

### Development Ports:
- **Frontend (Next.js)**: Port 4200
- **Backend (Wrangler)**: Port 8787
- **Staging Worker**: Port 8788

### Quick Start:
```bash
# Start Frontend (port 4200)
npm run dev

# Backend (from parent directory)
cd .. && npx wrangler dev --local --port 8787
```

## 🏗️ **CURRENT ARCHITECTURE** (Updated 2025-09-11)

### **Core Technology Stack:**
- **Frontend:** Next.js 15.4.4 with App Router and Edge Runtime
- **Backend:** Cloudflare Workers (for API processing)
- **Database:** Cloudflare D1 (SQLite-based, replaced Redis)
- **File Storage:** Cloudflare R2 (for document uploads)
- **Communications:** Microsoft SharePoint integration

### **⚠️ IMPORTANT: NO REDIS**
- **We migrated FROM Redis TO D1 database**
- D1 provides better Cloudflare integration
- All form data persistence uses D1Helper class
- Redis dependencies removed from codebase

## 📊 **Database Schema (D1)**

### Tables:
1. **applications** - 97 columns for complete form data
2. **draft_data** - Auto-save functionality 
3. **application_files** - File upload tracking
4. **audit_log** - Change tracking

### Key Files:
- `/src/lib/d1.js` - D1Helper class with all database operations
- `/schema.sql` - Complete database schema
- `/wrangler.toml` - D1 and R2 bindings

## 🔗 **SharePoint Integration**

### **Purpose:**
- **Invitation Management:** Track and validate invitation codes
- **Internal Communications:** Stakeholder notifications and updates
- **External Communications:** Partner onboarding and correspondence
- **Document Management:** Final application storage and processing

### **Configuration:**
- Site: `https://saberrenewables.sharepoint.com/sites/SaberEPCPartners`
- Client ID: `bbbfe394-7cff-4ac9-9e01-33cbf116b930`
- Auth Method: Certificate-based (working)
- Lists: "EPC Invitations", "EPC Onboarding"

## 🚀 **Development Setup**

### **Required Commands:**
```bash
# Start React frontend (port 4200)
cd epc-portal-react && npm run dev

# Start Cloudflare Worker backend (port 8787)
cd .. && npx wrangler dev --port 8787 --local

# Create D1 database tables
npx wrangler d1 execute epc-form-data --local --file=../schema.sql
```

### **Environment Files:**
- `.env.local` - Development environment variables
- `wrangler.toml` - Cloudflare bindings and configuration

## 📁 **Key API Routes**

All API routes use **Edge Runtime** and **D1 database**:
- `/api/save-draft` - Auto-save form data to D1
- `/api/epc-application` - Submit complete application 
- `/api/upload-file` - Handle file uploads to R2
- `/api/clear-draft` - Clear saved draft data

## 🎯 **Form Features**

### **Current Fields (Added):**
- Company Website (URL input)
- Company Logo (File upload)
- All original EPC application fields

### **Functionality:**
- ✅ Auto-save to D1 database
- ✅ File upload to R2 storage  
- ✅ SharePoint integration for final submission
- ✅ Multi-step form with progress tracking
- ✅ Invitation code validation

## 🔧 **Development Notes**

### **Cache Management:**
- Clear Next.js cache: `rm -rf .next` if making major changes
- D1 local database: `.wrangler/state/v3/d1/`
- Hot reload works for most changes

### **Testing:**
- Test invitation codes: `TEST001`, `TEST2024`, `DEMO2024`
- Local URLs: `http://localhost:4200/form?invitationCode=TEST001`
- SharePoint access requires device login for testing

### **Deployment:**
- Frontend: Cloudflare Pages
- Backend: Cloudflare Workers 
- Database: Cloudflare D1 (remote)
- Storage: Cloudflare R2 (remote)

---

## 🚨 **CRITICAL REMINDERS:**

1. **NO REDIS** - Everything uses D1 database now
2. **SharePoint is for COMMUNICATIONS** - invitations, stakeholder updates, partner correspondence
3. **All storage is Cloudflare native** - D1 + R2 + Workers
4. **Certificate auth works** - SharePoint integration is functional
5. **Form fields include Company Website + Logo** - both working and validated

---

*Last Updated: 2025-09-11 - D1 Migration Complete*