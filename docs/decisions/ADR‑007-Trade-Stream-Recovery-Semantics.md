# ADR‑007: Trade Stream Recovery Semantics
## Status
Accepted

## Context
The Binance Trade WebSocket stream is live‑only. When the collector crashes or disconnects, there is no way to retrieve trades that occurred during the downtime via the WebSocket API. The exchange does not provide a mechanism to replay historical trades by trade_id range.

## Decision
We accept that trades received during collector downtime will be lost. The collector will resume from the point of reconnection, not from the last processed trade. No attempt is made to backfill missing trades.

For recovery, the collector stores a checkpoint of the last successfully written trade_id (or event_time) per symbol. On restart, it starts consuming the live stream from the current moment, not from the checkpoint. The checkpoint is used only to skip events that are older than the last persisted event (i.e., to avoid reprocessing events that were already written before the crash). It does not guarantee that every trade is processed exactly once.

## Consequences
Positive: Simple implementation; no complex backfill logic for trades.

Positive: High ingestion performance (no per‑event duplicate detection).

Negative: Trade data gaps may occur during crashes or network partitions.

Negative: Feature engineering that relies on perfect trade‑level history may be affected (mitigated by using 1‑minute aggregates where small gaps are tolerable).

## Future Enhancement
If perfect trade recovery becomes necessary, a separate historical trade downloader can be built using Binance REST aggTrades endpoint (limited to recent history). This would run as a backfill job, not part of the real‑time collector.

