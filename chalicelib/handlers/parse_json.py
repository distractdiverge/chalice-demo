import json

from aws_lambda_powertools import Logger
from chalice.app import SNSEvent

from chalicelib.handlers.abstract_handler import AbstractEventHandler


class ParseJSONHandler(AbstractEventHandler):
    def __init__(self, logger: Logger):
        super().__init__(logger)

    def handle_event(self, event: SNSEvent) -> None:
        self._logger.info(
            {"message": "test-invoke-etl-parser", "event": json.dumps(event)}
        )
