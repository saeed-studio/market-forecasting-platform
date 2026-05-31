# # services/collector/tests/unit/storage/test_rotator.py

# import pytest
# from services.collector.app.storage.rotator import FileRotator


# class TestFileRotatorRotation:
#     """Test file rotation scenarios"""

#     def test_rotation_maximum_rows_reached(self):
#         """Test rotation when maximum rows are reached"""
#         rotator = FileRotator(max_rows_per_file=100_000)

#         # Start with initial state
#         assert rotator.file_index == 1
#         assert rotator.current_rows == 0

#         # Simulate adding 99,000 rows
#         rotator.update_row_count(99_000)

#         # Adding 2,000 more rows should trigger rotation
#         assert rotator.should_rotate(2_000) is True

#         # Perform rotation
#         rotator.rotate()

#         # Verify new file is created
#         assert rotator.file_index == 2
#         assert rotator.current_rows == 0

#     def test_rotation_creates_new_file(self):
#         """Test that rotation increments file index for new file"""
#         rotator = FileRotator(max_rows_per_file=100_000)

#         initial_file_index = rotator.file_index

#         # Update rows to near limit
#         rotator.update_row_count(99_500)

#         # Should rotate when adding more rows
#         assert rotator.should_rotate(1_000) is True

#         # Rotate
#         rotator.rotate()

#         # Verify file index increased
#         assert rotator.file_index == initial_file_index + 1
#         # Verify row count reset to 0
#         assert rotator.current_rows == 0

#     def test_rotation_multiple_cycles(self):
#         """Test multiple rotation cycles"""
#         rotator = FileRotator(max_rows_per_file=1_000)

#         # First cycle
#         rotator.update_row_count(900)
#         assert rotator.should_rotate(200) is True
#         rotator.rotate()
#         assert rotator.file_index == 2

#         # Second cycle
#         rotator.update_row_count(900)
#         assert rotator.should_rotate(200) is True
#         rotator.rotate()
#         assert rotator.file_index == 3

#         # Third cycle
#         rotator.update_row_count(900)
#         assert rotator.should_rotate(200) is True
#         rotator.rotate()
#         assert rotator.file_index == 4

#     def test_rotation_no_rotate_below_limit(self):
#         """Test that rotation doesn't occur when below limit"""
#         rotator = FileRotator(max_rows_per_file=100_000)

#         # Add 50,000 rows
#         rotator.update_row_count(50_000)

#         # Adding 30,000 more (total 80,000) should not rotate
#         assert rotator.should_rotate(30_000) is False

#         # File index should remain the same
#         assert rotator.file_index == 1
#         assert rotator.current_rows == 50_000

#     def test_rotation_exact_limit(self):
#         """Test rotation with rows exactly at limit"""
#         rotator = FileRotator(max_rows_per_file=100_000)

#         rotator.update_row_count(100_000)

#         # Adding any rows should trigger rotation
#         assert rotator.should_rotate(1) is True


# class TestFileRotatorState:
#     """Test FileRotator state management"""

#     def test_rotator_initialization(self):
#         """Test rotator initializes with correct values"""
#         rotator = FileRotator(max_rows_per_file=50_000)

#         assert rotator.max_rows_per_file == 50_000
#         assert rotator.current_rows == 0
#         assert rotator.file_index == 1

#     def test_rotator_update_row_count(self):
#         """Test updating row count"""
#         rotator = FileRotator()

#         rotator.update_row_count(100)
#         assert rotator.current_rows == 100

#         rotator.update_row_count(50)
#         assert rotator.current_rows == 150

#         rotator.update_row_count(0)
#         assert rotator.current_rows == 150

#     def test_rotator_should_rotate_cumulative(self):
#         """Test should_rotate logic with cumulative rows"""
#         rotator = FileRotator(max_rows_per_file=1_000)

#         # Incrementally add rows
#         rotator.update_row_count(300)
#         assert rotator.should_rotate(500) is False  # 300 + 500 = 800

#         rotator.update_row_count(500)
#         assert rotator.should_rotate(200) is True  # 800 + 200 = 1000 (at limit)
#         assert rotator.should_rotate(201) is True  # 800 + 201 = 1001 (exceeds limit)

#     def test_rotator_reset_after_rotation(self):
#         """Test that rotate() properly resets state"""
#         rotator = FileRotator(max_rows_per_file=100)

#         rotator.update_row_count(100)
#         initial_file_index = rotator.file_index

#         rotator.rotate()

#         assert rotator.current_rows == 0
#         assert rotator.file_index == initial_file_index + 1

#     def test_rotator_large_batch_size(self):
#         """Test with large rows per file"""
#         rotator = FileRotator(max_rows_per_file=1_000_000)

#         rotator.update_row_count(900_000)
#         assert rotator.should_rotate(100_000) is False
#         assert rotator.should_rotate(100_001) is True

#         rotator.rotate()
#         assert rotator.file_index == 2
#         assert rotator.current_rows == 0

#     def test_rotator_small_batch_size(self):
#         """Test with small rows per file"""
#         rotator = FileRotator(max_rows_per_file=10)

#         rotator.update_row_count(5)
#         assert rotator.should_rotate(4) is False
#         assert rotator.should_rotate(5) is False
#         assert rotator.should_rotate(6) is True
