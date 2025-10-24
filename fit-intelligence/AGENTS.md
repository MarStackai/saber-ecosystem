# Repository Guidelines

## Project Structure & Module Organization
- API: `fit_api_server.py` (Flask) serves REST endpoints and static UI under `visualizations/`.
- Chat/Logic: `llm_enhanced_chatbot.py`, `enhanced_fit_intelligence_api.py` (Chroma vector store in `chroma_db/`).
- Ops: `deployment/systemd/` (user-level services), `scripts/` (helper scripts).
- Tests: `test_*.py` at repo root target core flows.

## Build, Test, and Development Commands
- Run API locally: `env TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 venv/bin/python fit_api_server.py`
- Health: `curl http://localhost:5000/api/health`
- Map data: `GET /api/chroma/clusters`, `POST /api/chroma/business_query`
- Restart services: `./scripts/restart_fit_stack.sh`

## Coding Style & Naming Conventions
- Python 3.12, 4-space indentation, `snake_case` for functions/vars, `CamelCase` for classes.
- Keep modules cohesive, prefer pure helpers, log via `logging` (INFO default).
- Static HTML/JS: avoid inline secrets; fetch runtime config from `/api/config`.

## Testing Guidelines
- Name tests `test_<area>.py` (e.g., `test_system.py`).
- Mock network/LLM where possible; keep tests deterministic.
- Run with `python -m pytest -q` (if pytest is available) or target files via `python file.py` for smoke checks.

## Commit & Pull Request Guidelines
- Commits: imperative subject (“Add clusters endpoint”), include “what + why”.
- PRs: brief description, endpoints touched, manual test notes, and screenshots for UI changes.

## Security & Configuration Tips
- Mapbox token: set `MAPBOX_TOKEN` in the environment; clients fetch it from `GET /api/config`.
- Offline mode: set `TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1` to avoid network pulls.
- Autostart: copy `deployment/systemd/*.service` to `~/.config/systemd/user/` and `systemctl --user enable --now fit-api.service fit-cloudflared.service`.
