# services/collector/app/schemas/trade.py

# define a dataclass for trade events received from the Binance WebSocket stream.
# This class will be used to parse and store trade data efficiently.
from dataclasses import dataclass


@dataclass(slots=True)  # Use slots to reduce memory usage and improve performance
class TradeEvent:
    symbol: str
    trade_id: int

    event_time: int
    trade_time: int

    price: float
    quantity: float

    is_buyer_maker: bool

    from dataclasses import dataclass
