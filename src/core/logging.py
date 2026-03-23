"""Logging setup with PII redaction filter (SEC-11)."""
import logging
import structlog

SENSITIVE_FIELDS = {
    "password", "hashed_password", "access_token", "refresh_token",
    "token", "merchant", "account_number", "telegram_id",
    "auth_code", "card_number", "phone",
}


def redact_sensitive(logger, method, event_dict: dict) -> dict:
    """structlog processor: replace sensitive field values with ***REDACTED***."""
    for key in list(event_dict.keys()):
        if key.lower() in SENSITIVE_FIELDS:
            event_dict[key] = "***REDACTED***"
    return event_dict


def setup_logging() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            redact_sensitive,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    logging.basicConfig(level=logging.INFO)


def get_logger(name: str = __name__):
    return structlog.get_logger(name)
