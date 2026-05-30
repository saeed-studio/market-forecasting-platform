# ADR-001

## Decision

Use asyncio.Queue instead of Kafka for MVP.

## Context

The project currently handles a single exchange and a single symbol.

## Consequences

Lower complexity and faster development.
Kafka can be introduced later without changing service boundaries.

-------------------------------------------------------------------
