# ADR-002

## Context

Collector must survive temporary network failures.

## Decision

Use exponential backoff reconnect strategy.

## Consequences

Improves resilience but may increase recovery time.