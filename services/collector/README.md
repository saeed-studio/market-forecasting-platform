# Collector Service

## Responsibility

Collect realtime market data from exchanges.

## Components

- Connection Manager
- Stream Consumer
- Validation Layer
- Async Queue
- Storage Writer

## Data Flow

Binance
→ Connection Manager
→ Consumer
→ Validation
→ Queue
→ Storage