from os import getenv
from typing import NamedTuple
from aws_lambda_powertools.utilities import parameters


class AWSConfig(NamedTuple):
    queue_name: str


def get_ssm_values(path):
    return parameters.get_parameters(path, decrypt=True)


def get_aws_config() -> AWSConfig:
    param_name = getenv("CONFIG_SSM_PARAM_NAME")
    params = get_ssm_values(param_name)

    queue_name = str(getenv("POLLING_QUEUE_NAME"))

    return AWSConfig(queue_name=queue_name)
