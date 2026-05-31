# sercices/collector/app/storage/serializer.py

from dataclasses import asdict

from services.collector.app.schemas.trade import TradeEvent


class EventSerializer:
    @staticmethod
    def serialize(
        event: TradeEvent,
    ) -> dict:

        return asdict(event)
