# services/collector/app/validation/pipeline.py

from services.collector.app.validation.validators.timestamp_validator import (
    TimestampValidator,
)

from services.collector.app.validation.validators.sequence_validator import (
    SequenceValidator,
)

from services.collector.app.validation.validators.duplicate_validator import (
    DuplicateValidator,
)


class ValidationPipeline:
    def __init__(self):

        self.validators = [
            TimestampValidator(),
            DuplicateValidator(),
            SequenceValidator(),
        ]

    def validate(self, event):

        for validator in self.validators:
            validator.validate(event)

        return event
