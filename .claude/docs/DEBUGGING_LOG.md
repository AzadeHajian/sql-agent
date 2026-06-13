# Debugging Log

Running history of bugs investigated in this repo. **Read this before
starting a new debugging session** — the symptom you're seeing may already
be diagnosed (and possibly still open) below.

**After every debugging session, append a new entry** using the template
at the bottom: date, symptom, root cause, fix/status, files touched. This
applies whether or not the issue was actually fixed — "diagnosed but not
fixed yet" is still worth recording so the next session doesn't redo the
investigation.

---

## 2026-06-13 — `ModuleNotFoundError: No module named 'tools'`

**Symptom:** `streamlit run main.py` fails with
`ModuleNotFoundError: No module named 'tools'` at
`agent/agent.py:18 -> from tools import SUPABASE_TOOLS`. Same root cause
would also break `python -m mcp_server.server`.

**Root cause:** `agent/agent.py` does `from tools import SUPABASE_TOOLS`
and `mcp_server/server.py` does
`from tools.supabase_tools import (execute_sql, list_tables,
get_table_schema, get_sample_rows)`, but the package in this repo was named
`tool/` (singular) — there was no top-level `tools` package.

**Fix/status:** **FIXED.** Renamed `tool/` → `tools/` via `git mv` (the
internal header comments already said `tools/...`, and nothing else in the
codebase imports `tool.*`, so no other files needed changes). Verified via
WSL venv: `from tools import SUPABASE_TOOLS` and `from agent import
SQLAgent` both import cleanly, and `_get_client()` successfully builds a
Supabase client from the existing `.env` values.

**Files involved:** `tool/` → `tools/` (renamed, contains `__init__.py`,
`supabase_tools.py`). `agent/agent.py` and `mcp_server/server.py` were
already correct and needed no edits.

---

## 2026-06-13 — `_get_client()` error handling

**Symptom:** N/A (proactive change, not triggered by an error) — request
was to verify `SUPABASE_URL` / `SUPABASE_ANON_KEY` are present in `.env`
and wrap `create_client()` in try/except.

**Root cause:** `.env` checked and both `SUPABASE_URL` and
`SUPABASE_ANON_KEY` are present and parse correctly (no trailing-whitespace
issues — python-dotenv strips them). `create_client(url, key)` itself had
no error handling, so any failure there (bad URL format, network issue)
would surface as a raw, unlabeled exception.

**Fix/status:** **FIXED.** `tools/supabase_tools.py::_get_client()` now
wraps `create_client(url, key)` in try/except and re-raises as
`RuntimeError(f"Failed to create Supabase client: {e}")`, consistent with
the error-wrapping style already used in `llm/anthropic_client.py` and
`llm/openai_client.py`.

**Files involved:** `tools/supabase_tools.py`.

---

## Template for new entries

```
## YYYY-MM-DD — short symptom description

**Symptom:** what you observed (error message, wrong output, etc.)

**Root cause:** what was actually wrong.

**Fix/status:** what was changed (or "OPEN" if not yet fixed) and why.

**Files involved:** list of files touched or relevant.
```
