## ADR‑010: Raw / Silver Data Layer Separation

### Status
Accepted

### Context
The collector writes raw market data to Parquet files in the `raw/` partition. Raw data may contain duplicates (e.g., after a crash and restart, the same batch could be re‑written). It is also stored in the exact schema as received from the exchange.

For ML feature engineering, a **clean, deduplicated, consistent** dataset is required. This is called the **silver layer**.

### Decision
The system will maintain **two separate data layers**:

- **Raw layer** – written by the real‑time collector (`StorageConsumer`). Append‑only, immutable, may contain duplicates. Stored under `data/raw/{stream_type}/...`.
- **Silver layer** – written by an **offline batch job** (or a separate stream processor) that reads raw Parquet files, deduplicates by `(stream_id, event_id)`, applies schema validation, and writes to `data/silver/{stream_type}/...`.

The silver job is **not** a subscriber of `EventRouter`. It processes raw files periodically (e.g., every hour or every N files) and keeps its own **processing checkpoint** (e.g., last processed raw file path) separate from the collector’s operational checkpoint.

### Consequences
- **Positive:** Raw layer remains simple and fast – duplicates allowed.
- **Positive:** Silver layer can be reprocessed from raw if bugs are found or schema changes.
- **Positive:** Feature engineering reads only from silver – a clean, trustworthy dataset.
- **Negative:** Extra processing step (silver job) adds latency – features are not real‑time (acceptable for research).
- **Negative:** Two checkpoint stores are required (one for collector, one for silver job).

### Future Evolution
If real‑time features become necessary, an optional streaming silver layer could be added (e.g., Flink or `EventRouter` subscriber with deduplication state). The raw layer remains the source of truth.

---