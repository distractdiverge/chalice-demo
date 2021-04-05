import json
import pytest

from tests.stubs.utilities import read_json_file

@pytest.fixture
def logger(mocker):
    stub_logger = mocker.MagicMock(name="StubLogger")
    stub_logger.info.return_value = None
    stub_logger.warn.return_value = None
    stub_logger.error.return_value = None
    stub_logger.debug.return_value = None
    return stub_logger

@pytest.fixture
def sns_event():
    return read_json_file("/samples/sns_event.json")

