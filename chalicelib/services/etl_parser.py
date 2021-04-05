import json

from typing import Dict, Any, NamedTuple, Union

from aws_lambda_powertools import Logger


class ETLResponse(NamedTuple):
    message: str
    payload: Dict[str, Any]


class ETLParser:
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def _parse_json_string(self, input: str) -> Union[Dict[str,Any], None]:
        result = None
        try:
            result = json.loads(input)
        except Exception as e:
            self._logger.error({"message": "Error parsing input", "exception": str(e)})

        return result

    def parse(self, input: str) -> Union[ETLResponse, None]:
        self._logger.info("Parsing record")

        result = self._parse_json_string(input)

        if result is None:
            raise Exception("Error, could not parse input")

        return ETLResponse(message=result, payload=input)
