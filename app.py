from typing import Any, Dict
from chalice import Chalice, Cron
from chalice.app import ConvertToMiddleware, SNSEvent, SQSEvent
from aws_lambda_powertools import Logger

from chalicelib.services.config import get_aws_config, AWSConfig
from chalicelib.services.s3 import S3Client
from chalicelib.services.sqs import SQSClient
from chalicelib.services.etl_parser import ETLParser
from chalicelib.handlers.parse_json import ParseJSONHandler
from chalicelib.handlers.polling_ingestor import PollingIngestor
from chalicelib.handlers.polling_processor import PollingProcessor


app = Chalice(app_name="chalice-demo")
logger = Logger(
    service="chalice-demo",
    log_record_order=["timestamp", "service", "level", "location", "message"],
)

app.register_middleware(ConvertToMiddleware(logger.inject_lambda_context))


def config_factory() -> AWSConfig:
    return get_aws_config()


def s3_factory():
    return S3Client(logger)


def sqs_factory():
    config = config_factory()
    queue_name = config.queue_name
    return SQSClient(queue_name, logger)


def etl_parser_factory():
    config = config_factory()
    return ETLParser(logger, config)


every_min = Cron("0/1", "*", "*", "*", "?", "*")
every_3mins = Cron("0/3", "*", "*", "*", "?", "*")


@app.on_sns_message(topic="chalice-demo-input.fifo")
def etl_parser(event: SNSEvent) -> None:
    """
    Respond to a new S3 Record Post -- Parse the JSON file
    """
    config = config_factory()
    parser = etl_parser_factory()

    return ParseJSONHandler(logger, config, parser).handle_event(event)


@app.schedule(every_min)
def polling_ingestor(event: Dict[str, Any]):
    """
    Populate the SQS Queue with a list of messages to be processed (allow fan-out)
    """
    logger.info("Called Ingestor")

    sqs = sqs_factory()
    config = config_factory()
    return PollingIngestor(logger, config, sqs).handle_event(event)


@app.on_sqs_message("chalice_demo.fifo", batch_size=3)
def polling_processor(event: SQSEvent):
    """
    Process a chunk of messages as they are created in the queue
    """
    logger.info("Called Processor")

    config = config_factory()
    return PollingProcessor(logger, config).handle_event(event)
