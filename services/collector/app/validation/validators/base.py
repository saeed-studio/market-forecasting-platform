# services/collector/app/validation/validators/base.py

from abc import ABC, abstractmethod


class BaseValidator(ABC):
    """Base class for all validators in the validation pipeline,
    to make sure they all implement the validate method."""

    @abstractmethod
    def validate(self, event) -> None:
        pass
