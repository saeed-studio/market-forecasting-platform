# services/collector/app/storage/rotator.py


class FileRotator:
    def __init__(
        self,
        max_rows_per_file: int = 100_000,
    ) -> None:

        self.max_rows_per_file = max_rows_per_file

        self.current_rows = 0

        self.file_index = 1

    def should_rotate(
        self,
        incoming_rows: int,
    ) -> bool:

        return self.current_rows + incoming_rows > self.max_rows_per_file

    def rotate(self) -> None:

        self.current_rows = 0

        self.file_index += 1

    def update_row_count(
        self,
        rows: int,
    ) -> None:

        self.current_rows += rows
