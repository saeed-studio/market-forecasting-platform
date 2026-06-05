# services/collector/app/checkpoint/store.py

import aiosqlite
import asyncio
from pathlib import Path
from typing import Optional

from shared.logging.config import get_logger

logger = get_logger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS checkpoints (
    stream_key TEXT PRIMARY KEY,
    checkpoint_value TEXT NOT NULL,
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s','now'))
)
"""


class CollectorCheckpointStore:
    """A simple checkpoint store that uses SQLite to persist checkpoint values for different stream keys.
    This allows the collector to resume from the last checkpoint after a restart."""

    def __init__(self, db_path: str = "data/checkpoints.db"):
        """Initializes the checkpoint store with the given database path.
        The database file will be created if it does not exist."""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[aiosqlite.Connection] = (
            None  # connection will be initialized in init()
        )
        self._lock = asyncio.Lock()

    async def init(self) -> None:
        """Call this once before using the store."""
        self._conn = await aiosqlite.connect(self.db_path)
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA synchronous=NORMAL")
        await self._conn.execute(CREATE_TABLE_SQL)
        await self._conn.commit()
        logger.info(f"Checkpoint store initialized at {self.db_path}")

    async def get_checkpoint(self, stream_key: str) -> Optional[str]:
        """Returns the checkpoint value for the given stream key, or None if not found."""
        if not self._conn:
            raise RuntimeError("Checkpoint store not initialized")
        async with self._lock:
            cursor = await self._conn.execute(
                "SELECT checkpoint_value FROM checkpoints WHERE stream_key = ?",
                (stream_key,),
            )
            row = await cursor.fetchone()
            return row[0] if row else None

    async def set_checkpoint(self, stream_key: str, checkpoint_value: str) -> None:
        """Sets the checkpoint value for the given stream key. If the key already exists, it will be updated."""
        if not self._conn:
            raise RuntimeError("Checkpoint store not initialized")
        async with self._lock:
            await self._conn.execute(
                """INSERT OR REPLACE INTO checkpoints
                   (stream_key, checkpoint_value, updated_at)
                   VALUES (?, ?, strftime('%s','now'))""",
                (stream_key, checkpoint_value),
            )
            await self._conn.commit()

    async def set_checkpoints_multi(self, checkpoints: dict[str, str]) -> None:
        """
        Set multiple checkpoints in a single transaction.
        checkpoints: dict[stream_key, checkpoint_value]
        """
        if not self._conn:
            raise RuntimeError("Checkpoint store not initialized")
        if not checkpoints:
            return
        async with self._lock:
            await self._conn.executemany(
                """INSERT OR REPLACE INTO checkpoints
                (stream_key, checkpoint_value, updated_at)
                VALUES (?, ?, strftime('%s','now'))""",
                [(key, value) for key, value in checkpoints.items()],
            )
            await self._conn.commit()

    async def close(self) -> None:
        """Closes the database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None
