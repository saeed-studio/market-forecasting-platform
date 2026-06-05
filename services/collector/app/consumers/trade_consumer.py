# services/collector/app/consumers/trade_consumer.py

from services.collector.app.consumers.base import BaseConsumer
from services.collector.app.schemas.trade import TradeEvent

from services.collector.app.consumers.trade_validator import (
    TradeValidator,
)
from shared.logging.config import get_logger
from typing import Optional

logger = get_logger(__name__)


class TradeConsumer(BaseConsumer):
    async def consume(self, payload: dict) -> Optional[TradeEvent]:
        try:
            if payload.get("e") != "trade":
                return None

            TradeValidator.validate(payload)

            event_time = payload["E"]
            symbol = payload["s"]
            trade_id = payload["t"]
            price = float(payload["p"])
            quantity = float(payload["q"])
            trade_time = payload["T"]
            is_buyer_maker = payload["m"]

            # Deterministic event_id
            event_id = f"{symbol}_{trade_id}"

            return TradeEvent(
                event_id=event_id,
                symbol=symbol,
                exchange="binance",
                event_time=event_time,
                schema_version=1,
                trade_id=trade_id,
                trade_time=trade_time,
                price=price,
                quantity=quantity,
                is_buyer_maker=is_buyer_maker,
            )
        except Exception as e:
            logger.error(f"Failed to parse trade: {e}, payload={payload}")
            return None
