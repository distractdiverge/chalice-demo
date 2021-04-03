import json
from typing import Dict, Any, List
from datetime import datetime

import boto3
from aws_lambda_powertools import Logger

from chalicelib.services.ppp_repository import PPPSummaryRecord

class SQSClient:
    _logger: Logger

    def __init__(self, queue_name: str, logger: Logger):
        self._logger = logger
        sqs = boto3.resource('sqs')
        self._client = sqs.get_queue_by_name(QueueName=queue_name)

    def _from_json(self, input: str) -> PPPSummaryRecord:
      """
      Parse a JSON string into the NamedTuple PPPSummaryRecord

      we need this because a tuple converts to an array, which isn't as readable, 
      so this converts it to an object
      """
      values = json.loads(input)
      return PPPSummaryRecord(
        id=values['id'],
        stage=values['stage'],
        submission_errors=values['submission_errors'],
        async_validation_errors=values['async_validation_errors'],
        hours_since_modified=values['hours_since_modified'],
        hours_since_created=values['hours_since_created']
      )

    def _to_json(self, record: PPPSummaryRecord) -> str:
      """
      Convert a PPPSummaryRecord NamedTuple into a JSON Object & JSON String

      we need this because a tuple converts to an array, which isn't as readable, 
      so this converts it to an object
      """
      return json.dumps({
        'id': record.id,
        'stage': record.stage,
        'submission_errors': record.submission_errors,
        'async_validation_errors': record.async_validation_errors,
        'hours_since_modified': record.hours_since_modified,
        'hours_since_created': record.hours_since_created
      })
    
    def _to_message_attributes(self, record: PPPSummaryRecord) -> Dict[str, Dict[str, str]]:
      return {
        'timestamp': {
          'StringValue': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%-S"),
          'DataType': 'String'
        },
        'hours_since_modified': {
          'StringValue': str(record.hours_since_modified),
          'DataType': 'Number'
        },
        'hours_since_created': {
          'StringValue': str(record.hours_since_created),
          'DataType': 'Number'
        }
      }

    def send_message(self, ppp_summary_record: PPPSummaryRecord) -> bool:
      
      message = self._to_json(ppp_summary_record)
      attributes = self._to_message_attributes(ppp_summary_record)

      success = True
      try:
        self._client.send_message(
          MessageBody=message,
          MessageAttributes=attributes,
          MessageGroupId='1'
        )
        self._logger.info({ 'title': 'Sent Message', 'message': message, 'attributes': attributes})
      except Exception as e:
        self._logger.error({ 'title': 'Error sending message', 'message': message, 'attributes': attributes, 'detail': str(e)})
        success = False
      
      return success

    def read_messages(self) -> List[PPPSummaryRecord]:
      # TODO: Parse messages into PPPSummaryRecords
      for message in self._client.receive_messages():
        record = self._from_json(message.message)
        yield record

    def delete_message(self, message: Any) -> bool:
      success = True
      try:
        message.delete()
      except Exception as ex:
        self._logger.error({'title': 'Error deleting message', 'message': message, 'detail': str(ex) })
        success = False
      
      return success

        
