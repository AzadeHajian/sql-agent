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

**Symptom:** Importing `SQLAgent` (`from agent import SQLAgent`, used by
`main.py`) or running `python -m mcp_server.server` fails at import time.

**Root cause:** `agent/agent.py` does `from tools import SUPABASE_TOOLS`
and `mcp_server/server.py` does
`from tools.supabase_tools import (execute_sql, list_tables,
get_table_schema, get_sample_rows)`, but the package in this repo is named
`tool/` (singular) — there is no top-level `tools` package, and none of the
installed dependencies provide one either.

**Fix/status:** **OPEN — not fixed yet.** Options: rename `tool/` →
`tools/` (matches what the importers expect, but changes the package name
everywhere it's imported from `tool.*`), or change the two import
statements to `from tool import SUPABASE_TOOLS` /
`from tool.supabase_tools import ...`. Either works; pick one and update
`ARCHITECTURE.md` / `PROJECT_OVERVIEW.md` if the directory name changes.

**Files involved:** `agent/agent.py`, `mcp_server/server.py`, `tool/`.

---

## Template for new entries

```
## YYYY-MM-DD — short symptom description

**Symptom:** what you observed (error message, wrong output, etc.)

**Root cause:** what was actually wrong.

**Fix/status:** what was changed (or "OPEN" if not yet fixed) and why.

**Files involved:** list of files touched or relevant.
```
