# services/collector/app/services/collector_service.py

from services.collector.app.connection.manager import ConnectionManager

from services.collector.app.queue.event_queue import (
    EventQueue,
)


class CollectorService:
    def __init__(
        self,
        *,
        stream_url: str,
        consumer,
        queue: EventQueue,
    ):

        self.stream_url = stream_url
        self.consumer = consumer
        self.queue = queue

        self.connection_manager = ConnectionManager(stream_url)

    async def handle_message(
        self,
        payload: dict,
    ) -> None:

        event = self.consumer.consume(payload)

        if event is not None:
            await self.queue.put(event)
        # If trade_event is None, nothing gets put in the queue (lost as desired)

    async def run(self):

        async for payload in self.connection_manager.listen():
            await self.handle_message(payload)
