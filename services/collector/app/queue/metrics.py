# services/collector/app/queue/metrics.py

from dataclasses import dataclass


@dataclass(slots=True)
class QueueMetrics:
    events_in: int = 0
    events_out: int = 0
    peak_size: int = 0

    def increment_in(self) -> None:
        self.events_in += 1

    def increment_out(self) -> None:
        self.events_out += 1

    def update_peak_size(self, size: int) -> None:
        if size > self.peak_size:
            self.peak_size = size
