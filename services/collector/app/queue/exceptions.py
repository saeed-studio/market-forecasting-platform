# services/collector/app/queue/exceptions.py


class QueueFullError(Exception):
    """Queue reached maximum capacity."""
