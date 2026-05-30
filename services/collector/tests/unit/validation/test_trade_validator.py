# services/collector/tests/unit/validation/test_trade_validator.py

import pytest

from services.collector.app.schemas.trade import TradeEvent

from services.collector.app.validation.validators.trade_validator import (
    TradeValidator,
)

from services.collector.app.validation.exceptions import (
    InvalidPriceError,
)


def test_negative_price():

    validator = TradeValidator()

    event = TradeEvent(
        symbol="BTCUSDT",
        trade_id=1,
        event_time=1,
        trade_time=1,
        price=-1,
        quantity=1,
        is_buyer_maker=True,
    )

    with pytest.raises(InvalidPriceError):
        validator.validate(event)
