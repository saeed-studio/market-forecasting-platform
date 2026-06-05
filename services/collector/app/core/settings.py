# services/collector/app/core/settings.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class StreamConfig:
    """Configuration for a single data stream."""

    name: str  # "trades", "klines_1m", "funding", "open_interest"
    enabled: bool = True
    websocket_url: Optional[str] = None  # None means REST-only
    rest_endpoint: Optional[str] = None
    interval_seconds: int = 60  # Polling interval for REST streams
    batch_size: int = 1000
    flush_interval_seconds: int = 60


@dataclass
class SymbolConfig:
    """Configuration for a trading symbol."""

    symbol: str  # "BTCUSDT", "ETHUSDT", etc.
    enabled: bool = True
    streams: Dict[str, StreamConfig] = field(default_factory=dict)


@dataclass
class CollectorSettings:
    """Root configuration for the collector service."""

    # Symbols to collect
    symbols: List[SymbolConfig] = field(
        default_factory=lambda: [
            SymbolConfig(symbol="BTCUSDT", enabled=True),
            # Add more symbols here as needed
        ]
    )

    # Global settings
    data_root: Path = Path("data/raw")
    max_queue_size: int = 10000
    stale_threshold_seconds: int = 30
    receive_timeout_seconds: int = 10

    # Backoff settings
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0

    # Backfill settings
    backfill_enabled: bool = True
    backfill_days_back: int = 7  # How many days to backfill on first run

    def get_enabled_symbols(self) -> List[str]:
        return [s.symbol for s in self.symbols if s.enabled]
