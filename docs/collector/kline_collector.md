# Kline Collector Design

## Purpose

The Kline Collector is a specialized data ingestion system designed to collect candlestick (kline) data from Binance Futures. The system focuses on collecting **closed candles only** to support feature engineering and backtesting applications, while maintaining data quality through validation and supporting both live and historical data collection.

## Architecture Overview

The collector operates in two distinct modes to handle different data sourcing requirements:

### Data Sources

| Mode | Source | Purpose |
|------|--------|---------|
| **Live Mode** | WebSocket | Real-time candle updates |
| **Backfill Mode** | REST API | Historical data recovery |

## Domain Schema

The system uses a Binance-agnostic schema to decouple from exchange-specific payloads:

```python
KlineEvent {
    symbol: str           # Trading pair (e.g., "BTCUSDT")
    interval: str         # Candle interval (e.g., "1m")
    open_time: int        # Candle open timestamp (ms)
    close_time: int       # Candle close timestamp (ms)
    open: float           # Open price
    high: float           # Highest price
    low: float            # Lowest price
    close: float          # Close price
    volume: float         # Trading volume
    quote_volume: float   # Quote asset volume
    trade_count: int      # Number of trades
    taker_buy_volume: float  # Taker buy base volume
    is_closed: bool       # Final candle flag (x from Binance)
    exchange_timestamp: int   # Exchange timestamp (ms)
    received_at: int      # Local receive timestamp (ms)
}
```

## Critical Design Decision: Closed Candles Only

### Why `is_closed` Matters

Binance WebSocket sends multiple updates for the same incomplete candle. For example, during a `1m` candle from `12:00:00` to `12:00:59`:

```
12:00:10 → Update 1 (candle still forming)
12:00:20 → Update 2
12:00:30 → Update 3
...
12:00:59 → Final update with "x": true
```

Only the final update (where `"x": true`) represents the closed, immutable candle. For feature engineering and backtesting, **only closed candles are meaningful**.

### Storage Strategy (MVP)

The MVP stores **only closed candles**:
- ✅ Lower storage requirements
- ✅ No noise from partial updates
- ✅ Clean feature engineering inputs
- ❌ Cannot reconstruct intra-candle movements

## Interval Strategy

### Single-Interval Collection

Collect only `1m` candles. Do **not** collect multiple intervals directly.

### Derived Intervals

All higher timeframes are generated via resampling from `1m` data:

```python
resample_rules = {
    "5m": "5min",
    "15m": "15min", 
    "1h": "1H",
    "4h": "4H"
}
```

### Benefits

- **Consistency** - Single source of truth
- **Storage Efficiency** - Store once, derive many
- **Simpler Validation** - Only need to validate one interval

## Storage Layout

Parquet partitioning structure (mirroring Trade Event pattern):

```
raw/
└── binance/
    └── klines/
        └── BTCUSDT/
            └── interval=1m/
                └── date=2026-06-02/
                    ├── part-00001.parquet
                    ├── part-00002.parquet
                    └── ...
```

## Validation Rules

The `KlineValidator` must enforce these checks:

### 1. Timestamp Order
```
✅ Valid:   12:00 → 12:01 → 12:02
❌ Invalid: 12:00 → 12:02 → 12:01
```

### 2. Missing Candle Detection
If sequence arrives as `12:00, 12:01, 12:03`, log:
```
MISSING_CANDLE: expected 12:02, got 12:03
```

### 3. Duplicate Detection
Candles with same `open_time` arriving twice → Reject second occurrence

### 4. Price Integrity
- `volume >= 0` (no negative volume)
- `high >= low` (valid price range)
- `open` within `[low, high]`
- `close` within `[low, high]`

## Data Flow Architecture

```
                    ┌─────────────────┐
                    │   WebSocket     │
                    │   Connection    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ ConnectionManager│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  KlineConsumer  │
                    │  (raw handler)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Validator     │
                    │ • order check   │
                    │ • duplicates    │
                    │ • price bounds  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   EventQueue    │
                    │  (buffered)     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ StorageConsumer │
                    │ (Parquet writer)│
                    └─────────────────┘
```

## Operational Modes

### Live Mode (WebSocket)
- Continuous connection to Binance WebSocket stream
- Real-time candle update processing
- Filtering for closed candles only

### Backfill Mode (REST)
- HTTP-based historical data retrieval
- Critical for recovery scenarios:
  - Collector crash
  - Extended downtime (days/weeks)
  - Data gaps detection

```
Scenario: Collector offline for 1 week
    ↓
Execute Backfill Mode for date range
    ↓
REST API fetches historical 1m candles
    ↓
Validator checks for completeness
    ↓
Write to storage with backfill flag
```

## Metrics & Monitoring

From day one, track these metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `klines_received` | Counter | Total raw updates received |
| `klines_stored` | Counter | Closed candles successfully stored |
| `validation_errors` | Counter | Failed validation checks |
| `duplicates` | Counter | Duplicate candle detections |
| `missing_candles` | Counter | Detected gaps in sequence |
| `reconnect_count` | Counter | WebSocket reconnection events |

## Failure Modes

### WebSocket Disconnection
1. `ConnectionManager` detects disconnection
2. Exponential backoff reconnection
3. After reconnection: check for gap period
4. Trigger backfill for missing range

### Storage Failure
1. Local buffering of validated events
2. Retry with backoff
3. Alert on persistent failure

### Validation Failure
1. Log error with full event details
2. Increment `validation_errors` metric
3. Discard invalid event (do not store)

## Definition of Done

The Kline Collector is considered complete when all of the following are implemented:

| Component | Status |
|-----------|--------|
| Live WebSocket streaming | ✅ |
| Closed candle filtering (`x == true`) | ✅ |
| Validation rules (6 checks) | ✅ |
| Parquet storage with partitioning | ✅ |
| Metrics collection | ✅ |
| Structured logging | ✅ |
| Historical REST backfill | ✅ |
| Unit & integration tests | ✅ |

## Implementation Notes

### File Structure
```
collector/
├── kline_consumer.py    # Main consumer logic
├── kline_validator.py   # Validation rules
├── kline_backfill.py    # Historical REST sync
└── models/
    └── kline_event.py   # Domain schema
```

### Key Dependencies
- `websockets` - Binance WebSocket client
- `ccxt` or `python-binance` - REST API client
- `pyarrow` / `pandas` - Parquet storage
- `structlog` - Structured logging
- `prometheus_client` - Metrics export

---

*Documentation version 1.0 - Based on design review date: 2026-06-02*