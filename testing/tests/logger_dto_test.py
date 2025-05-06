import pytest

from logging_system_display_python_api.DTOs.logger_dto import logger_dto

logger = logger_dto('08-06-1945_08:15', 'Hello World')

@pytest.mark.logger_dto_tests
def test__init__():
    assert logger._logger_dto__time == "08-06-1945_08:15"
    assert logger._logger_dto__message == 'Hello World'

def test_get_time():
    assert logger.get_time() == "08-06-1945_08:15"

def test_get_message():
    assert logger.get_message() == 'Hello World'

def test__str__():
    time = "08-06-1945_08:15"
    message = 'Hello World'
    assert str(logger) == f"[{time}, 'blue']: {message}"