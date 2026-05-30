# services/collector/app/validation/exceptions.py


class ValidationError(Exception):
    """Base validation exception."""


class DuplicateEventError(ValidationError):
    """Duplicate event detected."""


class OutOfOrderEventError(ValidationError):
    """Out-of-order event detected."""


class MissingTimestampError(ValidationError):
    """Required timestamp missing."""


class InvalidPriceError(ValidationError):
    """Invalid price detected."""


class InvalidQuantityError(ValidationError):
    """Invalid quantity detected."""
