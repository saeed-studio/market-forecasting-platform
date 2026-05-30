# services/collector/app/validation/validators/timestamp_validator.py

from services.collector.app.validation.validators.base import (
    BaseValidator,
)

from services.collector.app.validation.exceptions import (
    MissingTimestampError,
)


class TimestampValidator(BaseValidator):
    def validate(self, event) -> None:

        if event.event_time is None:
            raise MissingTimestampError("event_time is missing")

        if event.trade_time is None:
            raise MissingTimestampError("trade_time is missing")
