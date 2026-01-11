import json
import os
import sys

from logger.logfire_read import query_logfire


def main():
    try:
        parsed = query_logfire()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    jsonl = os.getenv("LOGFIRE_READ_JSONL", "false").strip().lower() in {"1", "true", "yes", "on"}
    if jsonl and isinstance(parsed, list):
        for row in parsed:
            print(json.dumps(row))
        return

    print(json.dumps(parsed, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
