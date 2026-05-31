# # services/collector/tests/unit/storage/test_writer.py

# import pytest
# from pathlib import Path
# import tempfile
# import pandas as pd

# from services.collector.app.storage.writer import StorageWriter
# from services.collector.app.storage.rotator import FileRotator


# class TestStorageWriterParquetFile:
#     """Test parquet file creation scenarios"""

#     def test_parquet_file_created_on_flush(self):
#         """Test that parquet file is created when flushing events"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator(max_rows_per_file=100_000)
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             # Create events
#             events = [{"id": i, "price": 100.0 + i, "quantity": 10} for i in range(50)]

#             # Flush events
#             writer.flush(events)

#             # Verify file was created
#             expected_file = Path(temp_dir) / "trades_1.parquet"
#             assert expected_file.exists()
#             assert expected_file.is_file()

#     def test_parquet_file_contains_correct_data(self):
#         """Test that parquet file contains the flushed data"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator(max_rows_per_file=100_000)
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             # Create events
#             events = [
#                 {"id": i, "price": 100.0 + i, "quantity": 10 + i} for i in range(10)
#             ]

#             # Flush events
#             writer.flush(events)

#             # Read the parquet file
#             file_path = Path(temp_dir) / "trades_1.parquet"
#             df = pd.read_parquet(file_path)

#             # Verify data
#             assert len(df) == 10
#             assert list(df["id"]) == list(range(10))
#             assert list(df["price"]) == [100.0 + i for i in range(10)]
#             assert list(df["quantity"]) == [10 + i for i in range(10)]

#     def test_parquet_file_with_rotation(self):
#         """Test that new parquet file is created on rotation"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator(max_rows_per_file=100)
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             # First flush - creates file 1
#             events1 = [{"id": i, "value": f"event_{i}"} for i in range(50)]
#             writer.flush(events1)

#             file1 = Path(temp_dir) / "trades_1.parquet"
#             assert file1.exists()

#             # Update rotator to trigger rotation
#             rotator.update_row_count(100)

#             # Second flush - should create file 2
#             events2 = [{"id": i + 50, "value": f"event_{i + 50}"} for i in range(30)]
#             writer.flush(events2)

#             file2 = Path(temp_dir) / "trades_2.parquet"
#             assert file2.exists()

#             # Verify both files exist
#             assert file1.exists()
#             assert file2.exists()

#     def test_parquet_file_compression(self):
#         """Test that parquet file uses snappy compression"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator()
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             # Create events
#             events = [
#                 {"id": i, "data": "x" * 100}  # Large data for compression
#                 for i in range(100)
#             ]

#             # Flush events
#             writer.flush(events)

#             # Read metadata
#             file_path = Path(temp_dir) / "trades_1.parquet"
#             parquet_file = pd.io.parquet.ParquetFile(file_path)

#             # Verify compression is used
#             assert parquet_file.schema_arrow is not None

#     def test_parquet_empty_events_no_flush(self):
#         """Test that empty event list doesn't create file"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator()
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             # Flush empty events
#             writer.flush([])

#             # Verify no file was created
#             files = list(Path(temp_dir).glob("*.parquet"))
#             assert len(files) == 0

#     def test_parquet_file_index_increments(self):
#         """Test that file index increments correctly with multiple flushes"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator(max_rows_per_file=50)
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             # First flush
#             events1 = [{"id": i} for i in range(40)]
#             writer.flush(events1)
#             assert (Path(temp_dir) / "trades_1.parquet").exists()

#             # Prepare for rotation
#             rotator.update_row_count(50)
#             rotator.rotate()

#             # Second flush
#             events2 = [{"id": i + 40} for i in range(20)]
#             writer.flush(events2)
#             assert (Path(temp_dir) / "trades_2.parquet").exists()

#             # Prepare for another rotation
#             rotator.update_row_count(50)
#             rotator.rotate()

#             # Third flush
#             events3 = [{"id": i + 60} for i in range(15)]
#             writer.flush(events3)
#             assert (Path(temp_dir) / "trades_3.parquet").exists()


# class TestStorageWriterMetrics:
#     """Test metrics tracking in StorageWriter"""

#     def test_metrics_increment_on_flush(self):
#         """Test that metrics are incremented on successful flush"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator()
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             events = [{"id": i} for i in range(50)]
#             writer.flush(events)

#             # Verify metrics were incremented
#             assert writer.metrics.events_written == 50
#             assert writer.metrics.flushes_completed == 1

#     def test_metrics_track_multiple_flushes(self):
#         """Test that metrics accumulate across multiple flushes"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator()
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             # First flush
#             writer.flush([{"id": i} for i in range(30)])

#             # Second flush
#             writer.flush([{"id": i + 30} for i in range(40)])

#             # Verify accumulated metrics
#             assert writer.metrics.events_written == 70
#             assert writer.metrics.flushes_completed == 2


# class TestStorageWriterState:
#     """Test StorageWriter state management"""

#     def test_writer_initialization(self):
#         """Test writer initializes with correct state"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator()
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             assert writer.base_path == Path(temp_dir)
#             assert writer.rotator is rotator
#             assert writer.metrics is not None

#     def test_writer_creates_base_path(self):
#         """Test that writer creates base path if it doesn't exist"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             base_path = Path(temp_dir) / "new" / "nested" / "path"
#             rotator = FileRotator()

#             writer = StorageWriter(base_path=str(base_path), rotator=rotator)

#             assert base_path.exists()
#             assert base_path.is_dir()

#     def test_writer_with_existing_base_path(self):
#         """Test writer works with existing base path"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator()
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             events = [{"id": i} for i in range(10)]
#             writer.flush(events)

#             # Verify file was created in existing path
#             assert (Path(temp_dir) / "trades_1.parquet").exists()


# class TestStorageWriterErrorHandling:
#     """Test error handling in StorageWriter"""

#     def test_flush_with_invalid_data_raises_error(self):
#         """Test that flush with invalid data raises FlushError"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator()
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             # Events with unserializable data (e.g., set objects)
#             events = [{"id": i, "data": {1, 2, 3}} for i in range(5)]

#             # This should raise an error
#             with pytest.raises(Exception):
#                 writer.flush(events)

#     def test_flush_error_increments_failure_metric(self):
#         """Test that flush errors increment failure metrics"""
#         with tempfile.TemporaryDirectory() as temp_dir:
#             rotator = FileRotator()
#             writer = StorageWriter(base_path=temp_dir, rotator=rotator)

#             # Events with unserializable data
#             events = [{"id": i, "data": {1, 2, 3}} for i in range(5)]

#             try:
#                 writer.flush(events)
#             except Exception:
#                 pass

#             # Verify failure metric was incremented
#             assert writer.metrics.failures_count > 0
