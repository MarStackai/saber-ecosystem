# Architecture Overview

## Runtime Components
- Flask API (`fit_api_server.py`): Serves REST endpoints and static UI from `visualizations/`.
- Chat/Reasoner (`llm_enhanced_chatbot.py`): Hybrid flow combining rule-based parsing, optional LLM intent understanding, and vector search.
- Data Layer (`enhanced_fit_intelligence_api.py` + `chroma_db/`): Chroma PersistentClient with prepared collections (e.g., `commercial_fit_sites`).
- Warm Index (`warm_index.py`): In‑memory embedding + metadata cache for fast, deterministic geo/site filtering.
- Config Endpoint: `GET /api/config` exposes minimal runtime config (e.g., `MAPBOX_TOKEN`).

## Key Request Paths
- Health: `GET /api/health` → basic status and collection counts.
- Map Data:
  - `GET /api/chroma/clusters` → postcode‑area buckets (site_count, capacity, urgent).
  - `POST /api/chroma/business_query` → normalized site list + BI summary.
- Chat: `POST /api/chat` → enhanced response using warm index; returns `{ success: true, ... }`.

## Data Flow
1) User/UI hits API → router in Flask.
2) Queries pass to `LLMEnhancedFITChatbot.process_query()` or API search helpers.
3) Warm Index filters candidates by area/prefix and attributes; returns normalized metadata.
4) Optional financial enrichers compute derived fields for UI (e.g., remaining FIT years).

## Deployment & Ops
- User‑level systemd units in `deployment/systemd/` (API + Cloudflare tunnel).
- Logs: `~/fit_api_server.out` (API), `~/cloudflared-fit.log` (tunnel).
- Configuration via env: `MAPBOX_TOKEN`, `TRANSFORMERS_OFFLINE`, `HF_HUB_OFFLINE`.

## Extensibility Points
- Add endpoints in `fit_api_server.py` under `/api/...`.
- Add vector collections in `enhanced_fit_intelligence_api.py` and surface via warm index.
- Frontend pages live in `visualizations/` (Mapbox/Leaflet). Fetch runtime config from `/api/config`.
