from typing import Any, Dict
from abc import ABC, abstractmethod
from aws_lambda_powertools import Logger


class AbstractEventHandler(ABC):
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    @abstractmethod
    def handle_event(self, event: Dict[str, Any]) -> None:
        pass
