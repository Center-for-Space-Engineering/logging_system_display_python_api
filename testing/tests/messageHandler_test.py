'''
    This is a unit test for the logger
'''

import pytest
from logging_system_display_python_api.messageHandler import messageHandler
from threading_python_api.taskHandler import taskHandler
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto
from logging_system_display_python_api.DTOs.byte_report import byte_report_dto

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
from urllib.parse import parse_qs
from datetime import datetime

post_received_event = threading.Event()
received_post = ""

@pytest.fixture(scope="session", autouse=True)
def start_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            """Read and validate the JSON data from POST requests"""
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            try:
                received_data = json.loads(post_data)  # Parse JSON
            except json.JSONDecodeError:
                received_data = parse_qs(post_data) # Parse form data

            global received_post
            received_post = received_data

            self.send_response(200)
            self.end_headers()

            post_received_event.set()
    
    server = HTTPServer(("127.0.0.1", 5000), SimpleHandler)

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    yield

    server.shutdown()
    server_thread.join()

@pytest.mark.messageHandler_tests
def test__func_dict_all_callable():
    message_handler = messageHandler()

    for _key, value in message_handler._messageHandler__func_dict.items():
        print(_key, value, callable(value))
        if not callable(value):
            assert False
        
    assert True

@pytest.mark.messageHandler_tests
def test_set_thread_handler():
    message_handler = messageHandler()

    threadpool = taskHandler(message_handler)
    message_handler.set_thread_handler(threadpool)

    assert message_handler._messageHandler__thread_handler == threadpool

@pytest.mark.messageHandler_tests
def test_send_message_permanent():
    # define message handlers
    message_handler_local = messageHandler(destination='Local')
    message_handler_server = messageHandler(server_name='Test Server', hostname='127.0.0.1', destination='server', display_name="messageHandler test")
    message_handler_server._messageHandler__host_url = "127.0.0.1:5000"

    # define resources
    message = print_message_dto("Hello World")
    
    # test local
    message_handler_local.send_message_permanent(message, typeM=2)
    assert message_handler_local._messageHandler__graphics._graphicsHandler__messages_permanent[-1] == (2, message)

    # test server
    message_handler_server.send_message_permanent(message, typeM=2)
    post_received_event.wait()

    expected_data = {
        'sender' : ['127.0.0.1'],
        'Display_name' : ['messageHandler test'],
        'function' : ['send_message_permanent'],
        'message' : ['Hello World'], 
        'type' : ['2'],
    }

    assert received_post == expected_data

    # test key check
    message_handler_local._messageHandler__permanent_message_lock.acquire()
    with pytest.raises(RuntimeError):
        message_handler_local.send_message_permanent(message, typeM=2)
    message_handler_local._messageHandler__permanent_message_lock.release()

    # test key return
    assert not message_handler_local._messageHandler__permanent_message_lock.locked()

@pytest.mark.messageHandler_tests
def test_print_message():
    # define message handlers
    message_handler_local = messageHandler(destination='Local')
    message_handler_server = messageHandler(server_name='Test Server', hostname='127.0.0.1', destination='server', display_name="messageHandler test")
    message_handler_server._messageHandler__host_url = "127.0.0.1:5000"

    # define resources
    message = print_message_dto("Hello World")
    
    # test local
    message_handler_local.print_message(message, typeM=2)
    message_handler_messages = message_handler_local._messageHandler__graphics._graphicsHandler__messages
    assert message_handler_messages[-1][0] == 2
    assert message_handler_messages[-1][1].get_message() ==  message.get_message()

    # test server
    message_handler_server.print_message(message, typeM=2)

    post_received_event.wait()

    expected_data = {
        'sender' : ['127.0.0.1'],
        'Display_name' : ['messageHandler test'],
        'function' : ['print_message'],
        'message' : ['Hello World'], 
        'type' : ['2'],
    }

    assert received_post == expected_data

    # test key check
    message_handler_local._messageHandler__print_message_lock.acquire()
    with pytest.raises(RuntimeError):
        message_handler_local.print_message(message, typeM=2)
    message_handler_local._messageHandler__print_message_lock.release()

    # test key return
    assert not message_handler_local._messageHandler__print_message_lock.locked()

