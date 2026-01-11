import time

import logfire
import structlog

from .logger import log_critical, log_debug, log_error, log_info, log_warning


def _simulate_workload(correlation_id):
    with logfire.span("simulate_workload", task="demo", stage="start"):
        log_debug(
            correlation_id,
            "Preparing inputs",
            input_count=3,
        )
        time.sleep(0.1)

        try:
            log_info(correlation_id, "Processing item", item_id="item-001", amount=19.99)
            raise ValueError("Simulated parsing failure")
        except Exception as exc:
            log_warning(correlation_id, "Retrying after failure", reason=str(exc), attempt=1)
            log_error(
                correlation_id,
                "Processing failed",
                error=str(exc),
                exc_info=True,
                item_id="item-001",
            )

        log_info(correlation_id, "Processing complete", processed=1, failed=1)


def main():
    correlation_id = "123e4567-e89b-12d3-a456-426614174000"
    structlog.contextvars.bind_contextvars(
        request_id="req-9f7c2a",
        user_id="user-42",
    )

    with logfire.span("demo_run", component="logger-demo"):
        log_info(correlation_id, "Demo run starting", env="local")
        _simulate_workload(correlation_id)
        log_critical(correlation_id, "Demo run finished")


if __name__ == "__main__":
    main()
