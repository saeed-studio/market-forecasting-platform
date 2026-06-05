# services/collector/app/main.py

import asyncio
import sys
from pathlib import Path

from shared.logging.config import get_logger
from services.collector.app.core.config import (
    DEFAULT_SYMBOL,
    BINANCE_TRADES_STREAM,
    BINANCE_KLINE_1M_STREAM,
    CHECKPOINT_DB_PATH,
)
from services.collector.app.core.stream_definition import StreamDefinition
from services.collector.app.orchestrator.orchestrator import Orchestrator
from services.collector.app.queue.event_queue import EventQueue
from services.collector.app.services.storage_consumer import StorageConsumer
from services.collector.app.checkpoint.store import CollectorCheckpointStore
from services.collector.app.consumers.trade_consumer import TradeConsumer
from services.collector.app.consumers.kline_consumer import KlineConsumer
from services.collector.app.consumers.funding_consumer import FundingConsumer
from services.collector.app.consumers.oi_consumer import OpenInterestConsumer
from services.collector.app.connection.manager import ConnectionManager

logger = get_logger("main")


# Factory functions – each returns a fresh async iterator
def trades_event_factory(symbol: str):
    async def _iterate():
        url = BINANCE_TRADES_STREAM.format(symbol=symbol.lower())
        cm = ConnectionManager(url)
        consumer = TradeConsumer()
        try:
            async for raw_msg in cm.listen():
                event = await consumer.consume(raw_msg)
                if event:
                    yield event
        finally:
            await cm.close()

    return _iterate


def klines_event_factory(symbol: str):
    async def _iterate():
        url = BINANCE_KLINE_1M_STREAM.format(symbol=symbol.lower())
        cm = ConnectionManager(url)
        consumer = KlineConsumer()
        try:
            async for raw_msg in cm.listen():
                event = await consumer.consume(raw_msg)
                if event:
                    yield event
        finally:
            await cm.close()

    return _iterate


def funding_factory(symbol: str):
    """Creates a new FundingConsumer each time – allows restart recovery."""

    async def _iterate():
        consumer = FundingConsumer(symbol)

        try:
            async for event in consumer.stream():
                yield event

        finally:
            await consumer.close()

    return _iterate


def oi_factory(symbol: str):
    async def _iterate():
        consumer = OpenInterestConsumer(symbol)

        try:
            async for event in consumer.stream():
                yield event

        finally:
            await consumer.close()

    return _iterate


async def main():
    symbol = DEFAULT_SYMBOL
    logger.info(f"Starting multi-stream collector for {symbol}")

    # Ensure directories exist
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/checkpoints.db").parent.mkdir(parents=True, exist_ok=True)

    # Shared components
    event_queue = EventQueue(maxsize=10000)
    checkpoint_store = CollectorCheckpointStore(db_path=CHECKPOINT_DB_PATH)
    await checkpoint_store.init()

    storage_consumer = StorageConsumer(
        event_queue=event_queue,
        base_path="data/raw",  # Only the root path, no stream type
        checkpoint_store=checkpoint_store,
        batch_size=1000,
        flush_interval=5.0,
    )
    storage_task = asyncio.create_task(storage_consumer.run())

    # Register streams with factories (no pre‑created instances)
    orchestrator = Orchestrator()

    orchestrator.register(
        StreamDefinition("binance", symbol, "trades"), trades_event_factory(symbol)
    )

    orchestrator.register(
        StreamDefinition("binance", symbol, "klines"), klines_event_factory(symbol)
    )

    orchestrator.register(
        StreamDefinition("binance", symbol, "funding"), funding_factory(symbol)
    )

    orchestrator.register(StreamDefinition("binance", symbol, "oi"), oi_factory(symbol))

    try:
        await orchestrator.start_all(event_queue)
    except asyncio.CancelledError:
        logger.info("Shutdown signal received")
    finally:
        await storage_consumer.stop()
        storage_task.cancel()
        await asyncio.gather(storage_task, return_exceptions=True)
        await checkpoint_store.close()
        # No consumer instances to close – leaks accepted for Sprint 1


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
        sys.exit(0)
