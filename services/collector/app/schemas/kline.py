# services/collector/app/schemas/kline.py

from dataclasses import dataclass
from typing import ClassVar
from shared.schemas.base import BaseEvent


@dataclass(frozen=True, kw_only=True)
class KlineEvent(BaseEvent):
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

    event_type: ClassVar[str] = "kline"

    @property
    def stream_key(self) -> str:
        """Include interval for per‑timeframe isolation."""
        return f"{self.exchange}:{self.symbol}:{self.event_type}:{self.interval}"

    def get_checkpoint_int(self) -> int:
        """Use close_time (monotonic) for ordering."""
        return self.close_time
