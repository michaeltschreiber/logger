# Logger Project

This project provides a structured logging setup using the `structlog` library in Python. It is designed to capture structured logs from containerized applications, making it easy to import this module to satisfy logging as a cross-cutting concern. The project includes an example Docker Compose setup to demonstrate the logging and log processing capabilities.

## Project Structure

- **/example_compose**: Contains an example Docker Compose setup that demonstrates the use of the logging and log processing scripts. It includes a service that generates logs using `structlog` and a log processor that captures and stores these logs in an SQLite database.
- **/log_processor**: Contains the `log_processor.py` script, which processes logs from Docker Compose services, parses them, and stores them in an SQLite database. It distinguishes between structured logs (from services using `structlog`) and unstructured logs, storing them in separate tables.
- **/logger**: Contains the `logger.py` script, which provides a structured logging setup using the `structlog` library in Python. It includes functions for logging messages at different levels (INFO, DEBUG, WARNING, ERROR, CRITICAL) and captures additional context such as the caller module and function name, as well as custom key-value pairs and the argument values passed to the logging function.

## Prerequisites

- Python 3.6 or higher
- Docker and Docker Compose

## Installation

1. **Clone the repository**

    ```sh
    git clone https://github.com/yourusername/logger.git
    cd logger
    ```

2. **Create a virtual environment and activate it**

    ```sh
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux
    ```

3. **Install the required dependencies**

    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Example Compose

1. **Navigate to the example_compose directory**

    ```sh
    cd example_compose
    ```

2. **Build and run the Docker Compose services**

    ```sh
    docker-compose up --build
    ```

3. **Run the log processor**

    The `log_processor.py` script is meant to be run from the Docker host and is located in the `../log_processor` folder relative to this directory. Navigate to the [log_processor](http://_vscodecontentref_/1) folder and run the script:

    ```sh
    cd ../log_processor
    python log_processor.py
    ```

### Logger

The `logger.py` script provides functions for logging messages at different levels (INFO, DEBUG, WARNING, ERROR, CRITICAL). Each function requires a `correlation_id` and a `message`. Additional parameters can be passed as keyword arguments.

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
