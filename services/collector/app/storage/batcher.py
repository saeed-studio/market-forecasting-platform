# services/collector/app/storage/batcher.py

import time


class EventBatcher:
    """Single-symbol batcher (kept as is)"""

    def __init__(
        self,
        batch_size: int = 1000,
        flush_interval: int = 60,
    ) -> None:
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.events: list[dict] = []
        self.last_flush_time = time.time()

    def add(self, event: dict) -> None:
        self.events.append(event)

    def should_flush(self) -> bool:
        return len(self.events) >= self.batch_size

    def should_flush_by_time(self) -> bool:
        return time.time() - self.last_flush_time >= self.flush_interval

    def reset(self) -> None:
        self.events.clear()
        self.last_flush_time = time.time()


class MultiSymbolBatcher:
    """
    Manages multiple EventBatcher instances, one per symbol.

    This allows events for different symbols (BTCUSDT, ETHUSDT, etc.)
    to be batched independently, preventing mixing of symbols in the same file.
    """

    def __init__(
        self,
        batch_size: int = 1000,
        flush_interval: int = 60,
    ) -> None:
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._batchers: dict[str, EventBatcher] = {}

    def _get_batcher(self, symbol: str) -> EventBatcher:
        """Get or create a batcher for the given symbol."""
        if symbol not in self._batchers:
            self._batchers[symbol] = EventBatcher(
                batch_size=self.batch_size,
                flush_interval=self.flush_interval,
            )
        return self._batchers[symbol]

    def add(self, symbol: str, event: dict) -> None:
        """Add an event to the appropriate symbol's batch."""
        batcher = self._get_batcher(symbol)
        batcher.add(event)

    def should_flush(self, symbol: str) -> bool:
        """Check if the symbol's batch should be flushed (size-based)."""
        if symbol not in self._batchers:
            return False
        return self._batchers[symbol].should_flush()

    def should_flush_by_time(self, symbol: str) -> bool:
        """Check if the symbol's batch should be flushed (time-based)."""
        if symbol not in self._batchers:
            return False
        return self._batchers[symbol].should_flush_by_time()

    def get_events(self, symbol: str) -> list[dict]:
        """Get all events in the symbol's batch."""
        if symbol not in self._batchers:
            return []
        return self._batchers[symbol].events

    def reset(self, symbol: str) -> None:
        """Reset only the specified symbol's batch."""
        if symbol in self._batchers:
            self._batchers[symbol].reset()

    def reset_all(self) -> None:
        """Reset all symbol batches (useful for testing or shutdown)."""
        for batcher in self._batchers.values():
            batcher.reset()

    def get_symbols_with_batches(self) -> list[str]:
        """Get all symbols that have active batches (non-empty)."""
        return [symbol for symbol, batcher in self._batchers.items() if batcher.events]

    def get_all_pending_events_count(self) -> int:
        """Get total pending events across all symbols."""
        return sum(len(batcher.events) for batcher in self._batchers.values())
