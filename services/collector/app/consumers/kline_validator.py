# services/collector/app/consumers/kline_validator.py

from services.collector.app.connection.exceptions import (
    PayloadError,
)

REQUIRED_FIELDS = {
    "e",  # event type
    "E",  # event time
    "s",  # symbol
    "k",  # kline data
}


class KlineValidator:
    @staticmethod
    def validate(payload: dict) -> None:

        missing = REQUIRED_FIELDS - payload.keys()

        if missing:
            raise PayloadError(f"Missing required fields: {missing}")

        kline = payload["k"]

        required_kline_fields = {
            "t",  # open_time
            "T",  # close_time
            "i",  # interval
            "o",  # open_price
            "h",  # high_price
            "l",  # low_price
            "c",  # close_price
            "v",  # volume
            "q",  # quote_volume
            "n",  # trade_count
            "V",  # taker_buy_volume
            "x",  # is_closed
        }

        missing_kline = required_kline_fields - kline.keys()

        if missing_kline:
            raise PayloadError(f"Missing kline fields: {missing_kline}")
