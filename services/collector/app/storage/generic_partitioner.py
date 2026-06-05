# services/collector/app/storage/generic_partitioner.py

from datetime import datetime, timezone
from pathlib import Path
from shared.schemas.base import BaseEvent


class GenericPartitioner:
    """Partitions any event by symbol, event_type, date, hour."""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def get_partition_path(self, event: BaseEvent) -> Path:
        now = datetime.fromtimestamp(
            event.event_time / 1000, tz=timezone.utc
        )  # Convert ms timestamp to datetime
        return (
            self.base_path
            / event.get_event_type()  # "trades", "klines", etc.
            / f"symbol={event.symbol}"
            / f"date={now.strftime('%Y-%m-%d')}"
            / f"hour={now.strftime('%H')}"
        )

    def get_partition_key(self, event: BaseEvent) -> str:
        now = datetime.fromtimestamp(event.event_time / 1000, tz=timezone.utc)
        return f"{event.symbol}:{event.get_event_type()}:{now.strftime('%Y-%m-%d-%H')}"
