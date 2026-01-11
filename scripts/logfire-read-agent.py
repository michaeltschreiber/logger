import argparse
import json

from logger import query_logfire


def main():
    parser = argparse.ArgumentParser(description="Query Logfire records and emit JSONL.")
    parser.add_argument("--since", help="ISO-8601 timestamp filter (start_timestamp >= since).")
    parser.add_argument("--level", help="Numeric log level filter.")
    parser.add_argument("--message-like", help="Substring match for message.")
    parser.add_argument("--trace-id", help="Filter by trace_id.")
    parser.add_argument("--span-id", help="Filter by span_id.")
    parser.add_argument(
        "--columns",
        help="Comma-separated column list.",
        default=None,
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    rows = query_logfire(
        jsonl=True,
        columns=args.columns,
        limit=args.limit,
        since=args.since,
        level=args.level,
        message_like=args.message_like,
        trace_id=args.trace_id,
        span_id=args.span_id,
    )
    for row in rows:
        print(json.dumps(row))


if __name__ == "__main__":
    main()
