# Staging Domain Setup

I have successfully set up the staging environment for the Saber EPC Portal. This includes:

*   A new D1 database for staging data.
*   A new R2 bucket for staging file storage.
*   A new Cloudflare Pages project for the staging site.

However, I was unable to automatically add the custom domain `staging-epc.saberrenewable.energy` to the new Pages project. This is a limitation of the `wrangler` command-line tool.

You will need to add the custom domain manually in the Cloudflare dashboard.

## Instructions

1.  Go to the Cloudflare dashboard -> **Workers & Pages**.
2.  Select the `saber-epc-portal-staging` Pages project.
3.  Go to the **Custom domains** tab.
4.  Click **Set up a domain**.
5.  Enter `staging-epc.saberrenewable.energy` and click **Continue**.
6.  Follow the instructions to validate the domain.

Once you have added the custom domain, the staging environment will be available at `https://staging-epc.saberrenewable.energy`.

To deploy to the staging environment, simply push your changes to the `staging` branch:

```bash
git push origin staging
```
