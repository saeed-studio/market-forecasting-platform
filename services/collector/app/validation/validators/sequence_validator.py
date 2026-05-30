# services/collector/app/validation/validators/sequence_validator.py


from services.collector.app.validation.validators.base import (
    BaseValidator,
)

from services.collector.app.validation.exceptions import (
    OutOfOrderEventError,
)


class SequenceValidator(BaseValidator):
    def __init__(self):
        self.last_timestamp = None

    def validate(self, event) -> None:

        if self.last_timestamp is None:
            self.last_timestamp = event.event_time
            return

        if event.event_time < self.last_timestamp:
            raise OutOfOrderEventError(
                (
                    f"Event timestamp "
                    f"{event.event_time} "
                    f"is older than "
                    f"{self.last_timestamp}"
                )
            )

        self.last_timestamp = event.event_time
