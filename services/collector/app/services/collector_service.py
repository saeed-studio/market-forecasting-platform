# services/collector/app/services/collector_service.py


from services.collector.app.consumers.trade_consumer import (
    TradeConsumer,
)

from services.collector.app.validation.pipeline import (
    ValidationPipeline,
)

from services.collector.app.queue.event_queue import (
    EventQueue,
)


class CollectorService:
    def __init__(
        self,
        queue: EventQueue,
    ) -> None:

        self.queue = queue

        self.consumer = TradeConsumer()

        self.validator = ValidationPipeline()

    async def process_message(
        self,
        raw_message: str,
    ) -> None:

        payload = raw_message

        trade_event = self.consumer.consume(payload)

        if trade_event is not None:
            validated_event = self.validator.validate(trade_event)
            await self.queue.put(validated_event)
        # If trade_event is None, nothing gets put in the queue (lost as desired)
