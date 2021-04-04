import json
from typing import Dict, Any, List
from datetime import datetime

import boto3
from aws_lambda_powertools import Logger

class SQSClient:
    _logger: Logger

    def __init__(self, queue_name: str, logger: Logger):
        self._logger = logger
        sqs = boto3.resource("sqs")
        self._client = sqs.get_queue_by_name(QueueName=queue_name)

    def send_message(self, msg: str) -> bool:
        message = f'MSG: {msg}'

        success = True
        try:
            self._client.send_message(
                MessageBody=message, MessageGroupId="1"
            )
            self._logger.info(
                {"title": "Sent Message", "message": message}
            )
        except Exception as e:
            self._logger.error({
                "title": "Error sending message",
                "message": message,
                "detail": str(e),
            })
            success = False

        return success

    def read_messages(self) -> List[str]:
        msgs = []
        for message in self._client.receive_messages():
            record = message.message
            msgs.append(record)
        return msgs

    def delete_message(self, message: Any) -> bool:
        success = True
        try:
            message.delete()
        except Exception as ex:
            self._logger.error({
                "title": "Error deleting message",
                "message": message,
                "detail": str(ex),
            })
            success = False

        return success
