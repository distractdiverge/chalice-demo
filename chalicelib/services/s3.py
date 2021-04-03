import boto3
import json
from typing import Dict, Any
from aws_lambda_powertools import Logger


class S3Client:
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def get_categories(self):
        return ["Submissions", "StatusUpdates", "Rescissions"]

    def build_path(self, category, date, filename):
        stage = "prod"
        group_name = "PPPOrigination"
        return f"{stage}/{group_name}/{category}/{date}/{filename}"

    def read_file(self, bucket_name: str, keypath: str) -> str:
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        file_object = bucket.Object(key=keypath)
        response = file_object.get()

        lines = response["Body"].read()

        return lines

    def read_json_file(self, bucket_name: str, keypath: str) -> Dict[str, Any]:
        content = self.read_file(bucket_name, keypath)
        json_content = json.loads(content)
        return json_content
