# Setup & Running

## Requirements
- Python 3.10 (matches `.venv/lib/python3.10`)
- A Supabase project with a Postgres RPC function called `execute_sql`
  (callable as `client.rpc("execute_sql", {"query": "..."})`) — required by
  every tool in `tools/supabase_tools.py`. See "Database setup" below.

## Database setup

Run this once in the Supabase SQL Editor for the project (it's not part of
any default Supabase project — without it every tool in
`tools/supabase_tools.py` fails with `PGRST202: Could not find the function
public.execute_sql(query) in the schema cache`):

```sql
create or replace function public.execute_sql(query text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  result jsonb;
  cleaned text;
begin
  cleaned := regexp_replace(trim(query), ';\s*$', '');

  if cleaned ~* '^\s*(select|with)\s' then
    execute format('select coalesce(jsonb_agg(t), ''[]''::jsonb) from (%s) t', cleaned) into result;
  else
    execute cleaned;
    result := jsonb_build_object('status', 'ok');
  end if;

  return result;
end;
$$;

grant execute on function public.execute_sql(text) to anon, authenticated, service_role;
```

This strips a trailing `;` (the tools' queries all end with one, which would
otherwise be a syntax error inside the wrapping subquery). `SELECT`/`WITH`
queries are wrapped to return rows as a JSON array; everything else (DDL like
`CREATE TABLE`, or DML like `INSERT`/`UPDATE`/`DELETE`) is executed directly
and returns `{"status": "ok"}` — these can't be used inside a `FROM (...)`
subquery, which is why the original wrapped-only version raised
`42601: syntax error at or near "CREATE"` for anything but a `SELECT`.
`security definer` + granting to `anon` means the anon key can run arbitrary
SQL (including writes/DDL) against this project — intentional, since
`execute_sql` in `tools/supabase_tools.py` is designed to support
inserts/updates/creates when the user asks for them, but worth knowing since
the anon key is the least-privileged credential by convention.

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
| `LLM_PROVIDER` | (informational) | actual provider is chosen via Streamlit sidebar (defaults to `"openai"` / GPT-4o) or `SQLAgent(provider=...)` (constructor default `"anthropic"`) |
| `LANGSMITH_TRACING` | LangChain/LangGraph | enables tracing |
| `LANGSMITH_ENDPOINT` | LangChain/LangGraph | e.g. `https://eu.api.smith.langchain.com` |
| `LANGSMITH_API_KEY` | LangChain/LangGraph | |
| `LANGSMITH_PROJECT` | LangChain/LangGraph | e.g. `sqlspeak` |
| `SUPABASE_URL` | `tools/supabase_tools.py` | project REST URL |
| `SUPABASE_ANON_KEY` | `tools/supabase_tools.py` | anon/public key used by `create_client` |
| `SUPABASE_ACCESS_TOKEN` | (informational/CLI use) | not read directly by app code |
| `SUPABASE_PROJECT_ID` | (informational) | not read directly by app code |

## Run the Streamlit app
```bash
streamlit run main.py
```

## Run the MCP server (separate entry point)
```bash
python -m mcp_server.server
```

