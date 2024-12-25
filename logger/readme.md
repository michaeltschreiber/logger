# Logger

This project provides a structured logging setup using the `structlog` library in Python. It is designed to capture structured logs from containerized applications, making it easy to import this module to satisfy logging as a cross-cutting concern.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/logger.git
    cd logger
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Configuration

The logging level can be configured globally by setting the `LOGGING_LEVEL` variable at the top of the [logger.py](http://_vscodecontentref_/0) file. The available logging levels are:

- `logging.DEBUG`: Detailed information, typically of interest only when diagnosing problems.
- `logging.INFO`: Confirmation that things are working as expected.
- `logging.WARNING`: An indication that something unexpected happened, or indicative of some problem in the near future.
- `logging.ERROR`: Due to a more serious problem, the software has not been able to perform some function.
- `logging.CRITICAL`: A very serious error, indicating that the program itself may be unable to continue running.

### Logging Functions

The following logging functions are available:

- `log_info(correlation_id, message, **params)`: Logs an informational message.
- `log_debug(correlation_id, message, **params)`: Logs a debug message.
- `log_warning(correlation_id, message, **params)`: Logs a warning message.
- `log_error(correlation_id, message, **params)`: Logs an error message.
- `log_critical(correlation_id, message, **params)`: Logs a critical message.

Each function requires a `correlation_id` and a `message`. Additional parameters can be passed as keyword arguments.

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
  "caller_module": "__main__",
  "caller_function": "example_function",
  "function_kwargs": {
    "param1": "value1",
    "param2": "value2",
    "optional_param": "optional_value"
  },
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_key": "custom_value"
}
{
  "event": "Warning log from example_function",
  "log_level": "warning",
  "caller_module": "__main__",
  "caller_function": "example_function",
  "function_kwargs": {
    "param1": "value1",
    "param2": "value2",
    "optional_param": "optional_value"
  },
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_key": "custom_value"
}
{
  "event": "Error log from example_function",
  "log_level": "error",
  "caller_module": "__main__",
  "caller_function": "example_function",
  "function_kwargs": {
    "param1": "value1",
    "param2": "value2",
    "optional_param": "optional_value"
  },
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_key": "custom_value"
}
{
  "event": "Critical log from example_function",
  "log_level": "critical",
  "caller_module": "__main__",
  "caller_function": "example_function",
  "function_kwargs": {
    "param1": "value1",
    "param2": "value2",
    "optional_param": "optional_value"
  },
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_key": "custom_value"
}
```
### Explanation

With the logging level set to logging.INFO, the output includes logs at the INFO, WARNING, ERROR, and CRITICAL levels. The DEBUG log is not included because it is below the INFO level. Each log entry includes the following information:

- **event**: The log message.
- **log_level**: The level of the log (info, warning, error, critical).
- **caller_module**: The module where the log was generated.
- **caller_function**: The function where the log was generated.
- **function_kwargs**: The arguments passed to the function where the log was generated.
- **correlation_id**: A unique identifier for correlating logs.
- **custom_key**: Any additional custom parameters passed to the log function.
  
## Intended Use

This logging setup is intended to capture structured logs from containerized applications. By importing this module, you can easily satisfy logging as a cross-cutting concern in your application, ensuring consistent and structured log output across different parts of your system.

### Intended Use

This logging setup is intended to capture structured logs from containerized applications. By importing this module, you can easily satisfy logging as a cross-cutting concern in your application, ensuring consistent and structured log output across different parts of your system.

### Testing

To run the example function and see the logs, execute the test_logger.py file:

```python
python test_logger.py
```

### License

This project is licensed under the MIT License.