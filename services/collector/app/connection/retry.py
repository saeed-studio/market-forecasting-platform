# services/collector/app/connection/retry.py
"""Exponential backoff retry strategy for connection management."""

import random


class ExponentialBackoff:
    """Calculate exponentially increasing delays for retry attempts.

    Implements an exponential backoff strategy with optional jitter to avoid
    thundering herd problems. Each retry attempt increases the delay
    exponentially up to a maximum threshold.
    """

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        jitter: bool = True,
    ):
        """Initialize the exponential backoff calculator.

        Args:
            base_delay (float): Initial delay in seconds before first retry.
                Defaults to 1.0.
            max_delay (float): Maximum delay cap in seconds. Defaults to 30.0.
            jitter (bool): Whether to add randomness (±20%) to delays.
                Defaults to True.
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.attempt = 0

    def next_delay(self) -> float:
        """Calculate the next retry delay.

        Computes delay as base_delay * 2^attempt, capped at max_delay.
        If jitter is enabled, multiplies by a random factor between 0.8 and 1.2.
        Increments the attempt counter.

        Returns:
            float: The delay in seconds to wait before the next retry attempt.
        """
        delay = min(
            self.base_delay * (2**self.attempt),
            self.max_delay,
        )

        if self.jitter:
            delay = delay * random.uniform(0.8, 1.2)

        self.attempt += 1

        return delay

    def reset(self) -> None:
        """Reset the attempt counter to zero.

        Call this method when a connection is successfully established
        to reset the backoff strategy for future retry attempts.
        """
        self.attempt = 0
