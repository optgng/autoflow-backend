"""
Custom application exceptions.
"""
from typing import Any


class AutoFlowException(Exception):
    """Base exception for AutoFlow application."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        detail: Any = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class AuthenticationError(AutoFlowException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed", detail: Any = None) -> None:
        super().__init__(message=message, status_code=401, detail=detail)


class AuthorizationError(AutoFlowException):
    """User is not authorized to perform this action."""

    def __init__(self, message: str = "Not authorized", detail: Any = None) -> None:
        super().__init__(message=message, status_code=403, detail=detail)


class NotFoundError(AutoFlowException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", detail: Any = None) -> None:
        super().__init__(message=message, status_code=404, detail=detail)


class ValidationError(AutoFlowException):
    """Validation error."""

    def __init__(self, message: str = "Validation error", detail: Any = None) -> None:
        super().__init__(message=message, status_code=422, detail=detail)


class ConflictError(AutoFlowException):
    """Resource conflict (e.g., duplicate entry)."""

    def __init__(self, message: str = "Resource conflict", detail: Any = None) -> None:
        super().__init__(message=message, status_code=409, detail=detail)
