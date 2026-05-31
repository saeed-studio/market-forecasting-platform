# # services/collector/tests/unit/storage/test_batcher.py

# import time
# import pytest
# from services.collector.app.storage.batcher import EventBatcher


# class TestEventBatcherFlush:
#     """Test batch flush scenarios"""

#     def test_batch_flush_100_events(self):
#         """Test that 100 events are batched and ready for flush"""
#         batcher = EventBatcher(batch_size=100, flush_interval=30)

#         # Add 100 events
#         for i in range(100):
#             batcher.add({"id": i, "value": f"event_{i}"})

#         # Verify should_flush returns True
#         assert batcher.should_flush() is True
#         assert len(batcher.events) == 100

#     def test_batch_flush_buffer_empty_after_reset(self):
#         """Test that buffer is empty after reset (flush)"""
#         batcher = EventBatcher(batch_size=100, flush_interval=30)

#         # Add 100 events
#         for i in range(100):
#             batcher.add({"id": i, "value": f"event_{i}"})

#         # Verify buffer has events
#         assert len(batcher.events) == 100

#         # Reset (simulating flush)
#         batcher.reset()

#         # Verify buffer is empty
#         assert len(batcher.events) == 0
#         assert batcher.events == []

#     def test_batch_flush_less_than_batch_size_no_flush(self):
#         """Test that events less than batch_size don't trigger flush"""
#         batcher = EventBatcher(batch_size=100, flush_interval=30)

#         # Add 50 events (less than batch_size)
#         for i in range(50):
#             batcher.add({"id": i, "value": f"event_{i}"})

#         # should_flush should return False based on size
#         assert batcher.should_flush() is False
#         assert len(batcher.events) == 50

#     def test_batch_flush_exact_batch_size(self):
#         """Test flush triggers at exact batch_size"""
#         batcher = EventBatcher(batch_size=100, flush_interval=30)

#         # Add exactly batch_size events
#         for i in range(100):
#             batcher.add({"id": i, "value": f"event_{i}"})

#         assert batcher.should_flush() is True
#         assert len(batcher.events) == 100

#     def test_batch_flush_exceeds_batch_size(self):
#         """Test flush triggers when exceeding batch_size"""
#         batcher = EventBatcher(batch_size=100, flush_interval=30)

#         # Add more than batch_size events
#         for i in range(105):
#             batcher.add({"id": i, "value": f"event_{i}"})

#         assert batcher.should_flush() is True
#         assert len(batcher.events) == 105

#     def test_batch_flush_time_interval(self):
#         """Test flush triggers based on time interval"""
#         batcher = EventBatcher(batch_size=1000, flush_interval=1)

#         # Add events but less than batch_size
#         for i in range(100):
#             batcher.add({"id": i, "value": f"event_{i}"})

#         # Should not flush based on size
#         assert batcher.should_flush() is False

#         # Wait for flush interval to pass
#         time.sleep(1.1)

#         # Should flush based on time interval
#         assert batcher.should_flush() is True

#     def test_batch_reset_updates_flush_time(self):
#         """Test that reset updates the last_flush_time"""
#         batcher = EventBatcher(batch_size=100, flush_interval=1)

#         initial_flush_time = batcher.last_flush_time
#         time.sleep(0.5)

#         # Add events
#         for i in range(100):
#             batcher.add({"id": i, "value": f"event_{i}"})

#         batcher.reset()

#         # Verify flush time is updated
#         assert batcher.last_flush_time > initial_flush_time


# class TestEventBatcherState:
#     """Test EventBatcher state management"""

#     def test_batcher_initialization(self):
#         """Test batcher initializes with correct values"""
#         batcher = EventBatcher(batch_size=500, flush_interval=60)

#         assert batcher.batch_size == 500
#         assert batcher.flush_interval == 60
#         assert batcher.events == []
#         assert isinstance(batcher.last_flush_time, float)

#     def test_batcher_add_single_event(self):
#         """Test adding a single event"""
#         batcher = EventBatcher()
#         event = {"id": 1, "value": "test"}

#         batcher.add(event)

#         assert len(batcher.events) == 1
#         assert batcher.events[0] == event

#     def test_batcher_add_multiple_events(self):
#         """Test adding multiple events maintains order"""
#         batcher = EventBatcher()
#         events = [{"id": i, "value": f"event_{i}"} for i in range(10)]

#         for event in events:
#             batcher.add(event)

#         assert len(batcher.events) == 10
#         assert batcher.events == events
