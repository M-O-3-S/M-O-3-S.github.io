# AGENTS.md

This file is the single source of truth for AI coding tools working in this repository.

## 1) Scope
- Repository: `M-O-3-S.github.io`
- Goal: Collect AI news, summarize/tag with local LLM, publish JSON for static frontend, notify via Telegram.

## 2) Read Order (For Any AI Tool)
1. `AGENTS.md` (this file)
2. `README.md`
3. `docs/PRD_AI_News_Archive.md`
4. `docs/DEV_Requirements_AI_News_Archive.md`
5. `docs/SWDesign/Architecture_Design.md`

If instructions conflict: `AGENTS.md` > code reality > older docs.

## 3) Repository Map
- `backend/src/`: pipeline modules (`crawler`, `processor`, `publisher`, `deploy`, `scheduler`, `main`)
- `backend/config/`: runtime config and env template
- `frontend/`: static site assets + generated data files
- `docs/`: PRD, architecture, UX, operations docs
- `tests/`: PoC and infra tests

## 4) Quick Commands
- Run scheduler (recommended): `./start_news_archive_scheduler.sh`
- Run daily once: `python3 backend/src/main.py --mode daily`
- Run weekly once: `python3 backend/src/main.py --mode weekly`
- Tail scheduler logs: `tail -f logs/scheduler.log`
- Stop scheduler: `kill $(cat logs/scheduler.pid)`

## 5) Config Contract
- Main config: `backend/config/config.yml`
- Secrets: `backend/config/.env` (from `.env.example`)
- LLM model should be managed from config and remain swappable.
- Daily/weekly schedule must remain configurable from `config.yml`.

## 6) Editing Rules For AI Tools
- Keep changes minimal and scoped to user request.
- Do not rewrite large docs unless requested.
- Do not hardcode calendar/date logic in frontend for specific month/year.
- Do not commit secrets (`.env`, tokens).
- Avoid committing runtime artifacts (DB files, lock files, transient logs) unless explicitly requested.

## 7) Data/Interface Contract (Backend -> Frontend)
- Backend publishes JSON files under `frontend/data/`.
- Frontend consumes only static JSON (no backend server dependency).
- Preserve shape consistency for:
  - `frontend/data/index.json`
  - `frontend/data/daily/YYYY-MM-DD.json`
  - `frontend/data/tags/<tag>.json`
  - `frontend/data/weekly/YYYY_Wxx.json`

## 8) Definition of Done (When AI Makes Code Changes)
- Code builds/runs for changed path.
- Relevant script/test executed when possible.
- Any config key changes are reflected in docs.
- User-visible behavior changes are noted in final summary.

## 9) Known High-Priority Gaps (Track While Implementing)
- Config key mismatch between docs and runtime usage.
- Deploy conflict-safety (`pull --rebase`) missing in deploy flow.
- Calendar/date behavior has hardcoded month/date assumptions.
- Weekly data availability/fallback UX should be robust.

