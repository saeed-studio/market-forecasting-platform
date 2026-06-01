# ADR 005

## Current:
Rewrite parquet file.

## Reason:
Simple MVP.

## Future:
PyArrow Dataset Writer
Partitioned append strategy.

------------------------------------
## Decision 2026-06-01
Saving raw data on daily and hourly partitions.

## Reason
adding a new file on each partition , creates a big mess on data folders


