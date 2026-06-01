# services/collector/app/main.py

import asyncio

from services.collector.app.connection.manager import (
    ConnectionManager,
)

from services.collector.app.core.config import BINANCE_TRADES_STREAM
from services.collector.app.queue.event_queue import (
    EventQueue,
)

from services.collector.app.storage.batcher import (
    EventBatcher,
)

from services.collector.app.storage.partitioner import (
    Partitioner,
)

from services.collector.app.storage.writer import (
    StorageWriter,
)

from services.collector.app.services.storage_consumer import (
    StorageConsumer,
)

from services.collector.app.services.collector_service import (
    CollectorService,
)


async def main():

    queue = EventQueue(maxsize=10000)

    partitioner = Partitioner(
        base_path="data/raw",
        stream_type="trades",
    )

    writer = StorageWriter(
        partitioner=partitioner,
    )

    batcher = EventBatcher(
        batch_size=1000,
        flush_interval=60,
    )

    collector = CollectorService(
        queue=queue,
    )

    storage_consumer = StorageConsumer(
        queue=queue,
        batcher=batcher,
        writer=writer,
    )

    asyncio.create_task(storage_consumer.run())
    asyncio.create_task(storage_consumer.periodic_flush())

    connection = ConnectionManager(stream_url=BINANCE_TRADES_STREAM)

    try:
        async for message in connection.listen():
            await collector.process_message(message)
    finally:
        await storage_consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
