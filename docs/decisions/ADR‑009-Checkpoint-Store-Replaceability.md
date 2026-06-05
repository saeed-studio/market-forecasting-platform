## ADR‑009: Checkpoint Store Replaceability

### Status
Accepted

### Context
The collector needs a persistent store for checkpoints (last processed event ID per stream). Initially, SQLite with WAL mode is used because it is simple, transactional, and sufficient for the expected load (checkpoint writes happen every few seconds or per batch).

However, future scaling (many symbols, many streams, multiple consumers) may require a more robust or distributed solution (e.g., Redis, PostgreSQL, etc.).

### Decision
The `CheckpointStore` is defined as an **abstract interface**. The initial implementation uses SQLite. All components depend only on the interface, not on SQLite specifics.

```python
class CheckpointStore(ABC):
    @abstractmethod
    def get_checkpoint(self, stream_def: StreamDefinition, checkpoint_type: str) -> str | None: ...
    @abstractmethod
    def set_checkpoint(self, stream_def: StreamDefinition, checkpoint_type: str, value: str, event_time: int): ...
```

The SQLite implementation is configured with:
- `PRAGMA journal_mode=WAL`
- `PRAGMA synchronous=NORMAL`

### Consequences
- **Positive:** Easy to swap backends later without refactoring.
- **Positive:** SQLite is sufficient for MVP and early production.
- **Negative:** Slight indirection overhead (negligible).
- **Negative:** Some advanced features (e.g., high‑availability) are not available with SQLite, but they are not required initially.

---