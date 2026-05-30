class CollectorError(Exception):
    """Base exception for collector-related failures."""


class NetworkError(CollectorError):
    """Network connectivity failure."""


class StaleConnectionError(CollectorError):
    """No messages received within stale threshold."""


class PayloadError(CollectorError):
    """Invalid payload received from stream."""
