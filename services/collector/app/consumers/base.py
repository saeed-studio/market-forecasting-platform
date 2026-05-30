# services/collector/app/consumers/base.py

from abc import ABC, abstractmethod


class BaseConsumer(ABC):
    @abstractmethod
    def consume(self, payload: dict):
        raise NotImplementedError
