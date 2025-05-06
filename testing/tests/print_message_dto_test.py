import pytest

from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto

message_dto = print_message_dto('Hello World')

@pytest.mark.logger_dto_tests
def test__init__():
    assert message_dto._print_message_dto__message == 'Hello World'

def test_get_message():
    assert message_dto.get_message() == 'Hello World'

def test__str__():
    assert str(message_dto) == 'Hello World'