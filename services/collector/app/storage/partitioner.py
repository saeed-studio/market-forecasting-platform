# services/collector/app/storage/partitioner.py

from datetime import datetime, timezone
from pathlib import Path


class Partitioner:
    def __init__(
        self,
        base_path: str,
        stream_type: str,
    ) -> None:

        self.base_path = Path(base_path)
        self.stream_type = stream_type

    def current_partition(
        self,
        symbol: str,
    ) -> tuple[str, Path]:

        now = datetime.now(timezone.utc)

        partition_key = f"{now.strftime('%Y-%m-%d')}_{now.strftime('%H')}"

        partition_path = (
            self.base_path
            / self.stream_type
            / f"symbol={symbol}"
            / f"date={now.strftime('%Y-%m-%d')}"
            / f"hour={now.strftime('%H')}"
        )

        partition_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return partition_key, partition_path
