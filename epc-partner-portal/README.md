# Saber EPC Partner Portal

This repository contains the complete infrastructure for the Saber Renewable Energy EPC (Engineering, Procurement, and Construction) Partner Portal. The project automates the onboarding and management of EPC partners using a combination of a public-facing web application and a Microsoft 365 backend.

## 🚀 Development Configuration (Updated 2025-09-23)

### Port Configuration
- **Frontend (Next.js)**: Port **4200** (avoids common 3000-3003 conflicts)
- **Backend (Wrangler)**: Port **8787**
- **Staging Worker**: Port **8788**

### Quick Start
```bash
# Frontend - runs on port 4200
cd epc-portal-react && npm run dev

# Backend Worker - runs on port 8787
npx wrangler dev --local --port 8787
```

## Tech Stack

- **Frontend:** Next.js, React, Tailwind CSS
- **Backend:** Cloudflare Workers, D1, R2
- **Automation:** SharePoint Online, Power Automate
- **Infrastructure as Code:** PowerShell (PnP.PowerShell)
- **Testing:** Playwright for End-to-End tests

## Project Structure

The repository is organized as a monorepo with the following key directories:

- **/public-deployment**: The Next.js application that serves as the public-facing portal for EPC partners.
- **/scripts**: Contains all PnP.PowerShell scripts for provisioning, managing, and automating the SharePoint backend.
- **/sharepoint-pages**: Markdown source files for documentation and content pages to be deployed on the SharePoint site.
- **/syntax**: A documentation site and design system built on "Tailwind Plus," providing component examples in both JavaScript and TypeScript.
- **/tests**: End-to-end tests for the public portal, written with Puppeteer.
- **CLAUDE.md**: A strict set of guidelines for AI-assisted development to ensure code quality, security, and consistency.
- **agents.md**: Documentation on the roles and responsibilities of the AI agents used in this project.

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MarStackai/saber-epc-portal.git
    cd saber-epc-portal
    ```

2.  **Install Frontend Dependencies:**
    ```bash
    cd public-deployment
    npm install
    ```

3.  **Configure Environment Variables:**
    Create a `.env.local` file in the `public-deployment` directory and add the necessary environment variables for connecting to the SharePoint backend.

4.  **Provision the SharePoint Backend:**
    Navigate to the `/scripts` directory and run the `setup-epc-portal.ps1` script after configuring your SharePoint connection details.

## Key Components

### 1. SharePoint Backend
The entire business process is anchored in SharePoint. The `/scripts` handle the automated creation of:
- A dedicated SharePoint Team Site.
- The `EPC Onboarding` list to store partner data.
- The `EPC Submissions` document library for storing evidence and compliance documents.

### 2. Public Portal
A modern, responsive web application where external partners can submit their onboarding information and upload required documents.

### 3. Automation Flows
Power Automate flows (or equivalent PowerShell scripts) are used to process new submissions, create folders for each partner, notify internal stakeholders, and manage the review and approval process.
