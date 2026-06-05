import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from typing import Dict, List
from shared.schemas.base import BaseEvent
from .generic_partitioner import GenericPartitioner


class GenericStorageWriter:
    """
    Writes ANY BaseEvent to Parquet.
    No stream-specific logic.
    """

    def __init__(self, partitioner: GenericPartitioner):
        self.partitioner = partitioner
        self._writers: Dict[str, pq.ParquetWriter] = {}  # partition_key -> writer
        self._current_files: Dict[str, Path] = {}

    def write_batch(self, events: List[BaseEvent]) -> None:
        if not events:
            return

        # Group events by partition key
        groups: Dict[str, List[BaseEvent]] = {}
        for event in events:
            key = self.partitioner.get_partition_key(event)

            # setdefault : Retrieves the value of a key if it is present in the dictionary.
            #              If not, it inserts the key with a specified value (in this case, an empty list) and returns that value.
            groups.setdefault(key, []).append(event)

        for key, batch_events in groups.items():
            self._write_partition(key, batch_events)

    def _write_partition(self, partition_key: str, events: List[BaseEvent]) -> None:
        # Get or create writer for this partition
        if partition_key not in self._writers:
            path = self.partitioner.get_partition_path(events[0])
            path.mkdir(parents=True, exist_ok=True)
            file_path = path / "data.parquet"

            # Infer schema from first event (all events in partition share schema)
            df = pd.DataFrame([e.to_dict() for e in events[:1]])
            table = pa.Table.from_pandas(df, preserve_index=False)  # index is timestamp
            self._writers[partition_key] = pq.ParquetWriter(
                str(file_path), schema=table.schema, compression="snappy"
            )
            self._current_files[partition_key] = file_path

        # Write batch
        df = pd.DataFrame([e.to_dict() for e in events])
        table = pa.Table.from_pandas(df, preserve_index=False)
        self._writers[partition_key].write_table(table)

    def close_all(self):
        for writer in self._writers.values():
            writer.close()
        self._writers.clear()
