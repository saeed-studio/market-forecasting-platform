# services/collector/app/storage/writer.py

from pathlib import Path

import pandas as pd

from services.collector.app.storage.metrics import StorageMetrics
from services.collector.app.storage.rotator import FileRotator
from services.collector.app.storage.exceptions import FlushError


class StorageWriter:
    def __init__(
        self,
        base_path: str,
        rotator: FileRotator,
    ) -> None:

        self.base_path = Path(base_path)

        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.rotator = rotator

        self.metrics = StorageMetrics()

    def flush(
        self,
        events: list[dict],
    ) -> None:

        if not events:
            return

        try:
            if self.rotator.should_rotate(len(events)):
                self.rotator.rotate()

            file_path = self.base_path / f"trades_{self.rotator.file_index}.parquet"

            df = pd.DataFrame(events)

            df.to_parquet(
                file_path,
                compression="snappy",  # fast compressor average 2-3 comp ratio
                index=False,
            )

            self.rotator.update_row_count(len(events))

            self.metrics.increment_events(len(events))

            self.metrics.increment_flushes()

        except Exception as exc:
            self.metrics.increment_failures()

            raise FlushError(str(exc)) from exc
