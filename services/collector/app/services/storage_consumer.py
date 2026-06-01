# services/collector/app/services/storage_consumer.py

import asyncio

from services.collector.app.queue.event_queue import (
    EventQueue,
)

from services.collector.app.storage.batcher import (
    EventBatcher,
)

from services.collector.app.storage.writer import (
    StorageWriter,
)

from services.collector.app.storage.serializer import (
    EventSerializer,
)


class StorageConsumer:
    """
    Consumes events from a queue, batches them, and writes them to storage.

    The StorageConsumer acts as the bridge between the event queue and the
    storage layer. It continuously pulls events from the queue, serializes them,
    adds them to a batch, and flushes the batch to disk when either the batch
    size threshold is reached or a time interval has passed.

    The consumer runs two concurrent tasks:
        1. Main event consumption loop (run method)
        2. Periodic time-based flush loop (periodic_flush method)

    This design ensures that events are written efficiently in batches rather
    than individually, reducing I/O overhead while maintaining timely persistence.
    """

    def __init__(
        self,
        queue: EventQueue,
        batcher: EventBatcher,
        writer: StorageWriter,
    ) -> None:
        """
        Initialize the StorageConsumer with queue, batcher, and writer.

        Args:
            queue: EventQueue instance that provides async get() and task_done()
                   methods for consuming events.
            batcher: EventBatcher instance that accumulates events until a
                     flush threshold is reached (size or time-based).
            writer: StorageWriter instance that handles the actual writing of
                    batched events to disk (e.g., Parquet files).
        """

        self.queue = queue

        self.batcher = batcher

        self.writer = writer

        self.running = True

    async def run(self) -> None:
        """
        Main event consumption loop.

        Continuously fetches events from the queue, serializes each event,
        adds it to the batcher, and checks if a flush is needed based on
        batch size. Runs until `self.running` is set to False.

        The method calls `queue.task_done()` after processing each event
        to signal that the event has been successfully consumed and batched.
        """

        while self.running:
            event = await self.queue.get()

            serialized = EventSerializer.serialize(event)

            self.batcher.add(serialized)

            if self.batcher.should_flush():
                await self.flush()

            self.queue.task_done()

    async def periodic_flush(
        self,
    ) -> None:
        """
        Periodic time-based flush loop.

        Runs concurrently with the main consumption loop. Wakes up every
        5 seconds and triggers a flush if there are events in the batch and
        the time threshold has been exceeded.

        This ensures that events are persisted even when batch size thresholds
        are never reached (e.g., during low-traffic periods).
        """

        while self.running:
            await asyncio.sleep(5)

            if self.batcher.events and self.batcher.should_flush_by_time():
                await self.flush()

    async def flush(
        self,
    ) -> None:
        """
        Flush the current batch of events to storage.

        Extracts the symbol from the first event in the batch (assuming all
        events in a batch share the same symbol), calls the writer's flush
        method with the symbol and events, then resets the batcher.

        If there are no events in the batch, the method returns immediately
        without performing any write operation.
        """
        if not self.batcher.events:
            return

        symbol = self.batcher.events[0]["symbol"]

        self.writer.flush(
            symbol=symbol,
            events=self.batcher.events,
        )

        self.batcher.reset()

    async def stop(self) -> None:

        self.running = False

        await self.flush()

        self.writer.close()
