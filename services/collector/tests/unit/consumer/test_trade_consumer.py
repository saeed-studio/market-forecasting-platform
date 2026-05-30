# services/collector/tests/unit/consumer/test_trade_consumer.py

import pytest

from services.collector.app.consumers.trade_consumer import (
    TradeConsumer,
)

from services.collector.app.connection.exceptions import (
    PayloadError,
)


@pytest.fixture  # This fixture provides a valid trade payload for testing the TradeConsumer.
def valid_trade_payload():
    return {
        "e": "trade",
        "E": 1700000000000,
        "s": "BTCUSDT",
        "t": 12345,
        "p": "65000.50",
        "q": "0.010",
        "T": 1700000000001,
        "m": True,
    }


# fixture makes valid_trade_payload to returned value of function valid_trade_payload,
# so we can use it directly in test function without calling it.
def test_consume_valid_trade(valid_trade_payload):

    consumer = TradeConsumer()

    trade = consumer.consume(valid_trade_payload)

    assert trade.symbol == "BTCUSDT"
    assert trade.trade_id == 12345
    assert trade.price == 65000.50
    assert trade.quantity == 0.010


def test_missing_required_field(valid_trade_payload):

    consumer = TradeConsumer()

    valid_trade_payload.pop("p")

    with pytest.raises(PayloadError):
        consumer.consume(valid_trade_payload)


def test_negative_price(valid_trade_payload):

    consumer = TradeConsumer()

    valid_trade_payload["p"] = "-100"

    with pytest.raises(PayloadError):
        consumer.consume(valid_trade_payload)


def test_negative_quantity(valid_trade_payload):

    consumer = TradeConsumer()

    valid_trade_payload["q"] = "-1"

    with pytest.raises(PayloadError):
        consumer.consume(valid_trade_payload)
