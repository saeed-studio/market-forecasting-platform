# services/collector/app/orchestrator/orchestrator.py

"""This module defines the Orchestrator class, which manages the lifecycle of data streams.
It allows registering multiple streams, starting them concurrently, and ensures that
events from all streams are sent"""

import asyncio
from shared.logging.config import get_logger
from typing import Callable, Dict, AsyncIterator

from ..core.stream_definition import StreamDefinition
from ..queue.event_queue import EventQueue

logger = get_logger(__name__)


class Orchestrator:
    """The Orchestrator class manages multiple data streams, ensuring they run concurrently and that
    events from all streams are sent to the event queue. It also handles stream failures by
    restarting them after a delay."""

    def __init__(self):
        self._stream_factories: Dict[str, Callable[[], AsyncIterator]] = {}
        self._restart_delay = 5.0  # seconds

    def register(
        self, stream_def: StreamDefinition, factory: Callable[[], AsyncIterator]
    ):
        """
        Register a stream with a factory function that returns a fresh async iterator.
        The factory is called on every restart attempt.
        """
        key = stream_def.key()
        if key in self._stream_factories:
            raise ValueError(f"Stream {key} already registered")
        self._stream_factories[key] = factory
        logger.info(f"Registered stream factory: {key}")

    async def start_all(self, event_queue: EventQueue):
        """Start all registered streams concurrently. If any stream crashes, it will be restarted after a delay."""
        tasks = []
        for key, factory in self._stream_factories.items():
            task = asyncio.create_task(
                self._run_stream_with_retry(key, factory, event_queue)
            )
            tasks.append(task)

        if not tasks:
            logger.warning("No streams registered")
            return

        # Gather with return_exceptions to prevent one crash from cancelling others
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Orchestrator task failed: {r}")

    async def _run_stream_with_retry(
        self, key: str, factory: Callable[[], AsyncIterator], event_queue: EventQueue
    ):
        """Run a single stream with infinite retries, recreating the iterator on failure."""
        while True:
            try:
                # Create a fresh iterator for each attempt
                event_iter = factory()
                await self._run_stream_once(key, event_iter, event_queue)
            except asyncio.CancelledError:
                logger.info(f"Stream {key} cancelled")
                break
            except Exception as e:
                logger.exception(
                    f"Stream {key} crashed: {e}. Restarting in {self._restart_delay}s"
                )
                await asyncio.sleep(self._restart_delay)
                # Loop continues, factory called again

    async def _run_stream_once(
        self, key: str, event_iter: AsyncIterator, event_queue: EventQueue
    ):
        logger.info(f"Stream {key} started")
        async for event in event_iter:
            await event_queue.put(event)
        logger.warning(f"Stream {key} ended (iterator exhausted)")
