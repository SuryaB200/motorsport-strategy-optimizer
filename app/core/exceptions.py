"""Domain exception classes for the Motorsport Strategy Optimizer."""

from typing import Any, Optional


class MotorsportException(Exception):
    """Base exception for all domain-specific errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ConfigurationValidationError(MotorsportException):
    """Raised when race or model configuration fails validation rules."""

    pass


class IllegalStrategyError(MotorsportException):
    """Raised when a candidate pit strategy violates constraints or race bounds."""

    pass


class SimulationError(MotorsportException):
    """Raised when a numerical or logical simulation failure occurs."""

    pass


class ResourceNotFoundError(MotorsportException):
    """Raised when a requested resource (race, run, result) is not found in the database."""

    pass


class OptimizationBudgetExceededError(MotorsportException):
    """Raised when an optimization budget or resource limit is exceeded."""

    pass
