class StorageError(Exception):
    pass


class FlushError(StorageError):
    pass


class RotationError(StorageError):
    pass
