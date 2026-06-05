## ADR‑008: Backpressure Policy for EventRouter Subscribers

### Status
Accepted

### Context
The `EventRouter` distributes events to multiple subscribers (e.g., `StorageConsumer`, `MetricsConsumer`). Subscribers may have different processing speeds. Without backpressure control, a slow subscriber can cause unbounded memory growth (if queues are unbounded) or block the entire pipeline (if queues are bounded and the publisher awaits).

### Decision
Each subscriber has a **bounded queue** (`asyncio.Queue(maxsize=...)`). The router applies a **per‑subscriber backpressure policy**:

- **`BLOCK`** – The router `await queue.put(event)`. If the queue is full, the publisher (and therefore the entire event pipeline) will block until space becomes available. This ensures **zero data loss** but may slow down all streams.
- **`DROP`** – The router uses `queue.put_nowait(event)`. If the queue is full, the event is dropped and a metric counter is incremented. This prevents blocking but loses data.

### Assigned Policies

| Subscriber            | Policy   | Rationale                                                   |
|-----------------------|----------|-------------------------------------------------------------|
| `StorageConsumer`     | `BLOCK`  | Raw data must not be lost; slower ingestion is acceptable.  |
| `MetricsConsumer`     | `DROP`   | Metrics are sampled; loss is tolerable.                     |
| `SilverDedupConsumer` (future batch job) | N/A | Not a subscriber; runs offline. |
| `FeatureConsumer` (future) | `BLOCK` | Feature generation requires complete data.                  |

### Consequences
- **Positive:** Clear, documented behaviour for each consumer.
- **Positive:** No unbounded memory growth.
- **Negative:** A slow `StorageConsumer` will block trade ingestion (acceptable for research platform; if unacceptable, upgrade storage or increase batch size).
- **Negative:** Metrics may have gaps under high load.