@pytest.mark.messageHandler_tests
def test_report_thread():
    # define message handlers
    message_handler_local = messageHandler(destination='Local')
    message_handler_server = messageHandler(server_name='Test Server', hostname='127.0.0.1', destination='server', display_name="messageHandler test")
    message_handler_server._messageHandler__host_url = "127.0.0.1:5000"
    
    # test local
    message_handler_local.report_thread("Hello World")
    assert message_handler_local._messageHandler__graphics._graphicsHandler__threads_status == "Hello World"

    # test key check
    message_handler_local._messageHandler__report_thread_lock.acquire()
    with pytest.raises(RuntimeError):
        message_handler_local.report_thread("Hello World")
    message_handler_local._messageHandler__report_thread_lock.release()

    # test key return
    assert not message_handler_local._messageHandler__report_thread_lock.locked()

@pytest.mark.messageHandler_tests
def test_report_bytes():
    # define message handlers
    message_handler_local = messageHandler(destination='Local')
    message_handler_server = messageHandler(server_name='Test Server', hostname='127.0.0.1', destination='server', display_name="messageHandler test")
    message_handler_server._messageHandler__host_url = "127.0.0.1:5000"

    # define resources
    threadpool_local = taskHandler(message_handler_local)
    message_handler_local.set_thread_handler(threadpool_local)
    threadpool_server = taskHandler(message_handler_server)
    message_handler_server.set_thread_handler(threadpool_server)
    now_str = str(datetime.now())
    byte_report = byte_report_dto("testing", now_str, 42)
    
    # test local
    message_handler_local.report_bytes(byte_report)
    assert message_handler_local._messageHandler__graphics._graphicsHandler__byte_report[-1] == str(byte_report)
    
    # test server
    message_handler_server.report_bytes(byte_report)

    post_received_event.wait()

    expected_data = {
        'sender' : ['127.0.0.1'],
        'Display_name' : ['messageHandler test'],
        'message': ['42'],
        'type': ['report_bytes'],
        'function': ['report_bytes'],
        'thread_name': ['testing'],
        'time': [now_str]
    }

    assert received_post == expected_data

    # test key check
    message_handler_local._messageHandler__report_bytes_lock.acquire()
    with pytest.raises(RuntimeError):
        message_handler_local.report_bytes(byte_report)
    message_handler_local._messageHandler__report_bytes_lock.release()

    # test key return
    assert not message_handler_local._messageHandler__print_message_lock.locked()

@pytest.mark.messageHandler_tests
def test_report_additional_status_local():
    # define message handlers
    message_handler_local = messageHandler(destination='Local')
    message_handler_server = messageHandler(server_name='Test Server', hostname='127.0.0.1', destination='server', display_name="messageHandler test")
    message_handler_server._messageHandler__host_url = "127.0.0.1:5000"

    # define resources
    threadpool_local = taskHandler(message_handler_local)
    message_handler_local.set_thread_handler(threadpool_local)
    threadpool_server = taskHandler(message_handler_server)
    message_handler_server.set_thread_handler(threadpool_server)
    
    # test local
    message_handler_local.report_additional_status("testing", "hello world")
    assert message_handler_local._messageHandler__graphics._graphicsHandler__status_message["testing"] == "hello world"
    
    # test server
    message_handler_server.report_additional_status("testing", "hello world")

    post_received_event.wait()

    expected_data = {
        'sender' : ['127.0.0.1'],
        'Display_name' : ['messageHandler test'],
        'request' : ['report_additional_status'],
        'message' : ["hello world"],
    }

    assert received_post == expected_data

    # test key check
    message_handler_local._messageHandler__status_lock.acquire()
    with pytest.raises(RuntimeError):
        message_handler_local.report_additional_status("testing", "hello world")
    message_handler_local._messageHandler__status_lock.release()

    # test key return
    assert not message_handler_local._messageHandler__report_bytes_lock.locked()