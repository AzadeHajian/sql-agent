# 🗄️ SQLSpeak — AI Text-to-SQL Assistant

![Component Architecture](pic/architecture.png)

SQLSpeak is a Streamlit app that lets you talk to a Supabase/PostgreSQL
database in plain English. A [LangGraph](https://www.langchain.com/langgraph)
ReAct agent (powered by **GPT-4o** or **Claude**) explores your database,
writes the SQL, runs it, and explains the result — all in a chat interface.

## ✨ Features

- **Natural language → SQL** — ask questions or give instructions in plain English.
- **Explores before guessing** — the agent always checks which tables exist,
  their schema, and sample data before writing a query.
- **Reads *and* writes** — `SELECT` queries run immediately; for anything
  that changes data (`CREATE TABLE`, `INSERT`, etc.) the agent explains what
  it's about to do and asks you to confirm first.
- **Transparent** — every response shows the exact SQL the agent executed,
  not just the result.
- **Switchable LLM provider** — pick GPT-4o (OpenAI, default) or Claude
  (Anthropic) from the sidebar at any time.
- **MCP server included** — the same database tools are also exposed over
  the [Model Context Protocol](https://modelcontextprotocol.io/), so other
  MCP clients (e.g. Claude Desktop) can use them too.

## 📸 Demo

**Chat UI** — pick a provider (GPT-4o by default), see your Supabase
connection, and ask questions or give instructions via the chat box pinned
at the bottom:

![Main chat UI](pic/llm1.png)

**Exploring the database** — the agent lists existing tables, then for a
request that would change data (creating a `students` table and filling it
with 50 rows) it explains the plan and asks for confirmation:

![Agent proposes creating a table](pic/llm2.png)

**Confirming the plan** — the agent restates exactly what it's about to do
(table name, columns, 50 sample rows) before touching the database:

![Agent confirms the plan with the user](pic/llm3.png)

**Executing the change** — once confirmed, the agent runs the SQL itself and
reports back:

![Agent reports the table was created and populated](pic/llm4.png)

**Viewing the results** — asking to "view" the data shows the first rows in
a clean table:

![Agent shows the first 5 rows of the students table](pic/llm5.png)

**Verified in Supabase** — the `students` table (and its columns) really was
created in the project's Postgres database:

![Supabase schema visualizer showing the new students table](pic/supabase_pic.png)

## 🏗️ How it works

### Component architecture

![Component architecture](pic/architecture.png)

The app is built in four layers. The **Streamlit UI** collects the user's
question and shows the answer. The **SQLAgent** bridges the synchronous
Streamlit world to the async MCP layer. The **MCP Client + ReAct Agent**
spawns `tools/supabase_tool.py` as a subprocess, loads its four tools over
stdio, and drives a LangGraph ReAct loop powered by the chosen **LLM**
(GPT-4o or Claude). The **FastMCP Tool Server** translates each tool call
into a Supabase RPC call that executes SQL on the PostgreSQL database.

### Data flow — what happens per query

![Data flow per query](pic/data_flow.png)

Each user question goes through seven steps:

1. **User types** a question in the Streamlit chat box.
2. **`SQLAgent.run()`** wraps the call in `asyncio.run()` to bridge sync → async.
3. The **MCP client** spawns `tools/supabase_tool.py` as a subprocess (stdio).
4. **4 MCP tools** are loaded into LangGraph's ReAct agent.
5. The **ReAct loop** asks the LLM which tool to call next; the LLM
   explores the database step-by-step (`list_tables` → `get_table_schema`
   → `get_sample_rows`).
6. The **LLM composes the SQL** and calls `execute_sql()` — Supabase
   returns the rows.
7. The **answer** (SQL + plain-English explanation + results) is returned
   to the Streamlit chat.

The system prompt (`agent/prompt.py`) tells the agent to always explore
before writing SQL, to execute SQL itself (never ask the user to run it),
to always show the SQL it ran, and to ask for confirmation before any
destructive or data-changing statement.

For a deeper dive, see [`.claude/docs/ARCHITECTURE.md`](.claude/docs/ARCHITECTURE.md)
and [`.claude/docs/PROJECT_OVERVIEW.md`](.claude/docs/PROJECT_OVERVIEW.md).

## 🧰 Tech stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io/) |
| Agent | [LangGraph](https://www.langchain.com/langgraph) `create_react_agent` |
| LLMs | OpenAI GPT-4o / Anthropic Claude (via LangChain) |
| Database | [Supabase](https://supabase.com/) (PostgreSQL) |
| Tool protocol | [FastMCP](https://github.com/jlowin/fastmcp) + [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) (stdio) |
| Tracing | LangSmith (optional) |

## 📁 Project structure

```
main.py                       # Streamlit UI (only file with UI code)
agent/                        # SQLAgent class + system prompts
llm/                          # Provider abstraction (Anthropic / OpenAI)
tools/supabase_tool.py        # FastMCP stdio server — the 4 Supabase tools
mcp_server/client.py          # Async MCP client + LangGraph ReAct agent
```

See [`.claude/docs/PROJECT_OVERVIEW.md`](.claude/docs/PROJECT_OVERVIEW.md)
for a full folder-by-folder breakdown.

## ⚙️ Setup

### Requirements

- Python 3.10
- A Supabase project with a Postgres RPC function called `execute_sql`
  (the SQL to create it is in
  [`.claude/docs/SETUP.md`](.claude/docs/SETUP.md#database-setup) — **the
  app cannot query the database without it**)

### Install

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file (never commit it) with:

| Variable | Notes |
|---|---|
| `OPENAI_API_KEY` | required for the GPT-4o provider (default) |
| `ANTHROPIC_API_KEY` | required for the Claude provider |
| `SUPABASE_URL` | your Supabase project REST URL |
| `SUPABASE_ANON_KEY` | Supabase anon/public key |
| `SUPABASE_PROJECT_ID` | used to set up the `execute_sql` function |
| `SUPABASE_ACCESS_TOKEN` | Supabase Management API token (setup only) |
| `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_ENDPOINT`, `LANGSMITH_PROJECT` | optional, for tracing |

Full details in [`.claude/docs/SETUP.md`](.claude/docs/SETUP.md).

### Run

```bash
streamlit run main.py
```

Open the app, pick a provider in the sidebar (GPT-4o is selected by
default), and start chatting at the bottom of the page. The MCP tool
server (`tools/supabase_tool.py`) is spawned automatically as a
subprocess — no separate terminal needed.

## 💬 Example questions

- "What tables exist in the database?"
- "Show me the first 5 rows of each table"
- "How many records are in the transaction table?"
- "Create a table called students with columns Name, Family Name, Address,
  Class Name, Grade and fill it with 50 sample rows"

## 🔒 Security notes

- The agent's guardrails (read-only by default, no `DROP`/`TRUNCATE`,
  confirm before writes, always show the SQL) are **prompt-level** — see
  `agent/prompt.py`. There is no separate query-parsing/allowlist layer.
- The `execute_sql` Postgres function (see
  [`.claude/docs/SETUP.md`](.claude/docs/SETUP.md#database-setup)) runs with
  `security definer` and is granted to the `anon` role, so it can execute
  arbitrary SQL — including writes and DDL — using the Supabase anon key.
  This is intentional (it's what lets the agent create/populate tables), but
  keep your anon key and `.env` private.

## 📚 More documentation

- [`.claude/CLAUDE.md`](.claude/CLAUDE.md) — project guide index
- [`.claude/docs/PROJECT_OVERVIEW.md`](.claude/docs/PROJECT_OVERVIEW.md) — folder-by-folder breakdown
- [`.claude/docs/ARCHITECTURE.md`](.claude/docs/ARCHITECTURE.md) — data flow, provider abstraction, MCP
- [`.claude/docs/SETUP.md`](.claude/docs/SETUP.md) — env vars, install, database setup
- [`.claude/docs/DEBUGGING_LOG.md`](.claude/docs/DEBUGGING_LOG.md) — history of bugs found/fixed
