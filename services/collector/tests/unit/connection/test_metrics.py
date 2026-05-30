# service/collector/tests/unit/connection/test_metrics.py

from services.collector.app.connection.metrics import ConnectionMetrics


def test_increment_messages():
    metrics = ConnectionMetrics()

    metrics.increment_messages()
    metrics.increment_messages()

    assert metrics.messages_received == 2


def test_increment_reconnects():
    metrics = ConnectionMetrics()

    metrics.increment_reconnects()

    assert metrics.reconnect_count == 1


def test_increment_timeouts():
    metrics = ConnectionMetrics()

    metrics.increment_timeouts()

    assert metrics.timeout_count == 1


def test_increment_stale_events():
    metrics = ConnectionMetrics()

    metrics.increment_stale_events()

    assert metrics.stale_events == 1


def test_uptime_property():
    metrics = ConnectionMetrics()

    uptime = metrics.uptime_seconds

    assert uptime >= 0
