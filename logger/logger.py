import logging
import os

import logfire
import structlog


# Logging levels:
# INFO: Confirmation that things are working as expected.
# DEBUG: Detailed information, typically of interest only when diagnosing problems.
# WARNING: An indication that something unexpected happened, or indicative of some problem in the near future.
# ERROR: Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL: A very serious error, indicating that the program itself may be unable to continue running.
LOGGING_LEVEL = logging.DEBUG
SERVICE_NAME = os.getenv("LOGFIRE_SERVICE_NAME", "logger")

def _env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

def _normalize_logfire_level(logger, method_name, event_dict):
    if event_dict.get("level") == "critical":
        event_dict["level"] = "fatal"
    return event_dict

logfire.configure(
    service_name=SERVICE_NAME,
    send_to_logfire=_env_flag("LOGFIRE_SEND_TO_LOGFIRE", default=False),
)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        _normalize_logfire_level,
        logfire.StructlogProcessor(),
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
    logger.bind(correlation_id=correlation_id, **params).fatal(message)
