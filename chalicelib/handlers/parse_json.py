from aws_lambda_powertools import Logger
from chalice.app import SNSEvent

from chalicelib.handlers.abstract_handler import AbstractEventHandler


class ParseJSONHandler(AbstractEventHandler):
    def __init__(self, logger: Logger):
        super().__init__(logger)

    def handle_event(self, event: SNSEvent) -> None:

        if event:
            self._logger.info(
                {
                    "message": "Parse Complete",
                    "event": event,
                }
            )
        else:
            self._logger.error(
                {"message": "Error, did not save file to PSC", "event": event}
            )
