# PTM Fusion Personas Alignment

This repo demonstrates structured logging with Structlog + Logfire and a Docker Compose example. The personas below are mapped to how they relate to this repository so contributors can pick the right guidance quickly.

## Repo Standards

- Use `uv` for Python dependency management and installs.

## Observability Use Cases

- Correlation-aware API logging with request_id/user_id contextvars.
- Background job spans with structured metadata.
- Pipeline/ETL logs routed to stdout and collectors.
- Local debugging with no data egress.
- Production routing via OTel collectors with the same log shape.

## Mode Examples

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

Azure Monitor (Application Insights):

```sh
export LOGFIRE_SEND_TO_LOGFIRE=false
export OTEL_EXPORTER_OTLP_ENDPOINT=https://<region>.in.applicationinsights.azure.com
export OTEL_EXPORTER_OTLP_HEADERS="api-key=<your_connection_string_or_ikey>"
python example_compose/test_logger.py
```

Aspire Dashboard standalone (local sensitive):

```sh
docker run --rm -d -p 18888:18888 -p 4317:18889 --name aspire-dashboard mcr.microsoft.com/dotnet/aspire-dashboard:latest
export LOGFIRE_SEND_TO_LOGFIRE=false
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
python example_compose/test_logger.py
```

## Primary (Directly Used Here)

- observability-engineer: defines the Logfire + Structlog "Perfect Logger" setup and environment routing.
- backend-engineer: Python logging patterns, structured events, and callsite context.

## Supporting (Adjacent to the Demo)

- devops-engineer: containerized logging and deployment/ops concerns.
- aspire-devops-engineer: observability-first deployment patterns and distributed telemetry.
- fullstack-engineer: logging patterns in fullstack services.
- data-engineer: downstream log processing and data observability.
- sqlite-engineer: SQLite usage in the log processor.

## Not Demonstrated in This Repo

- frontend-engineer: React SPA patterns.
- designer: UI/UX and design systems.
- ai-engineer: PydanticAI agent systems.
- postgres-engineer: Postgres-specific patterns.
- mssql-engineer: SQL Server/CDC patterns.
- aspnet-csharp-engineer: ASP.NET APIs and logging.
- lovable-cloud-supabase-engineer: Supabase/Lovable Cloud integration.
- powerplatform-to-lovable-engineer: Power Apps migration.
- product-owner: PRDs/SDDs and Event Storming.
- copilot-skill-builder: agent skill creation.
