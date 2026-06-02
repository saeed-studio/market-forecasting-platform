# services/collector/app/schemas/kline.py

from dataclasses import dataclass


@dataclass(slots=True)
class KlineEvent:
    symbol: str

    interval: str

    open_time: int
    close_time: int

    open_price: float
    high_price: float
    low_price: float
    close_price: float

    volume: float
    quote_volume: float

    trade_count: int

    taker_buy_volume: float

    is_closed: bool

    event_time: int
