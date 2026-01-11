# Logger

This project provides a structured logging setup using `structlog` and Logfire in Python. It is designed to capture structured logs from containerized applications, making it easy to import this module to satisfy logging as a cross-cutting concern while attaching logs to traces.

## Observability Guidance (Logfire + Structlog)

We follow the "Perfect Logger" pattern where Logfire orchestrates tracing and Structlog emits structured events that attach to the active span.

### Structured Logging Rules

- Log with fields, not string concatenation: `log.info("user_purchased_item", user_id=..., item_id=...)`.
- Use `structlog.contextvars.bind_contextvars(...)` to attach request or job IDs to all logs.
- Keep INFO for business milestones, DEBUG for high-volume details, ERROR for failures, FATAL for unrecoverable issues.

### Tracing and Callsite Context

- Logfire wraps Structlog, so logs appear as span events.
- Callsite metadata is enabled via `CallsiteParameterAdder` (filename, function, line).
- Use `logfire.span(...)` for logical units of work to group logs.

### Environment Routing

Set environment variables to control routing:

- `LOGFIRE_SEND_TO_LOGFIRE=false` (default): logs remain on stdout and local collectors.
- `LOGFIRE_SEND_TO_LOGFIRE=true`: logs/traces sent to Logfire cloud (requires `LOGFIRE_TOKEN`).
- `LOGFIRE_SERVICE_NAME`: optional override for service name (default `logger`).

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/logger.git
    cd logger
    ```

2. Create a virtual environment and activate it:
    ```sh
    uv venv
    source .venv/bin/activate
    ```

3. Install the required dependencies:
    ```sh
    uv pip install -r requirements.txt
    ```

## Usage

### Configuration

The logging level can be configured globally by setting the `LOGGING_LEVEL` variable at the top of the `logger.py` file. The available logging levels are:

- `logging.DEBUG`: Detailed information, typically of interest only when diagnosing problems.
- `logging.INFO`: Confirmation that things are working as expected.
- `logging.WARNING`: An indication that something unexpected happened, or indicative of some problem in the near future.
- `logging.ERROR`: Due to a more serious problem, the software has not been able to perform some function.
- `logging.CRITICAL` (FATAL): A very serious error, indicating that the program itself may be unable to continue running.

### Logfire Environment

Logfire is enabled via environment variables so you can route data safely across environments:

- `LOGFIRE_SEND_TO_LOGFIRE`: Set to `true` to send traces/logs to Logfire cloud. Default is `false`.
- `LOGFIRE_TOKEN`: Required when `LOGFIRE_SEND_TO_LOGFIRE=true`.
- `LOGFIRE_SERVICE_NAME`: Optional override for the Logfire service name (defaults to `logger`).

### Logging Functions

The following logging functions are available:

- `log_info(correlation_id, message, **params)`: Logs an informational message.
- `log_debug(correlation_id, message, **params)`: Logs a debug message.
- `log_warning(correlation_id, message, **params)`: Logs a warning message.
- `log_error(correlation_id, message, **params)`: Logs an error message.
- `log_critical(correlation_id, message, **params)`: Logs a fatal message.

Each function requires a `correlation_id` and a `message`. Additional parameters can be passed as keyword arguments.

### Install as a Module (uv / uvx)

Install locally with `uv`:

```sh
uv pip install -e ..
```

Run the demo via `uvx`:

```sh
uvx --from .. logger-demo
```

### Example

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
### Example Output

Assuming the logging level is set to logging.INFO, the output will be:

```json
{
  "event": "Info log from example_function",
  "log_level": "info",
  "timestamp": "2025-01-01T00:00:00Z",
  "filename": "example.py",
  "func_name": "example_function",
  "lineno": 12,
  "request_id": "req-9f7c2a",
  "user_id": "user-42",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_key": "custom_value"
}
{
  "event": "Warning log from example_function",
  "log_level": "warning",
  "timestamp": "2025-01-01T00:00:00Z",
  "filename": "example.py",
  "func_name": "example_function",
  "lineno": 12,
  "request_id": "req-9f7c2a",
  "user_id": "user-42",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_key": "custom_value"
}
{
  "event": "Error log from example_function",
  "log_level": "error",
  "timestamp": "2025-01-01T00:00:00Z",
  "filename": "example.py",
  "func_name": "example_function",
  "lineno": 12,
  "request_id": "req-9f7c2a",
  "user_id": "user-42",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_key": "custom_value"
}
{
  "event": "Critical log from example_function",
  "log_level": "fatal",
  "timestamp": "2025-01-01T00:00:00Z",
  "filename": "example.py",
  "func_name": "example_function",
  "lineno": 12,
  "request_id": "req-9f7c2a",
  "user_id": "user-42",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_key": "custom_value"
}
```
### Explanation

With the logging level set to logging.INFO, the output includes logs at the INFO, WARNING, ERROR, and FATAL levels. The DEBUG log is not included because it is below the INFO level. Each log entry includes the following information:

- **event**: The log message.
- **log_level**: The level of the log (info, warning, error, fatal).
- **timestamp**: ISO-8601 timestamp in UTC.
- **filename/func_name/lineno**: Callsite metadata for fast code navigation.
- **request_id/user_id**: Request-scoped context variables bound via `structlog.contextvars`.
- **correlation_id**: A unique identifier for correlating logs.
- **custom_key**: Any additional custom parameters passed to the log function.
  
## Intended Use

This logging setup is intended to capture structured logs from containerized applications. By importing this module, you can easily satisfy logging as a cross-cutting concern in your application, ensuring consistent and structured log output across different parts of your system.

### Testing

To run the observability demo and see logs with spans/context, execute:

```python
python ../example_compose/test_logger.py
```

If you want to run the full containerized demo with the log processor, use:

```sh
../scripts/compose-up.sh
```

### License

This project is licensed under the MIT License.
