# services/collector/app/consumers/kline_consumer.py

from typing import Optional
from services.collector.app.schemas.kline import (
    KlineEvent,
)
from shared.logging.config import get_logger

from services.collector.app.consumers.kline_validator import (
    KlineValidator,
)

logger = get_logger(__name__)


class KlineConsumer:
    async def consume(
        self,
        payload: dict,
    ) -> Optional[KlineEvent]:

        KlineValidator.validate(payload)
        try:
            if payload.get("e") != "kline":
                return None
            k = payload["k"]
            if not k.get("x", False):
                return None
            symbol = k["s"]
            close_time = k["T"]
            event_id = f"{symbol}_{close_time}"  # deterministic

            return KlineEvent(
                event_id=event_id,
                symbol=symbol,
                exchange="binance",
                event_time=payload["E"],
                schema_version=1,
                interval=k["i"],
                open_time=k["t"],
                close_time=close_time,
                open_price=float(k["o"]),
                high_price=float(k["h"]),
                low_price=float(k["l"]),
                close_price=float(k["c"]),
                volume=float(k["v"]),
                quote_volume=float(k["q"]),
                trade_count=int(k["n"]),
                taker_buy_volume=float(k["V"]),
                is_closed=k["x"],
            )
        except Exception as e:
            logger.error(f"Failed to parse kline: {e}, payload={payload}")
            return None
