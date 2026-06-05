# services/collector/app/schemas/trade.py

# define a dataclass for trade events received from the Binance WebSocket stream.
# This class will be used to parse and store trade data efficiently.
from dataclasses import dataclass
from shared.schemas.base import BaseEvent
from typing import ClassVar


@dataclass(frozen=True, kw_only=True)
class TradeEvent(BaseEvent):
    """Trade event – same fields as original, plus BaseEvent fields."""

    trade_id: int
    trade_time: int
    price: float
    quantity: float
    is_buyer_maker: bool

    # Note: symbol, exchange, event_id, schema_version come from BaseEvent
    # To avoid duplication, we remove `event_time` from this dataclass field list
    # and rely on BaseEvent's `event_time`.

    event_type: ClassVar[str] = "trade"

    def get_checkpoint_int(self) -> int:
        """Use trade_id for precise recovery."""
        return self.trade_id

    def get_checkpoint_value(self) -> str:
        # Use trade_id for more precise recovery (overrides base)
        return f"{self.symbol}_{self.trade_id}"
