# shared/schemas/base_event.py

from abc import ABC
from dataclasses import dataclass
from typing import ClassVar

"""
Base event dataclass for all collector events.
why we need this abstraction class ? this calss provides a common structure for all event types, ensuring consistency
and reusability across different event schemas. By defining shared fields and methods in a base class, we can avoid
code duplication and make it easier to manage and extend our event definitions in the future.
Each specific event type can inherit from this base class and add its own unique fields while still maintaining a
consistent interface for processing events.
"""

"""
Base event dataclass for all collector events.
"""


@dataclass(frozen=True)
class BaseEvent(ABC):
    """
    Common fields for every event type.
    Subclasses must override the `event_type` class variable.
    """

    event_id: str
    symbol: str
    exchange: str
    event_time: int  # Unix milliseconds
    schema_version: int = 1

    # Abstract class attribute – each subclass defines its own string
    event_type: ClassVar[str] = ""

    def get_checkpoint_value(self) -> str:
        """
        Return a value used for checkpoint/resume.
        Default: f"{symbol}_{event_time}"
        """
        return f"{self.symbol}_{self.event_time}"

    def get_checkpoint_int(self) -> int:
        """
        Monotonically increasing integer for checkpoint ordering.
        Override in subclasses (e.g., trade_id, close_time).
        """
        return self.event_time

    @property
    def stream_key(self) -> str:
        """Unique key for this stream: exchange:symbol:event_type"""
        return f"{self.exchange}:{self.symbol}:{self.event_type}:1m"
