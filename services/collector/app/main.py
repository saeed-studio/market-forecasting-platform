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

from services.collector.app.storage.rotator import (
    FileRotator,
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

    batcher = EventBatcher(
        batch_size=1000,
        flush_interval=30,
    )

    rotator = FileRotator(
        max_rows_per_file=100000,
    )

    writer = StorageWriter(
        base_path=("data/raw/trades/BTCUSDT"),
        rotator=rotator,
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

    connection = ConnectionManager(stream_url=BINANCE_TRADES_STREAM)

    async for message in connection.listen():
        await collector.process_message(message)


if __name__ == "__main__":
    asyncio.run(main())
