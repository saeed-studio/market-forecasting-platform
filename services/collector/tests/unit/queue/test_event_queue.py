# services/collector/tests/unit/queue/test_event_queue.py

import pytest

from services.collector.app.queue.event_queue import EventQueue
from services.collector.app.queue.exceptions import QueueFullError


async def test_put_increases_size():

    queue = EventQueue()

    await queue.put("event")

    assert queue.size() == 1


async def test_get_returns_same_object():

    queue = EventQueue()

    payload = {"symbol": "BTCUSDT"}

    await queue.put(payload)

    result = await queue.get()

    assert result == payload


async def test_queue_full_raises():

    queue = EventQueue(maxsize=1)

    await queue.put("first")

    with pytest.raises(QueueFullError):
        await queue.put("second")


async def test_metrics_update():

    queue = EventQueue()

    await queue.put("event")

    assert queue.metrics.events_in == 1

    await queue.get()

    assert queue.metrics.events_out == 1


async def test_peak_size_tracking():

    queue = EventQueue()

    await queue.put(1)
    await queue.put(2)
    await queue.put(3)

    assert queue.metrics.peak_size == 3
