# services/collector/app/storage/writer.py

from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from services.collector.app.storage.metrics import StorageMetrics
from services.collector.app.storage.exceptions import FlushError
from services.collector.app.storage.partitioner import Partitioner


class StorageWriter:
    """
    Writes batched trade events to Parquet files with partition rotation.

    The StorageWriter manages the low-level writing of event batches to disk
    using PyArrow's ParquetWriter for efficient streaming writes. It maintains
    a single open Parquet file per partition, appending new events as they
    arrive until a partition change triggers a rotation.

    The writer uses a partitioner to determine the current partition path based
    on the event's symbol and timestamp. When the partition changes (e.g., a
    new day), the writer closes the current Parquet file and opens a new one
    in the new partition directory.

    This design prevents file overwrites by always appending to the same
    partition file (`trades.parquet`) within a partition directory, and creating
    a new file when the partition key changes.
    """

    def __init__(
        self,
        partitioner: Partitioner,
    ) -> None:
        """
        Initialize the StorageWriter with a partitioner.

        Args:
            partitioner: Partitioner instance that determines the partition
                         path and key for a given event (typically based on
                         symbol and date).

        The writer starts with no active partition or ParquetWriter. The first
        flush call will trigger partition rotation to open the initial file.
        """
        self.partitioner = partitioner

        self.metrics = StorageMetrics()

        self.current_partition: str | None = None

        self.parquet_writer: pq.ParquetWriter | None = None

        self.current_file: Path | None = None

    def flush(
        self,
        symbol: str,
        events: list[dict],
    ) -> None:
        """
        Write a batch of events to the current partition's Parquet file.

        The method determines the current partition for the given symbol,
        rotates to a new partition if necessary, then appends the events
        to the open ParquetWriter.

        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT') used for partition lookup.
            events: List of event dictionaries to write. Each dictionary
                    should have consistent schema across all events.

        Raises:
            FlushError: If any error occurs during the write operation,
                        including partition rotation failures or write errors.
                        The error is wrapped with FlushError for consistent
                        error handling upstream.

         Notes:
            - If events is empty, the method returns immediately.
            - Events are converted to a PyArrow Table before writing for
              efficient serialization.
            - Metrics are updated for successful writes (events count and
              flush count) or failures (failure count).
        """
        if not events:
            return

        try:
            partition_key, partition_path = self.partitioner.current_partition(
                symbol=symbol
            )

            if self.current_partition != partition_key:
                self._rotate_partition(
                    partition_key,
                    partition_path,
                    events,
                )

            table = pa.Table.from_pandas(
                pd.DataFrame(events),
                preserve_index=False,
            )

            self.parquet_writer.write_table(table)

            self.metrics.increment_events(len(events))

            self.metrics.increment_flushes()

        except Exception as exc:
            self.metrics.increment_failures()

            raise FlushError(str(exc)) from exc

    def _rotate_partition(
        self,
        partition_key: str,
        partition_path: Path,
        sample_events: list[dict],
    ) -> None:
        """
        Close the current Parquet file and open a new one for a different partition.

        This method is called internally when the partition key changes (e.g.,
        moving from one day to the next). It closes any open ParquetWriter,
        updates the current partition tracking, and creates a new ParquetWriter
        at the new partition path.

        The schema is inferred from a sample of events (first batch of the new
        partition) to ensure the Parquet file schema matches the incoming data.

        Args:
            partition_key: Unique identifier for the new partition
                           (e.g., 'BTCUSDT_2024-01-15').
            partition_path: Filesystem path where the partition directory
                            should be created and where 'trades.parquet'
                            will be written.
            sample_events: Sample events from the first batch of the new
                           partition used to infer the Parquet schema.
        The partition directory is created automatically by the partitioner.
        The Parquet file is always named 'trades.parquet' within the partition
        directory, allowing all events for that partition to accumulate in a
        single file.
        """
        self.close()

        self.current_partition = partition_key

        self.current_file = partition_path / "trades.parquet"

        schema = pa.Table.from_pandas(
            pd.DataFrame(sample_events),
            preserve_index=False,
        ).schema

        self.parquet_writer = pq.ParquetWriter(
            str(self.current_file),
            schema=schema,
            compression="snappy",
        )

        self.metrics.increment_files()

    def close(self) -> None:
        """
        Close the current ParquetWriter if one is open.

        This method finalizes the current Parquet file, ensuring all buffers
        are flushed and the file is properly closed. It should be called
        when the consumer is shutting down to prevent data loss.

        After closing, the writer is reset to None, and subsequent flush
        calls will trigger a new partition rotation (reopening a file).

        The method is safe to call multiple times; if no writer is open,
        it does nothing.
        """
        if self.parquet_writer:
            self.parquet_writer.close()

            self.parquet_writer = None
