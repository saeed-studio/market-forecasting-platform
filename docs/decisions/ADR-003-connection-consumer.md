# ADR-003

## Decision
Use dataclass instead of pydantic for MVP . 

## Context
The project currently need to be faster and simpler 

## Consequences
Lower complexity and faster development. pydantic can be replaced later if needed

-------------------------------------------------------------------
## Decision 
using validation pipeline over simple validations.

## Context
project will have different validations for each one of consumers.

## Consequences
We dont need to write a djungle of if-else statements. 

-----------------------------------------------------------------------


## Current:
In-memory set()

## Reason:
Simplicity and MVP scope

## Future:
Redis-backed state store
or Kafka compacted topic

-----------------------------------------------------------------------
