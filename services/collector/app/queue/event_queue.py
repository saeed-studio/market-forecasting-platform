# services/collector/app/queue/event_queue.py

import asyncio
from typing import Any
from .metrics import QueueMetrics


class EventQueue:
    def __init__(
        self,
        maxsize: int = 10_000,
    ) -> None:

        self._queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)

        self.metrics = QueueMetrics()

    async def put(self, item: Any) -> None:
        # No explicit full check – asyncio.Queue blocks automatically
        # when using asyncio.Queue, it will block until space is available, so we don't need to raise an exception here.
        # if self._queue.full():
        #     raise QueueFullError("Event queue is full.")

        await self._queue.put(item)

        self.metrics.increment_in()

        self.metrics.update_peak_size(self._queue.qsize())

    async def get(self) -> Any:

        item = await self._queue.get()

        self.metrics.increment_out()

        return item

    def size(self) -> int:
        return self._queue.qsize()

    def is_empty(self) -> bool:
        return self._queue.empty()

    def is_full(self) -> bool:
        return self._queue.full()

    def task_done(self) -> None:
        self._queue.task_done()

    async def join(self) -> None:
        await self._queue.join()
