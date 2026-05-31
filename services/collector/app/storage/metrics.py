# services/collector/app/storage/metrics.py

from dataclasses import dataclass


@dataclass(slots=True)
class StorageMetrics:
    events_written: int = 0
    files_created: int = 0
    flush_count: int = 0
    failed_writes: int = 0

    def increment_events(self, count: int) -> None:
        self.events_written += count

    def increment_flushes(self) -> None:
        self.flush_count += 1

    def increment_files(self) -> None:
        self.files_created += 1

    def increment_failures(self) -> None:
        self.failed_writes += 1
