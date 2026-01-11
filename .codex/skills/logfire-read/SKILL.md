---
name: logfire-read
description: "Query Logfire logs via the Logfire query API using read tokens and JSONL output. Use when you need to fetch or filter Logfire records, build log queries, or provide agent-ready log retrieval from this repo. Triggers: Logfire read, query API, JSONL logs, read token, log retrieval, log queries."
---

# Logfire Read Skill

Use this skill to read Logfire records with JSONL output using the repo’s reader utilities.

## Quick Start

1. Load `.env` from the repo root:

```sh
set -a
. ./.env
set +a
```

2. Run the JSONL reader:

```sh
python scripts/logfire-fetch.py
```

Or use the bundled script:

```sh
./.codex/skills/logfire-read/scripts/read_logs.sh --message-like "Processing failed" --limit 10
```

## Agent-Friendly CLI

Use the agent helper for targeted queries:

```sh
python scripts/logfire-read-agent.py --since 2026-01-11T00:00:00Z --message-like "Processing failed" --limit 10
```

## Module API

Use `query_logfire()` for programmatic access:

```python
from logger import query_logfire

rows = query_logfire(jsonl=True, level=21, message_like="Processing failed", limit=10)
for row in rows:
    print(row)
```

## Environment Variables

Required:
- `LOGFIRE_READ_URL` (e.g., `https://logfire-us.pydantic.dev/v1/query`)
- `LOGFIRE_READ_TOKEN`

Optional filters:
- `LOGFIRE_READ_COLUMNS`
- `LOGFIRE_READ_LIMIT`
- `LOGFIRE_READ_SINCE`
- `LOGFIRE_READ_LEVEL`
- `LOGFIRE_READ_MESSAGE_LIKE`
- `LOGFIRE_READ_TRACE_ID`
- `LOGFIRE_READ_SPAN_ID`
- `LOGFIRE_READ_JSONL=true`

## Output Format

- JSONL output returns one JSON object per record.
- `level` is converted to severity strings (`trace`, `debug`, `info`, `warn`, `error`, `fatal`).
