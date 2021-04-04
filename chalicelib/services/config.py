from os import getenv
from typing import NamedTuple


class AWSConfig(NamedTuple):
    queue_name: str


def get_aws_config() -> AWSConfig:
    queue_name = str(getenv("POLLING_QUEUE_NAME"))

    return AWSConfig(queue_name=queue_name)
