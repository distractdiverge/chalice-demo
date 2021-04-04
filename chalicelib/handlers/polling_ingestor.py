from typing import Any, Dict, List, NamedTuple

from chalicelib.handlers.abstract_handler import AbstractEventHandler
from chalicelib.services.config import PPPConfig
from chalicelib.services.sqs import SQSClient

from aws_lambda_powertools import Logger


class PollingIngestor(AbstractLambdaHandler):
    _config: PPPConfig
    _ppp_repository: PPPRepository
    _sqs: SQSClient

    def __init__(
        self, logger: Logger, config: PPPConfig,
        sqs: SQSClient
    ):
        super().__init__(logger)
        self._config = config
        self._ppp_repository = ppp_repository
        self._sqs = sqs

    def _get_records(self) -> List[PPPSummaryRecord]:
        return []

    def handle_event(self, event: Dict[str, Any]) -> None:
        self._logger.info({"message": "Starting Poll Ingestor"})
        awaiting_response = self._get_records()

        self._logger.info(
            {
                "message": "Found Records to Poll",
                "number_of_records": len(awaiting_response),
                "queue_name": self._config.queue_name,
            }
        )

        for ppp in awaiting_response:
            self._sqs.send_message(ppp)

        self._logger.info({"message": "Completed Poll Ingestor"})
