from typing import Any, Dict, List

from chalicelib.handlers.abstract_handler import AbstractEventHandler

from aws_lambda_powertools import Logger


class PollingProcessor(AbstractEventHandler):
    def __init__(self, logger: Logger):
        super().__init__(logger)

    def _get_records(self, event: Dict[str, Any]) -> List[Any]:
        return ["ppp_id"]

    def _poll_status(self, ppp_id: str) -> bool:
        detail = None
        success = True
        response = self._sba_proxy.get_status(ppp_id)

        try:
            detail = response.detail
        except:
            detail = "Unknown"
        self._logger.error(
            {
                "message": f"Error Getting Status for PPP: {ppp_id}",
                "ppp_id": ppp_id,
                "upstream_message": detail,
            }
        )

        self._record_event(success, ppp_id, detail)

    def handle_event(self, event: Dict[str, Any]) -> None:
        self._logger.info({"message": "Starting Poll Batch"})
        awaiting_response = self._get_records(event)

        self._logger.info(
            {
                "message": "Found Records to Poll",
                "number_of_records": len(awaiting_response),
            }
        )

        for ppp in awaiting_response:
            ppp_id = ppp.id

            if self._poll_status(ppp_id) is True:
                self._delete_message(ppp)
                self._logger.info({"title": "Deleting Message", "ppp_id": ppp_id})
            else:
                self._logger.warn(
                    {
                        "title": "Unable to successfully poll for status",
                        "ppp_id": ppp_id,
                    }
                )

        self._logger.info({"message": "Completed Polling Processor Batch"})
