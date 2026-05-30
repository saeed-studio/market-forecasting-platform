# services/collector/app/validation/validators/trade_validator.py

from services.collector.app.validation.validators.base import (
    BaseValidator,
)

from services.collector.app.validation.exceptions import (
    InvalidPriceError,
    InvalidQuantityError,
)


class TradeValidator(BaseValidator):
    def validate(self, event) -> None:

        if event.price <= 0:
            raise InvalidPriceError(f"Invalid price: {event.price}")

        if event.quantity <= 0:
            raise InvalidQuantityError(f"Invalid quantity: {event.quantity}")
