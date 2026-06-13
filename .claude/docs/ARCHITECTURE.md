# Architecture

## Request flow (Streamlit path)

```
User types question in main.py (Streamlit chat form)
  └─> SQLAgent.run(user_message, chat_history)        [agent/agent.py]
        ├─ converts chat_history dicts -> HumanMessage/AIMessage
        ├─ invokes a LangGraph create_react_agent(model, tools, prompt)
        │     model  = llm.get_llm(provider).client     [llm/]
        │     tools  = SUPABASE_TOOLS                    [tools/__init__.py]
        │     prompt = agent.prompt.get_full_prompt()    [agent/prompt.py]
        │
        │   ReAct loop (driven by the LLM, following task_prompt steps):
        │     1. list_tables()        -> information_schema.tables
        │     2. get_table_schema(t)  -> information_schema.columns
        │     3. get_sample_rows(t)   -> SELECT * FROM t LIMIT 5
        │     4. (LLM composes SQL)
        │     5. execute_sql(query)   -> runs the SQL
        │     6. (LLM explains results in prose + ```sql block)
        │
        └─> returns response["messages"][-1].content (a string)
  └─> appended to st.session_state.chat_history, rendered in chat UI
```

All four tools call `_get_client()` in `tools/supabase_tools.py`, which
builds a `supabase.Client` from `SUPABASE_URL` / `SUPABASE_ANON_KEY` and
issues everything through a single Postgres RPC function named
`execute_sql` (defined Supabase-side, not in this repo).

## Provider abstraction

```
agent.py --> llm.get_llm(provider) --> BaseLLM
                                          ├─ AnthropicLLM  (ChatAnthropic, claude-sonnet-4-5-20250929)
                                          └─ OpenAILLM     (ChatOpenAI, gpt-4o-2024-11-20)
```

`create_react_agent` is given `llm.client` — the underlying LangChain chat
model — directly, so LangGraph drives the tool-calling loop itself.
Switching provider in the Streamlit sidebar just rebuilds `SQLAgent` with
the other provider.

## System prompt composition

`agent/prompt.py` builds the system prompt as
`task_prompt() + "\n" + security_prompt()`:

- **task_prompt** — the EXPLORE → UNDERSTAND → PREVIEW → GENERATE →
  EXECUTE → EXPLAIN chain-of-thought, with a worked example.
- **security_prompt** — read-only by default, no destructive DDL/DML,
  no raw SQL injection, stay within this DB's `public` schema, always
  show the SQL.

These are prompt-level guardrails only — there is no query-parsing layer
that enforces them in code. `tools/supabase_tools.py` will execute whatever
SQL string the LLM passes to `execute_sql`.

## MCP server (alternative integration path)

`mcp_server/server.py` wraps the *same* underlying tool functions
(`tools/supabase_tools.py`) and re-exposes them as MCP tools
(`list_all_tables`, `get_schema`, `sample_rows`, `run_sql`) via FastMCP.
This lets any MCP-compatible client (e.g. Claude Desktop, another agent)
use the Supabase tools without going through the Streamlit `SQLAgent`.
It is currently a separate entry point (`python -m mcp_server.server`),
not invoked by `main.py`.
