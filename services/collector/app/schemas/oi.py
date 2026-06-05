# services/collector/app/schemas/oi.py

from dataclasses import dataclass
from typing import ClassVar
from shared.schemas.base import BaseEvent


@dataclass(frozen=True, kw_only=True)
class OpenInterestEvent(BaseEvent):
    open_interest: float

    event_type: ClassVar[str] = "oi"
