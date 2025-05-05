import pytest
from logging_system_display_python_api.messageHandler import messageHandler
from threading_python_api.taskHandler import taskHandler
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=import-error

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
from urllib.parse import parse_qs
from datetime import datetime
import time
import random

message_dto = print_message_dto('Hello World')

@pytest.mark.logger_dto_tests
def test__init__():
    assert message_dto._print_message_dto__message == 'Hello World'

def test_get_message():
    assert message_dto.get_message() == 'Hello World'

def test__str__():
    assert str(message_dto) == 'Hello World'