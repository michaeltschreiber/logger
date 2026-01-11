# Logger Project

This project provides a structured logging setup using `structlog` and Logfire in Python. It is designed to capture structured logs from containerized applications, making it easy to import this module to satisfy logging as a cross-cutting concern while attaching logs to traces. The project includes an example Docker Compose setup to demonstrate logging and log processing.

## Observability Showcase

This repo is a focused demo of "Perfect Logger" patterns:

- Logfire spans wrapping business work with structured Structlog events attached to traces.
- Context propagation via `structlog.contextvars.bind_contextvars(...)`.
- Callsite metadata (filename, function, line) via `CallsiteParameterAdder`.
- Error handling that captures exceptions while preserving structured fields.
- Environment-based routing for sensitive, dev, and production modes.

The demo script at `example_compose/test_logger.py` exercises spans, contextvars, error logging, and multiple log levels in one run.

## Use Cases

- API request logging with correlation IDs and request context.
- Background jobs with traceable spans and structured events.
- ETL or batch processing with rich per-record metadata.
- Containerized services forwarding stdout to a centralized pipeline.
- Local debugging with trace context preserved in logs.

## Project Structure

- **/example_compose**: Contains an example Docker Compose setup that demonstrates the use of the logging and log processing scripts. It includes a service that generates logs using `structlog` and a log processor that captures and stores these logs in an SQLite database.
- **/log_processor**: Contains the `log_processor.py` script, which processes logs from Docker Compose services, parses them, and stores them in an SQLite database. It distinguishes between structured logs (from services using `structlog`) and unstructured logs, storing them in separate tables.
- **/logger**: Contains the `logger.py` script, which provides a structured logging setup using `structlog` and Logfire in Python. It includes functions for logging messages at different levels (INFO, DEBUG, WARNING, ERROR, FATAL) and captures callsite context and custom key-value pairs.
- **/scripts**: Helper scripts to start/stop the Docker Compose demo with the correct env file.

## Observability Guidance (Logfire + Structlog)

We use the "Perfect Logger" pattern: Logfire orchestrates tracing and Structlog emits structured events that attach to the active span.

- Logfire wraps Structlog: log events become span events, while stdout remains a backup path.
- Always log with fields, not string formatting: `log.info("user_purchased_item", user_id=..., item_id=...)`.
- Use request-scoped context with `structlog.contextvars.bind_contextvars(...)` so all logs inherit identifiers.
- Callsite metadata is enabled via `CallsiteParameterAdder` for filename, function, and line number.

#### Environment Routing

Set these environment variables to route data safely:

- `LOGFIRE_SEND_TO_LOGFIRE=false` (default): logs stay local/stdout.
- `LOGFIRE_SEND_TO_LOGFIRE=true`: logs/traces sent to Logfire cloud (requires `LOGFIRE_TOKEN`).
- `LOGFIRE_SERVICE_NAME`: optional override for service name (default `logger`).

Recommended modes:

- Sensitive/local: keep `LOGFIRE_SEND_TO_LOGFIRE=false`, use local OTel collector if needed.
- Development: set `LOGFIRE_SEND_TO_LOGFIRE=true` with a write token.
- Production: keep `LOGFIRE_SEND_TO_LOGFIRE=false` and export via your OTel/Azure pipeline.

### Mode Examples

Load environment from `.env` before running locally:

```sh
set -a
. ./.env
set +a
```

Sensitive/local (stdout only):

```sh
export LOGFIRE_SEND_TO_LOGFIRE=false
python example_compose/test_logger.py
```

Development (Logfire cloud):

```sh
export LOGFIRE_SEND_TO_LOGFIRE=true
export LOGFIRE_TOKEN=your_write_token
python example_compose/test_logger.py
```

Production-style (external OTel pipeline):

```sh
export LOGFIRE_SEND_TO_LOGFIRE=false
export OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com:4317
python example_compose/test_logger.py
```

### Logfire Readback

Set a Logfire read URL and token, then run the fetch script:

```sh
export LOGFIRE_READ_URL="https://logfire-us.pydantic.dev/v1/query"
export LOGFIRE_READ_TOKEN=your_read_token
export LOGFIRE_READ_HEADER=Authorization
export LOGFIRE_READ_SCHEME=Bearer
export LOGFIRE_READ_COLUMNS="created_at,start_timestamp,message,level,trace_id,span_id,span_name,attributes_reduced,attributes,service_name,project_id"
export LOGFIRE_READ_LIMIT=20
export LOGFIRE_READ_LEVEL=error
export LOGFIRE_READ_MESSAGE_LIKE="Processing failed"
export LOGFIRE_READ_JSONL=true
python scripts/logfire-fetch.py
```

### Module Read API (JSONL)

Use the module function to retrieve query results as JSONL records:

```python
from logger import query_logfire

rows = query_logfire(jsonl=True)
for row in rows:
    print(row)
```

Optional filters:

- `LOGFIRE_READ_SINCE=2026-01-11T00:00:00Z`
- `LOGFIRE_READ_LEVEL=21`
- `LOGFIRE_READ_MESSAGE_LIKE="Processing failed"`
- `LOGFIRE_READ_TRACE_ID=<trace_id>`

