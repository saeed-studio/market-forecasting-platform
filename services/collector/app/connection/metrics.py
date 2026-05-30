# services/collector/app/connection/metrics.py
"""Data class for tracking connection metrics."""

from dataclasses import dataclass, field
from time import time


@dataclass
class ConnectionMetrics:
    messages_received: int = 0
    reconnect_count: int = 0
    timeout_count: int = 0
    stale_events: int = 0

    started_at: float = field(default_factory=time)

    def increment_messages(self) -> None:
        self.messages_received += 1

    def increment_reconnects(self) -> None:
        self.reconnect_count += 1

    def increment_timeouts(self) -> None:
        self.timeout_count += 1

    def increment_stale_events(self) -> None:
        self.stale_events += 1

    @property
    def uptime_seconds(self) -> float:
        return time() - self.started_at
