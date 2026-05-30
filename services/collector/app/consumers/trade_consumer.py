# services/collector/app/consumers/trade_consumer.py

from services.collector.app.schemas.trade import TradeEvent

from services.collector.app.consumers.trade_validator import (
    TradeValidator,
)


class TradeConsumer:
    def consume(self, payload: dict) -> TradeEvent:

        TradeValidator.validate(payload)

        return TradeEvent(
            symbol=payload["s"],
            trade_id=payload["t"],
            event_time=payload["E"],
            trade_time=payload["T"],
            price=float(payload["p"]),
            quantity=float(payload["q"]),
            is_buyer_maker=payload["m"],
        )
