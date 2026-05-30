# services/collector/app/validation/validators/duplicate_validator.py

from services.collector.app.validation.validators.base import (
    BaseValidator,
)

from services.collector.app.validation.exceptions import (
    DuplicateEventError,
)


class DuplicateValidator(BaseValidator):
    def __init__(self):
        self.seen_trade_ids = set()

    def validate(self, event) -> None:

        if event.trade_id in self.seen_trade_ids:
            raise DuplicateEventError(f"Duplicate trade id: {event.trade_id}")

        self.seen_trade_ids.add(event.trade_id)
