# services/collector/app/services/storage_consumer.py
from services.collector.app.queue.event_queue import EventQueue
from services.collector.app.storage.batcher import EventBatcher
from services.collector.app.storage.serializer import EventSerializer
from services.collector.app.storage.writer import StorageWriter


class StorageConsumer:
    def __init__(
        self,
        queue: EventQueue,
        batcher: EventBatcher,
        writer: StorageWriter,
    ) -> None:

        self.queue = queue
        self.batcher = batcher
        self.writer = writer

    async def run(self) -> None:

        while True:
            event = await self.queue.get()

            serialized = EventSerializer.serialize(event)

            self.batcher.add(serialized)

            if self.batcher.should_flush():
                self.writer.flush(self.batcher.events)

                self.batcher.reset()

            self.queue.task_done()
