# ADR-004

## Decision:
Use asyncio.Queue for MVP.

## Reason:
Simple.
No external dependency.
Sufficient for single-process collector.

## Trade-off:
Not distributed.
Not durable.

## Future:
Kafka or Redis Streams or RabbitMQ.