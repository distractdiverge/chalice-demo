import json
from typing import Any, Dict, NamedTuple, Union, List

from aws_lambda_powertools import Logger
from chalice.app import SNSEvent

from chalicelib.handlers.abstract_handler import AbstractEventHandler
from chalicelib.services.s3 import S3Client

#
# Example SNS Message
#
# {
#   "source_bucket": "ppbfs-dm-internal-data-pipeline",
#   "environment": "prod",
#   "business_type": "LexisNexisFraudPoint",
#   "object_name": "Response",
#   "filename": "2021-01-15",
#   "source_file":
#   "prod/LexisNexisFraudPoint/Response/2021-01-15/0063b00001Gc8vuAAB-2438854_aed83c63-a690-4ae1-b43c-4fcf4f037716"
# }
#
class PipelineEvent(NamedTuple):
    message_subject: str
    source_bucket: str
    environment: str
    business_type: str
    object_name: str
    filename: str
    source_file: str


class ParseJSONHandler(AbstractLambdaHandler):
    SUBMISSIONS_CATEGORY = "Submissions"
    POLL_CATEGORY = "StatusUpdates"
    RESCISSION_CATEGORY = "Rescissions"

    _prodswiftcore: ProdSwiftCore
    _parser: PPPParser
    _s3: S3Client

    def __init__(
        self,
        logger: Logger,
        prodswiftcore: ProdSwiftCore,
        ppp_parser: PPPParser,
        s3_client: S3Client,
    ):
        super().__init__(logger)
        self._s3 = s3_client
        self._prodswiftcore = prodswiftcore
        self._parser = ppp_parser

    def _parse_event(self, event: SNSEvent) -> PipelineEvent:
        if event is None:
            raise Exception("Expecting some kind of event, but got none")

        if event.subject is None or event.message is None:
            raise Exception("No Subject or Message on event")

        subject = event.subject
        raw_message = event.message
        message = json.loads(raw_message)
        self._logger.info(
            {
                "message": "Successfully Parsed SNSEvent",
                "event": str(message),
            }
        )
        return PipelineEvent(
            message_subject=subject,
            source_bucket=message["source_bucket"],
            environment=message["environment"],
            business_type=message["business_type"],
            object_name=message["object_name"],
            filename=message["filename"],
            source_file=message["source_file"],
        )

    def _get_file(self, bucket_name: str, key: str) -> Dict[str, Any]:
        return self._s3.read_json_file(bucket_name, key)

    def _parse_file(self, category: str, file_contents: Dict[str, Any]):
        if category == self.SUBMISSIONS_CATEGORY or category == self.POLL_CATEGORY:
            if category == self.SUBMISSIONS_CATEGORY:
                response_json = file_contents["PPP3LoanOriginationResponse"]
            elif category == self.POLL_CATEGORY:
                response_json = file_contents["PPP3LoanOrigination"]

            return self._parse_ppp3(category, response_json)

        elif category == self.RESCISSION_CATEGORY:
            return self._parse_rescission(category, file_contents)
        else:
            raise Exception(
                f'Unknown category type "{category}", cannot parse and save it'
            )

    def _parse_ppp3(
        self, source: str, json_contents: Dict[str, Any]
    ) -> List[Union[Ppp3LoanOrigination, PppBusines, List[PppBusinessOwner]]]:
        self._logger.info({"message": f"Parsing {source}"})
        return self._parser.parse(source, json_contents)

    def _parse_rescission(
        self, source: str, json_contents: Dict[str, Any]
    ) -> PppRescission:
        self._logger.info({"message": f"Parsing {source}"})
        return self._parser.parse_rescission(source, json_contents)

    def _save_contents(
        self,
        business: PppBusines,
        owners: List[PppBusinessOwner],
        rootElement: Ppp3LoanOrigination,
    ) -> bool:
        return self._prodswiftcore.save_ppp(business, owners, rootElement)

    def handle_event(self, event: SNSEvent) -> None:
        pipeline_event = self._parse_event(event)
        self._logger.info({"message": "Parsed SNS Event", "event": pipeline_event})

        json_file = self._get_file(
            pipeline_event.source_bucket, pipeline_event.source_file
        )

        category = pipeline_event.object_name
        if category == self.SUBMISSIONS_CATEGORY or category == self.POLL_CATEGORY:
            (business, owners, root) = self._parse_file(
                pipeline_event.object_name, json_file
            )
            response = self._save_contents(business, owners, root)
        elif category == self.RESCISSION_CATEGORY:
            # TODO: Capture different return value for Rescissions
            response = None

        if response:
            self._logger.info(
                {
                    "message": "Parse Complete",
                    "event": pipeline_event,
                }
            )
        else:
            self._logger.error(
                {
                    "message": "Error, did not save file to PSC",
                    "event": pipeline_event,
                    "raw_event": event,
                }
            )
