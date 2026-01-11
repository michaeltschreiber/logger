import json
import os
import urllib.error
import urllib.parse
import urllib.request


def _env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _escape_sql_literal(value):
    return value.replace("'", "''")


def _escape_like(value):
    return _escape_sql_literal(value).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _build_sql(
    *,
    columns=None,
    limit=None,
    since=None,
    level=None,
    message_like=None,
    trace_id=None,
    span_id=None,
):
    columns = columns or os.getenv(
        "LOGFIRE_READ_COLUMNS",
        "created_at,start_timestamp,message,level,trace_id,span_id,span_name,attributes_reduced,attributes,service_name,project_id",
    )
    limit = limit or int(os.getenv("LOGFIRE_READ_LIMIT", "100"))
    since = since or os.getenv("LOGFIRE_READ_SINCE")
    level = level or os.getenv("LOGFIRE_READ_LEVEL")
    message_like = message_like or os.getenv("LOGFIRE_READ_MESSAGE_LIKE")
    trace_id = trace_id or os.getenv("LOGFIRE_READ_TRACE_ID")
    span_id = span_id or os.getenv("LOGFIRE_READ_SPAN_ID")

    sql = f"SELECT {columns} FROM records WHERE 1=1"
    if since:
        sql += f" AND start_timestamp >= '{_escape_sql_literal(since)}'"
    if level:
        sql += f" AND level = '{_escape_sql_literal(level)}'"
    if message_like:
        sql += f" AND message LIKE '%{_escape_like(message_like)}%'"
    if trace_id:
        sql += f" AND trace_id = '{_escape_sql_literal(trace_id)}'"
    if span_id:
        sql += f" AND span_id = '{_escape_sql_literal(span_id)}'"
    sql += f" ORDER BY start_timestamp DESC LIMIT {limit}"
    return sql


def query_logfire(
    sql=None,
    *,
    url=None,
    token=None,
    header=None,
    scheme=None,
    jsonl=None,
    columns=None,
    limit=None,
    since=None,
    level=None,
    message_like=None,
    trace_id=None,
    span_id=None,
):
    url = url or os.getenv("LOGFIRE_READ_URL")
    token = token or os.getenv("LOGFIRE_READ_TOKEN")
    if not url or not token:
        raise RuntimeError("LOGFIRE_READ_URL and LOGFIRE_READ_TOKEN must be set.")

    sql = sql or os.getenv("LOGFIRE_READ_SQL")
    if not sql:
        sql = _build_sql(
            columns=columns,
            limit=limit,
            since=since,
            level=level,
            message_like=message_like,
            trace_id=trace_id,
            span_id=span_id,
        )
    query = urllib.parse.urlencode({"sql": sql})
    if "?" in url:
        url = f"{url}&{query}"
    else:
        url = f"{url}?{query}"

    header = header or os.getenv("LOGFIRE_READ_HEADER", "Authorization")
    scheme = scheme or os.getenv("LOGFIRE_READ_SCHEME", "Bearer")
    if header.lower() == "authorization" and scheme:
        header_value = f"{scheme} {token}"
    else:
        header_value = token

    req = urllib.request.Request(url)
    req.add_header(header, header_value)
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        raise RuntimeError(f"Request failed: HTTP {exc.code} {body}".strip()) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc}") from exc

    parsed = json.loads(payload)
    jsonl = _env_flag("LOGFIRE_READ_JSONL", default=False) if jsonl is None else jsonl
    if jsonl and isinstance(parsed, dict) and "columns" in parsed:
        columns = parsed.get("columns", [])
        names = [col.get("name") for col in columns]
        values = [col.get("values", []) for col in columns]
        return [dict(zip(names, row)) for row in zip(*values)]

    return parsed
