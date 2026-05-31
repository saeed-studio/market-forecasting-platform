# services/collector/app/consumers/trade_consumer.py

from services.collector.app.schemas.trade import TradeEvent

from services.collector.app.consumers.trade_validator import (
    TradeValidator,
)


class TradeConsumer:
    def consume(self, payload: dict) -> TradeEvent | None:

        price_str = payload.get("p", "0")
        quantity_str = payload.get("q", "0")

        # Convert to float for comparison
        try:
            price = float(price_str)
            quantity = float(quantity_str)
        except (ValueError, TypeError):
            return None  # Invalid format, skip

        # Skip zero-price or zero-quantity events to prevent crash on N/A execution types
        if price <= 0 or quantity <= 0:
            print("non trade type payload", payload)
            return None

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
