# Security & Configuration

## Secrets & Configuration
- Do not hardcode secrets in source or HTML. Provide sensitive values via environment variables.
- Mapbox: set `MAPBOX_TOKEN` in the API environment. Clients obtain it from `GET /api/config`.
- Keep `TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1` when running air‑gapped or to avoid unexpected downloads.

## Dependencies & Supply Chain
- Prefer pinned versions in `requirements*.txt` where feasible.
- Review new packages for transitive risk before adding to the server path.

## Network Exposure
- API binds to `0.0.0.0:5000`. Access is normally brokered through Cloudflare Tunnel.
- Verify Cloudflare Access policy for public hostnames; expect redirects to login when unauthenticated.

## Data Protection
- Chroma data under `chroma_db/` may contain aggregated site information. Limit OS‑level access to the serving user.
- Avoid exporting raw data in APIs not intended for bulk download.

## Operational Hardening
- Run API and tunnel as user services (systemd) rather than root.
- Log review: `~/fit_api_server.out` and `~/cloudflared-fit.log`. Rotate if files grow large.
- Backups: snapshot `chroma_db/` during maintenance windows; stop the API before copying for consistency.

## Reporting
- For suspected vulnerabilities or exposure, capture logs, disable public routes via Cloudflare, and notify maintainers with steps to reproduce.
