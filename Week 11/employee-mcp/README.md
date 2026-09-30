# MCP Employee Demo

Postgres (Docker) -> MCP server (tools, resources, prompts) -> OpenAI agent (MCP client).

## Setup

```bash
python -m venv .venv 
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
python setup_db.py                      # starts Postgres in Docker + loads simulated data
python agent.py                         # starts the server automatically over stdio
```

## Inspect the server without an LLM

```bash
mcp dev server.py        # opens the MCP Inspector in the browser
```

## Try these in the agent

1. `Who are the employees in Data & AI and what do they earn?`  (tools)
2. `What does our policy say about promotions?`                  (resource)
3. `Write a performance review for Vikram Rao`                   (prompt + tools + resources)
4. `Is anyone in Sales underpaid relative to performance?`       (prompt + tools)
5. `Give me a leadership briefing on team health`                (prompt)

## Files

| File               | Purpose                                                                    |
| ------------------ | -------------------------------------------------------------------------- |
| `setup_db.py`    | Creates the Docker container, applies`db/schema.sql` and `db/seed.sql` |
| `server.py`      | MCP server: 7 tools, 2 resources + 1 resource template, 3 prompts          |
| `agent.py`       | MCP client + OpenAI tool-calling loop                                      |
| `resources/*.md` | Text served as MCP resources                                               |
| `config.py`      | DB connection settings (env-overridable)                                   |

Tables: `departments`, `employees`, `salaries`, `work_assignments` (all data is fictional).
