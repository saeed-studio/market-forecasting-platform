## ADR‑011: Schema Registry for Event Evolution

### Status
Accepted

### Context
Event schemas (`TradeEvent`, `KlineEvent`, etc.) will evolve over time. New fields may be added, field types may change, or whole new event versions may be introduced. Without a central registry, different consumers may interpret the same data incorrectly after a schema change.

### Decision
A **Schema Registry** is introduced as a core component. Every `BaseEvent` carries a `schema_version` integer. The registry maintains a mapping of `(event_type, version)` to:

- A deserializer function that converts raw data (e.g., from Parquet) into the corresponding event object.
- A migration path (optional) for upgrading older versions.

Serializers and deserializers use the registry to ensure that any event read from storage is correctly interpreted according to its version.

### Implementation (MVP)
```python
class SchemaRegistry:
    _registry = {}  # (event_type, version) -> deserializer

    @classmethod
    def register(cls, event_type: str, version: int, deserializer: Callable):
        cls._registry[(event_type, version)] = deserializer

    @classmethod
    def get(cls, event_type: str, version: int):
        return cls._registry.get((event_type, version))
```

When a new event version is needed:
1. Define a new class (e.g., `TradeEventV2`).
2. Register its deserializer with version `2`.
3. Update the collector to produce version `2` (optional, can be rolled out gradually).
4. Consumers check version and use the appropriate deserializer.

### Consequences
- **Positive:** Safe schema evolution without breaking stored data.
- **Positive:** Multiple versions can coexist in storage.
- **Negative:** Adds complexity; requires discipline from developers.
- **Negative:** Minor performance overhead for version lookup (negligible).

---