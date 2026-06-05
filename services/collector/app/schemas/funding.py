# services/collector/app/schemas/funding.py

from dataclasses import dataclass
from typing import ClassVar
from shared.schemas.base import BaseEvent

"""
FundingEvent schema.
"""


@dataclass(frozen=True, kw_only=True)
class FundingEvent(BaseEvent):
    funding_rate: float
    mark_price: float

    event_type: ClassVar[str] = "funding"

    # Uses default get_checkpoint_int() = event_time (fine)
