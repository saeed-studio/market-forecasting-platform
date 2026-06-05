# services/collector/app/core/stream_definition.py
"""This module defines the StreamDefinition class, which represents a unique identifier
for a data stream in the system. It includes the exchange, symbol, and stream type,
and provides a method to generate a unique key for the stream."""

from dataclasses import dataclass


@dataclass(frozen=True)  # frozen to make it immutable
class StreamDefinition:
    exchange: str
    symbol: str
    stream_type: str

    def key(self) -> str:
        return f"{self.exchange}:{self.symbol}:{self.stream_type}"
