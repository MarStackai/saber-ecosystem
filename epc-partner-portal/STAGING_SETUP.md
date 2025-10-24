# Staging Environment Setup

This document outlines the steps to create and configure the staging environment for the Saber EPC Portal.

## 1. Cloudflare D1 and R2 Setup

Before you can deploy the staging environment, you need to create a new D1 database and R2 bucket for it.

### Create the D1 Database

1.  Go to the Cloudflare dashboard -> **Workers & Pages** -> **D1**.
2.  Click **Create database**.
3.  Enter `staging-epc-form-data` as the database name and click **Create**.
4.  Copy the **Database ID** and paste it into the `wrangler.toml` file under `env.staging.d1_databases.database_id`.

### Create the R2 Bucket

1.  Go to the Cloudflare dashboard -> **R2**.
2.  Click **Create bucket**.
3.  Enter `staging-epc-partner-files` as the bucket name and click **Create**.

## 2. Cloudflare Pages Setup

1.  **Create a new Cloudflare Pages project:**
    *   Go to the Cloudflare dashboard -> **Workers & Pages** -> **Create application** -> **Pages** -> **Connect to Git**.
    *   Select your GitHub repository.
    *   In the **Build and deployments** section, select the `staging` branch.
    *   For the build settings, use the following:
        *   **Framework preset:** Next.js
        *   **Build command:** `npm run build`
        *   **Build output directory:** `out`
    *   Under **Environment variables**, add any necessary variables (e.g., `SHAREPOINT_CLIENT_SECRET`).
    *   Click **Save and Deploy**.

2.  **Add a custom domain:**
    *   Go to your new Pages project -> **Custom domains** -> **Set up a domain**.
    *   Enter `staging-epc.saberrenewable.energy` and click **Continue**.
    *   Follow the instructions to validate the domain.

## 3. DNS Configuration

Cloudflare Pages will automatically create the necessary CNAME record for your custom domain. You just need to ensure that the domain is active.

## 4. Deployment

To deploy to the staging environment, simply push your changes to the `staging` branch:

```bash
git push origin staging
```

Cloudflare Pages will automatically build and deploy the new version to the staging site.