Level mapping (Logfire numeric):

- `1` = `trace`
- `5` = `debug`
- `9` = `info`
- `13` = `warn`
- `17` = `error`
- `21` = `fatal`

### Agent Read Tool (JSONL)

Use a CLI-friendly helper for agents or scripts:

```sh
python scripts/logfire-read-agent.py --since 2026-01-11T00:00:00Z --message-like "Processing failed" --limit 10
```

### Azure Monitor (Application Insights) Example

Use the Azure Monitor OpenTelemetry distro and route OTLP to Azure:

```sh
export LOGFIRE_SEND_TO_LOGFIRE=false
export OTEL_EXPORTER_OTLP_ENDPOINT=https://<region>.in.applicationinsights.azure.com
export OTEL_EXPORTER_OTLP_HEADERS="api-key=<your_connection_string_or_ikey>"
python example_compose/test_logger.py
```

### Aspire Dashboard Standalone (Local Sensitive)

Run the Aspire dashboard locally and point OTLP to it:

```sh
docker run --rm -d -p 18888:18888 -p 4317:18889 --name aspire-dashboard mcr.microsoft.com/dotnet/aspire-dashboard:latest
export LOGFIRE_SEND_TO_LOGFIRE=false
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
python example_compose/test_logger.py
```

## PTM Fusion Personas

This repo aligns most closely with the observability and backend personas (Logfire + Structlog). Full persona alignment notes are documented in `agents.md`.

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose

## Quick Start (Local)

1. **Create a virtual environment and activate it**

    ```sh
    uv venv
    source .venv/bin/activate
    ```

2. **Install demo dependencies**

    ```sh
    uv pip install -r example_compose/requirements.txt
    ```

3. **Run the demo script**

    ```sh
    python example_compose/test_logger.py
    ```

## Usage

### Example Compose

Use the helper scripts to start/stop the demo:

```sh
./scripts/compose-up.sh
./scripts/compose-down.sh
```

To send traces to Logfire cloud, set `LOGFIRE_SEND_TO_LOGFIRE=true` and `LOGFIRE_TOKEN` in `.env` before running the scripts.

1. **Navigate to the example_compose directory**

    ```sh
    cd example_compose
    ```

2. **Build and run the Docker Compose services**

    ```sh
    docker compose up --build
    ```

3. **Run the log processor**

    The `log_processor.py` script is meant to be run from the Docker host and is located in the `../log_processor` folder relative to this directory:

    ```sh
    cd ../log_processor
    python log_processor.py
    ```

### Logger

The `logger.py` script provides functions for logging messages at different levels (INFO, DEBUG, WARNING, ERROR, FATAL). Each function requires a `correlation_id` and a `message`. Additional parameters can be passed as keyword arguments.

### Install as a Module (uv / uvx)

This repo is packaged as a Python module (`ptm-logger`) for clean imports and CLI usage.

Install locally with `uv`:

```sh
uv pip install -e .
```

Run the demo via `uvx`:

```sh
uvx --from . logger-demo
```

### Example: Structured Event

```python
from logger import log_info

correlation_id = "c3a2a5c9-8ef8-4e0d-9c6a-7b0f420a2b50"
log_info("user_login", user_id="user-42", org_id="org-9", correlation_id=correlation_id)
```

### Example: Request Context

```python
import structlog
from logger import log_error

structlog.contextvars.bind_contextvars(request_id="req-123", user_id="user-42")
log_error("order_failed", order_id="order-77", reason="card_declined", correlation_id="corr-777")
```

#### Logfire Environment

- `LOGFIRE_SEND_TO_LOGFIRE`: Set to `true` to send traces/logs to Logfire cloud. Default is `false`.
- `LOGFIRE_TOKEN`: Required when `LOGFIRE_SEND_TO_LOGFIRE=true`.
- `LOGFIRE_SERVICE_NAME`: Optional override for the Logfire service name (defaults to `logger`).

The helper scripts (`./scripts/compose-up.sh`) load these values from the repo `.env`.

#### Example

Here is an example of how to use the logging functions in your code:

```python
from logger import log_info, log_debug, log_warning, log_error, log_critical

def example_function(param1, param2, optional_param=None):
    correlation_id = "123e4567-e89b-12d3-a456-426614174000"
    log_info(correlation_id, "Info log from example_function", custom_key="custom_value")
    log_debug(correlation_id, "Debug log from example_function", custom_key="custom_value")
    log_warning(correlation_id, "Warning log from example_function", custom_key="custom_value")
    log_error(correlation_id, "Error log from example_function", custom_key="custom_value")
    log_critical(correlation_id, "Critical log from example_function", custom_key="custom_value")

example_function("value1", "value2", optional_param="optional_value")
```

## Log Processor

The log_processor.py script processes logs from Docker Compose services, parses them, and stores them in an SQLite database. It distinguishes between structured logs (from services using structlog) and unstructured logs, storing them in separate tables.

## License

This project is licensed under the MIT License.
