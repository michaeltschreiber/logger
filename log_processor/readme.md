# Log Processor

This script, `log_processor.py`, is designed to process logs from Docker Compose services, parse them, and store them in an SQLite database. It distinguishes between structured logs (from services using `structlog`) and unstructured logs, storing them in separate tables.

## Features

- **Structured Logging**: Captures and stores structured logs with detailed fields.
- **Unstructured Logging**: Captures and stores unstructured logs.
- **Timestamp Management**: Keeps track of the last processed timestamp to ensure logs are not duplicated.
- **Custom Fields**: Dynamically captures any additional fields in the logs that are not predefined.

## Prerequisites

- Python 3.6 or higher
- Docker and Docker Compose
- Required Python packages (listed in `requirements.txt`)

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/logger.git
    cd logger
    ```

2. **Create a virtual environment and activate it**:
    ```sh
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux
    ```

3. **Install the required dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Ensure Docker and Docker Compose are running**:
    Make sure your Docker services are up and running.

2. **Run the log processor**:
    ```sh
    python log_processor.py
    ```

## How It Works

### Database Setup

The script connects to an SQLite database (`logs.db`) and creates the following tables if they do not exist:

- **structured_logs**: Stores structured logs with fields such as `timestamp`, `service`, `log_level`, `message`, `correlation_id`, `caller_module`, `caller_function`, `function_kwargs`, and `custom_fields`.
- **unstructured_logs**: Stores unstructured logs with fields such as `timestamp`, `source`, and `log`.
- **timestamp**: Stores the last processed timestamp to avoid duplicate log entries.

### Log Processing

- **get_last_processed_timestamp()**: Retrieves the last processed timestamp from the `timestamp` table.
- **update_last_processed_timestamp(timestamp)**: Updates the `timestamp` table with the current timestamp after processing logs.
- **store_structured_log(log)**: Stores a structured log in the `structured_logs` table.
- **store_unstructured_log(log)**: Stores an unstructured log in the `unstructured_logs` table.
- **process_log(log, source)**: Processes a log line. If the log is in JSON format and contains the required fields (`event` and `level`), it is stored as a structured log. Otherwise, it is stored as an unstructured log.
- **tail_logs()**: Uses the `docker-compose logs -f` command to tail the logs from Docker Compose. It processes each log line and updates the last processed timestamp.

### Example

Here is an example of how the logs are processed and stored:

1. **Structured Log**:
    ```json
    {
        "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
        "custom_key": "custom_value",
        "event": "Critical log from example_function",
        "level": "critical",
        "caller_module": "__main__",
        "caller_function": "example_function",
        "function_kwargs": {
            "param1": "value1",
            "param2": "value2",
            "optional_param": "optional_value"
        }
    }
    ```

    This log will be stored in the `structured_logs` table with the appropriate fields.

2. **Unstructured Log**:
    Any log that does not match the structured log format will be stored in the `unstructured_logs` table.

## License

This project is licensed under the MIT License.
