# services/collector/app/validation/trade_validator.py

from services.collector.app.connection.exceptions import PayloadError

# binance payload fields:
# s: symbol
# t: trade id
# E: event time
# T: trade time
# p: price
# q: quantity
# m: is the buyer the market maker?

REQUIRED_FIELDS = {
    "s",
    "t",
    "E",
    "T",
    "p",
    "q",
    "m",
}


class TradeValidator:
    @staticmethod
    def validate(payload: dict) -> None:

        missing_fields = REQUIRED_FIELDS - payload.keys()

        if missing_fields:
            raise PayloadError(f"Missing required fields: {missing_fields}")

        # these will be checked in validation pipeline, but we can check them here as well to fail fast
        price = float(payload["p"])
        quantity = float(payload["q"])

        if price <= 0:
            raise PayloadError(f"Invalid price: {price}")

        if quantity <= 0:
            raise PayloadError(f"Invalid quantity: {quantity}")
