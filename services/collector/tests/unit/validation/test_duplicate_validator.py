# services/collector/tests/unit/validation/test_duplicate_validator.py

import pytest

from services.collector.app.schemas.trade import TradeEvent

from services.collector.app.validation.validators.duplicate_validator import (
    DuplicateValidator,
)

from services.collector.app.validation.exceptions import (
    DuplicateEventError,
)


def test_duplicate_trade_id():

    validator = DuplicateValidator()

    event = TradeEvent(
        symbol="BTCUSDT",
        trade_id=100,
        event_time=1,
        trade_time=1,
        price=1,
        quantity=1,
        is_buyer_maker=True,
    )

    validator.validate(
        event
    )  # calling validate for the first time should pass without exceptions

    with pytest.raises(DuplicateEventError):
        validator.validate(
            event
        )  # second call with the same event should raise DuplicateEventError
