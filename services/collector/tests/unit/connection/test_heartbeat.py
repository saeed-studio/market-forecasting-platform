# services/collector/tests/unit/connection/test_heartbeat.py

from services.collector.app.connection.heartbeat import HeartbeatMonitor


def test_not_stale_after_heartbeat(monkeypatch):
    monitor = HeartbeatMonitor(stale_threshold=30)

    monkeypatch.setattr(
        "services.collector.app.connection.heartbeat.time.time", lambda: 100
    )

    monitor.beat()

    monkeypatch.setattr(
        "services.collector.app.connection.heartbeat.time.time", lambda: 110
    )

    assert monitor.is_stale() is False


def test_stale_connection(monkeypatch):
    monitor = HeartbeatMonitor(stale_threshold=30)

    monkeypatch.setattr(
        "services.collector.app.connection.heartbeat.time.time", lambda: 100
    )

    monitor.beat()

    monkeypatch.setattr(
        "services.collector.app.connection.heartbeat.time.time", lambda: 131
    )

    assert monitor.is_stale() is True


def test_beat_updates_timestamp(monkeypatch):
    monitor = HeartbeatMonitor()

    monkeypatch.setattr(
        "services.collector.app.connection.heartbeat.time.time", lambda: 500
    )

    monitor.beat()

    assert monitor.last_message_ts == 500
