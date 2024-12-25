from logger.logger import log_info, log_debug, log_warning, log_error, log_critical

def example_function(param1, param2, optional_param=None):
    correlation_id = "123e4567-e89b-12d3-a456-426614174000"
    log_info(correlation_id, "Info log from example_function", custom_key="custom_value")
    log_debug(correlation_id, "Debug log from example_function", custom_key="custom_value")
    log_warning(correlation_id, "Warning log from example_function", custom_key="custom_value")
    log_error(correlation_id, "Error log from example_function", custom_key="custom_value")
    log_critical(correlation_id, "Critical log from example_function", custom_key="custom_value")

example_function("value1", "value2", optional_param="optional_value")