# Setup & Running

## Requirements
- Python 3.10 (matches `.venv/lib/python3.10`)
- A Supabase project with a Postgres RPC function called `execute_sql`
  (callable as `client.rpc("execute_sql", {"query": "..."})`) — required by
  every tool in `tool/supabase_tools.py`.

## Install
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Environment variables (`.env`, gitignored — never commit real values)

| Variable | Used by | Notes |
|---|---|---|
| `OPENAI_API_KEY` | `llm/openai_client.py` | required only if provider = `openai` |
| `ANTHROPIC_API_KEY` | `llm/anthropic_client.py` | required only if provider = `anthropic` |
| `LLM_PROVIDER` | (informational) | actual provider is chosen via Streamlit sidebar / `SQLAgent(provider=...)`, default `"anthropic"` |
| `LANGSMITH_TRACING` | LangChain/LangGraph | enables tracing |
| `LANGSMITH_ENDPOINT` | LangChain/LangGraph | e.g. `https://eu.api.smith.langchain.com` |
| `LANGSMITH_API_KEY` | LangChain/LangGraph | |
| `LANGSMITH_PROJECT` | LangChain/LangGraph | e.g. `sqlspeak` |
| `SUPABASE_URL` | `tool/supabase_tools.py` | project REST URL |
| `SUPABASE_ANON_KEY` | `tool/supabase_tools.py` | anon/public key used by `create_client` |
| `SUPABASE_ACCESS_TOKEN` | (informational/CLI use) | not read directly by app code |
| `SUPABASE_PROJECT_ID` | (informational) | not read directly by app code |

> **Tip:** if env vars seem to not load, check `.env` for stray spaces
> around `=` or trailing spaces on values (e.g. `KEY =value` or
> `value ` with a trailing space) — `python-dotenv` treats these literally.

## Run the Streamlit app
```bash
streamlit run main.py
```

## Run the MCP server (separate entry point)
```bash
python -m mcp_server.server
```

## Before running for the first time
There is a known import-path bug that will raise `ModuleNotFoundError: No
module named 'tools'` as soon as `agent/agent.py` (and `mcp_server/server.py`)
are imported, because the code imports from `tools` but the directory is
`tool/`. See `DEBUGGING_LOG.md` for details/status before assuming a fresh
error is something new.
