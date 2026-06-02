# services/collector/app/consumers/kline_consumer.py

from services.collector.app.schemas.kline import (
    KlineEvent,
)

from services.collector.app.consumers.kline_validator import (
    KlineValidator,
)


class KlineConsumer:
    def consume(
        self,
        payload: dict,
    ) -> KlineEvent | None:

        KlineValidator.validate(payload)

        k = payload["k"]

        if not k["x"]:
            return None

        return KlineEvent(
            symbol=payload["s"],
            interval=k["i"],
            open_time=k["t"],
            close_time=k["T"],
            open_price=float(k["o"]),
            high_price=float(k["h"]),
            low_price=float(k["l"]),
            close_price=float(k["c"]),
            volume=float(k["v"]),
            quote_volume=float(k["q"]),
            trade_count=int(k["n"]),
            taker_buy_volume=float(k["V"]),
            is_closed=k["x"],
            event_time=payload["E"],
        )
