import json
import os

from typing import Any, Dict
from chalice import Chalice, Cron
from chalice.app import ConvertToMiddleware, SNSEvent, SQSEvent
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer

from chalicelib.services.config import (
    get_ppp_config,
    get_dropzone_config,
    get_database_config,
)
from chalicelib.services.s3 import S3Client
from chalicelib.services.sqs import SQSClient
from chalicelib.handlers.polling_ingestor import PollingIngestor
from chalicelib.handlers.polling_processor import PollingProcessor


app = Chalice(app_name="chalice-demo")
logger = Logger(
    service="chalice-demo",
    log_record_order=["timestamp", "service", "level", "location", "message"],
)

app.register_middleware(ConvertToMiddleware(logger.inject_lambda_context))

def s3_factory():
    return S3Client(logger)


def sqs_factory():
    ppp_config = get_ppp_config()
    queue_name = ppp_config.queue_name
    return SQSClient(queue_name, logger)


every_15_mins = Cron("0/15", "*", "*", "*", "?", "*")


@app.on_sns_message(topic="DM-InternalDataPipeline-Arrival")
def etl_parser(event: SNSEvent) -> None:
    """
    Triggered whenever an event is posted to the internal DM Pipeline.

    Only process events that match our expected pattern.
    """
    allowed_subjects = ["ppporigination"]

    if event is None:
        raise Exception("Missing event")

    logger.info(f"Event->Subject: {event.subject}")
    if str.lower(event.subject) not in allowed_subjects:
        logger.info(f'Ignoring SNS Event with subject "{event.subject}"')
        return None

    # Positive scenario
    logger.info(f"Event->Message: {event.message}")
    psc = prod_swift_core_factory()

    # Make sure DB can connect
    success = psc._test_pyodbc_connection()
    logger.info(f"DB Connection Successful? : {success}")

    s3 = s3_factory()

    parser = ppp_parser_factory()

    return ParseJSONHandler(logger, psc, parser, s3).handle_event(event)


@app.schedule(every_four_hours)
def polling_ingestor(event: Dict[str, Any]):
    """
        Create a list of SQS messages to be read bby the processor
    """
    logger.info("Called Ingestor")

    sqs = sqs_factory()
    ppp_config = get_ppp_config()
    return PollingIngestor(logger, None, ppp_config, sqs).handle_event(event)


@app.on_sqs_message("ppp_sba_2021_polling_queue.fifo", batch_size=10)
def polling_processor(event: SQSEvent):
    """
    Process a chunk of messages as they are created in the queue
    """
    logger.info("Called Processor")
    
    return PollingProcessor(logger, None, None).handle_event(event)
