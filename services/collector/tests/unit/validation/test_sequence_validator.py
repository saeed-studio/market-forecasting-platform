# services/collector/tests/unit/validation/test_sequence_validator.py

import pytest

from services.collector.app.schemas.trade import TradeEvent

from services.collector.app.validation.validators.sequence_validator import (
    SequenceValidator,
)

from services.collector.app.validation.exceptions import (
    OutOfOrderEventError,
)


def test_out_of_order_event():

    validator = SequenceValidator()

    validator.validate(
        TradeEvent(
            "BTCUSDT",
            1,
            1000,
            1000,
            1,
            1,
            True,
        )
    )

    with pytest.raises(OutOfOrderEventError):
        validator.validate(
            TradeEvent(
                "BTCUSDT",
                2,
                999,
                999,
                1,
                1,
                True,
            )
        )
