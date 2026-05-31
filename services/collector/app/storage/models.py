# services/app/storage/models.py

from dataclasses import dataclass


@dataclass(slots=True)
class StorageBatch:
    events: list[dict]
