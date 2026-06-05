# services/collector/app/services/storage_consumer.py

import asyncio
from typing import Dict, List
from collections import defaultdict

from shared.logging.config import get_logger
from shared.schemas.base import BaseEvent
from ..queue.event_queue import EventQueue
from ..storage.writer import StorageWriter
from ..storage.partitioner import Partitioner
from ..checkpoint.store import CollectorCheckpointStore


logger = get_logger(__name__)


class StorageConsumer:
    def __init__(
        self,
        event_queue: EventQueue,
        base_path: str,
        checkpoint_store: CollectorCheckpointStore,
        batch_size: int = 1000,
        flush_interval: float = 5.0,
    ):
        self._queue = event_queue
        self._base_path = base_path
        self._checkpoint_store = checkpoint_store
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._batch: List[BaseEvent] = []
        self._running = True
        self._checkpoint_cache: Dict[
            str, int
        ] = {}  # stream_key -> last checkpoint time
        self._batch_lock = (
            asyncio.Lock()
        )  # protects batch and prevents concurrent flushes
        self._writers: Dict[str, StorageWriter] = {}  # event_type -> StorageWriter

    def _get_writer(self, event_type: str) -> StorageWriter:
        """Get or create a StorageWriter for the given event_type."""
        if event_type not in self._writers:
            partitioner = Partitioner(base_path=self._base_path, stream_type=event_type)
            self._writers[event_type] = StorageWriter(partitioner=partitioner)
            logger.info(f"Created new storage writer for event_type={event_type}")
        return self._writers[event_type]

    async def run(self):
        logger.info("StorageConsumer: consumption loop started")
        flush_task = asyncio.create_task(self._flush_loop())
        try:
            while self._running:
                event = await self._queue.get()
                if await self._is_already_processed(event):
                    logger.debug(
                        f"Skipping old event: {event.stream_key} checkpoint={event.get_checkpoint_int()}"
                    )
                    self._queue.task_done()
                    continue

                # Append and check size inside lock
                should_flush = False
                async with self._batch_lock:
                    self._batch.append(event)
                    if len(self._batch) >= self._batch_size:
                        should_flush = True

                if should_flush:
                    await self._flush()

                self._queue.task_done()
        finally:
            flush_task.cancel()
            await asyncio.gather(
                flush_task,
                return_exceptions=True,
            )

    async def _flush_loop(self):
        while self._running:
            await asyncio.sleep(self._flush_interval)
            # Quick check outside lock – fine for triggering
            if self._batch:
                await self._flush()

    async def _flush(self):
        # Swap batch under lock
        async with self._batch_lock:
            if not self._batch:
                return
            batch_to_flush = self._batch
            self._batch = []
            per_stream_max: Dict[str, int] = defaultdict(int)

        # Process the swapped batch outside the lock
        # Process outside lock
        try:
            by_symbol_and_type: Dict[tuple, List[dict]] = defaultdict(list)
            for event in batch_to_flush:
                event_dict = event.__dict__
                key = (event.symbol, event.event_type)
                by_symbol_and_type[key].append(event_dict)

                sk = event.stream_key
                cp_int = event.get_checkpoint_int()
                if cp_int > per_stream_max[sk]:
                    per_stream_max[sk] = cp_int

            # Write to storage using the appropriate writer per event_type
            for (symbol, event_type), events in by_symbol_and_type.items():
                writer = self._get_writer(event_type)
                writer.flush(symbol=symbol, events=events)

            # Batch update checkpoints
            checkpoints_to_update = {
                stream_key: str(max_cp) for stream_key, max_cp in per_stream_max.items()
            }
            if checkpoints_to_update:
                await self._checkpoint_store.set_checkpoints_multi(
                    checkpoints_to_update
                )
                for sk, cp in checkpoints_to_update.items():
                    self._checkpoint_cache[sk] = int(cp)

            logger.info(
                f"Flushed {len(batch_to_flush)} events, checkpoints updated: {dict(per_stream_max)}"
            )
        except Exception as e:
            logger.exception(f"Flush failed: {e}")
            raise

    async def _is_already_processed(self, event: BaseEvent) -> bool:
        stream_key = event.stream_key
        if stream_key not in self._checkpoint_cache:
            cp_str = await self._checkpoint_store.get_checkpoint(stream_key)
            if cp_str:
                try:
                    self._checkpoint_cache[stream_key] = int(cp_str)
                except ValueError:
                    logger.warning(
                        f"Invalid checkpoint value {cp_str} for {stream_key}, resetting to 0"
                    )
                    self._checkpoint_cache[stream_key] = 0
            else:
                self._checkpoint_cache[stream_key] = 0
        last_cp = self._checkpoint_cache[stream_key]
        return event.get_checkpoint_int() <= last_cp

    async def stop(self):
        self._running = False
