import logging
import structlog
import sys
import inspect


# Logging levels:
# INFO: Confirmation that things are working as expected.
# DEBUG: Detailed information, typically of interest only when diagnosing problems.
# WARNING: An indication that something unexpected happened, or indicative of some problem in the near future.
# ERROR: Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL: A very serious error, indicating that the program itself may be unable to continue running.
LOGGING_LEVEL = logging.DEBUG

def add_caller_info(logger, method_name, event_dict):
    """
    Adds caller module, function name, and kwargs to the event dictionary.
    """
    frame = sys._getframe(5)  # Go five frames up to get the caller (example_function)
    event_dict['caller_module'] = frame.f_globals['__name__']
    event_dict['caller_function'] = frame.f_code.co_name

    # Capture function arguments
    try:
        args, _, _, values = inspect.getargvalues(frame)
        kwargs = {arg: values[arg] for arg in args}
        event_dict['function_kwargs'] = kwargs
    except Exception:
        event_dict['function_kwargs'] = "Unable to extract kwargs"

    return event_dict

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        add_caller_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(LOGGING_LEVEL),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def log_info(correlation_id, message, **params):
    logger.bind(correlation_id=correlation_id, **params).info(message)

def log_debug(correlation_id, message, **params):
    logger.bind(correlation_id=correlation_id, **params).debug(message)

def log_warning(correlation_id, message, **params):
    logger.bind(correlation_id=correlation_id, **params).warning(message)

def log_error(correlation_id, message, **params):
    logger.bind(correlation_id=correlation_id, **params).error(message)

def log_critical(correlation_id, message, **params):
    logger.bind(correlation_id=correlation_id, **params).critical(message)