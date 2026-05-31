# services/collector/tests/unit/queue/test_metrics.py

from services.collector.app.queue.metrics import QueueMetrics


def test_increment_in():

    metrics = QueueMetrics()

    metrics.increment_in()

    assert metrics.events_in == 1


def test_increment_out():

    metrics = QueueMetrics()

    metrics.increment_out()

    assert metrics.events_out == 1


def test_peak_size_updates():

    metrics = QueueMetrics()

    metrics.update_peak_size(5)

    assert metrics.peak_size == 5

    metrics.update_peak_size(3)

    assert metrics.peak_size == 5

    metrics.update_peak_size(10)

    assert metrics.peak_size == 10
