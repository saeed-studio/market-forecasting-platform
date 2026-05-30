# services/collector/tests/unit/connection/test_retry.py

from services.collector.app.connection.retry import ExponentialBackoff


def test_initial_delay_without_jitter():
    backoff = ExponentialBackoff(
        base_delay=1,
        max_delay=30,
        jitter=False,
    )

    assert backoff.next_delay() == 1


def test_exponential_growth():
    backoff = ExponentialBackoff(
        base_delay=1,
        max_delay=30,
        jitter=False,
    )

    delays = [
        backoff.next_delay(),
        backoff.next_delay(),
        backoff.next_delay(),
        backoff.next_delay(),
    ]

    assert delays == [1, 2, 4, 8]


def test_max_delay_cap():
    backoff = ExponentialBackoff(
        base_delay=10,
        max_delay=30,
        jitter=False,
    )

    delays = [
        backoff.next_delay(),
        backoff.next_delay(),
        backoff.next_delay(),
    ]

    assert delays == [10, 20, 30]


def test_reset():
    backoff = ExponentialBackoff(
        jitter=False,
    )

    backoff.next_delay()
    backoff.next_delay()

    assert backoff.attempt == 2

    backoff.reset()

    assert backoff.attempt == 0


def test_jitter_stays_within_expected_range():
    backoff = ExponentialBackoff(
        base_delay=10,
        max_delay=30,
        jitter=True,
    )

    delay = backoff.next_delay()

    assert 8 <= delay <= 12
