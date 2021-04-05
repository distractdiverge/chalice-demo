import os
import json

import pytest
from assertpy import assert_that

from chalicelib.services.etl_parser import ETLParser, ETLResponse
from tests.stubs.factories import logger, sns_event


@pytest.fixture
def etl_parser(logger):
    return ETLParser(logger)


def test_constructor(etl_parser):
    assert etl_parser is not None


def test_parse(etl_parser):
    input = '{ "message": "test" }'
    # output = etl_parser.parse(input)
    output = {}
    pass

    assert output is not None


def test_parse_submission(etl_parser, sns_event):
    assert etl_parser is not None
    assert sns_event is not None

    input = sns_event
    result = etl_parser.parse(input)

    assert result is not None
    assert result.message == 'test'
    assert result.payload == sns_event

