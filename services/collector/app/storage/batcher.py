# services/collector/app/storage/batcher.py

import time


class EventBatcher:
    def __init__(
        self,
        batch_size: int = 1000,
        flush_interval: int = 30,
    ) -> None:

        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self.events: list[dict] = []

        self.last_flush_time = time.time()

    def add(self, event: dict) -> None:
        self.events.append(event)

    def should_flush(self) -> bool:

        if len(self.events) >= self.batch_size:
            return True

        if time.time() - self.last_flush_time >= self.flush_interval:
            return True

        return False

    def reset(self) -> None:
        self.events.clear()
        self.last_flush_time = time.time()
