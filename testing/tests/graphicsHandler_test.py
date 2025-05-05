import pytest
from logging_system_display_python_api.messageHandler import messageHandler
from threading_python_api.taskHandler import taskHandler
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto
from logging_system_display_python_api.DTOs.byte_report import byte_report_dto
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=import-error
from logging_system_display_python_api.graphicsHandler import graphicsHandler

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
from urllib.parse import parse_qs
from datetime import datetime
import time
import random

class fakeComs():
    def __init__(self):
        self.server_name = None
        self.messages = []
    def send_request(self, server_name, messages):
        self.server_name = server_name
        self.messages = messages

fake_coms_obj = fakeComs()
graphics_handler = graphicsHandler(coms=fake_coms_obj, server_name='test server')

@pytest.mark.graphicsHandler_tests
def test_write_message_log():
    graphics_handler.write_message_log()

    assert fake_coms_obj.server_name == 'test server'
    assert fake_coms_obj.messages[0] == 'write_message_log'
    assert fake_coms_obj.messages[1][0].get_message() == 'Graphics handler started'

@pytest.mark.graphicsHandler_tests
def test_send_message():
    message = print_message_dto('hello world')
    graphics_handler.send_message(23, message)

    last_message = graphics_handler._graphicsHandler__messages[-1]

    assert last_message[0] == 23
    assert last_message[1].get_message() == 'hello world'

    for x in range(15):
        graphics_handler.send_message(x, message)

    assert len(graphics_handler._graphicsHandler__messages) == 9

@pytest.mark.graphicsHandler_tests
def test_send_message_permanent():
    message = print_message_dto('hello world')
    graphics_handler.send_message_permanent(2, message)

    last_message = graphics_handler._graphicsHandler__messages_permanent[-1]

    assert last_message[0] == 2
    assert last_message[1] == message

@pytest.mark.graphicsHandler_tests
def test_write_message_permanent_log():
    message = print_message_dto('hello world')
    graphics_handler.send_message_permanent(2, message)

    graphics_handler.write_message_permanent_log()

    assert fake_coms_obj.server_name == 'test server'
    assert fake_coms_obj.messages[0] == 'write_prem_message_log'
    assert fake_coms_obj.messages[1][-1].get_message() == 'hello world'

@pytest.mark.graphicsHandler_tests
def test_report_thread():
    graphics_handler.report_thread(['testing'])

    assert graphics_handler._graphicsHandler__threads_status == ['testing']

@pytest.mark.graphicsHandler_tests
def test_write_thread_report():
    graphics_handler.report_thread(['testing'])
    graphics_handler.write_thread_report()
    
    assert fake_coms_obj.server_name == 'test server'
    assert fake_coms_obj.messages[0] == 'thread_report'
    assert fake_coms_obj.messages[1] == ['testing']

    assert graphics_handler._graphicsHandler__threads_status == []