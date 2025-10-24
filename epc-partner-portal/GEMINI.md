# Saber Business Operations

## Project Overview

This repository contains the complete operational infrastructure for Saber Renewables' business operations, centered around the EPC (Engineering, Procurement, and Construction) Partner Portal. The system is designed to manage the partner onboarding process, from initial invitation to final application submission and review.

The architecture is a hybrid solution that leverages a public-facing frontend hosted on Cloudflare Pages, with a backend managed through SharePoint and Power Automate. This setup provides a seamless and professional experience for external partners while allowing the internal operations team to manage the process using familiar SharePoint lists and workflows.

**Main Technologies:**

*   **Frontend:** Next.js (React)
*   **Hosting:** Cloudflare Pages
*   **Serverless Functions:** Cloudflare Workers
*   **Database:** Cloudflare D1 (SQLite)
*   **File Storage:** Cloudflare R2
*   **Backend/Integration:** SharePoint Lists, Power Automate
*   **Automation:** PowerShell, Shell scripts

## Building and Running

The core of the project is the Next.js application located in the `epc-portal-react` directory.

### Development

To run the local development server:

```bash
cd epc-portal-react
npm install
npm run dev
```

### Build

To build the application for production:

```bash
cd epc-portal-react
npm run build
```

### Linting

To run the linter and check for code quality issues:

```bash
cd epc-portal-react
npm run lint
```

### Deployment

Deployment is handled automatically via Cloudflare Pages. Pushing to the `main` branch will trigger a new deployment.

## Development Conventions

*   **Code Style:** The project uses ESLint for code linting. Adhere to the rules defined in `.eslintrc.json`.
*   **Testing:** The repository contains a `/tests` directory, but a formal testing framework does not appear to be in place.
*   **Branching:** The `main` branch is the production branch. All development should be done on separate feature branches and merged into `main` via pull requests.
*   **Commits:** Commit messages should be clear and descriptive.

## AI Agent Guidelines

All AI agents working on this project are expected to adhere to the rules and guidelines outlined in the `agents.md` file. This file contains critical information regarding security, code quality, and interaction protocols. Before making any changes, please familiarize yourself with the contents of `agents.md`.