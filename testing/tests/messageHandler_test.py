import pytest

from logging_system_display_python_api.messageHandler import messageHandler
from threading_python_api.taskHandler import taskHandler
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto
from logging_system_display_python_api.DTOs.byte_report import byte_report_dto
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=import-error

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
from urllib.parse import parse_qs
from datetime import datetime
import time
import random

post_received_event = threading.Event()
received_post = ""

# define message handlers
message_handler_local = messageHandler(destination='Local')
message_handler_server = messageHandler(server_name='Test Server', hostname='127.0.0.1', destination='server', display_name="messageHandler test")
message_handler_server._messageHandler__host_url = "127.0.0.1:5000"

# set threadpools
threadpool_local = taskHandler(message_handler_local)
message_handler_local.set_thread_handler(threadpool_local)
threadpool_server = taskHandler(message_handler_server)
message_handler_server.set_thread_handler(threadpool_server)

#define resources
message = print_message_dto("Hello World")
now_str = str(datetime.now())

def assert_keys_checked_and_returned(lock, test_function, args=()):
    # test key check
    lock.acquire(timeout=1)
    with pytest.raises(RuntimeError):
        if args == ():
            test_function()
        else:
            test_function(*args)
    lock.release()

    # test key return
    test_function(*args)
    acquired = lock.acquire(timeout=0.1)  # Try to acquire after the function
    assert acquired

    if acquired:
        lock.release()

class Mock (threadWrapper):
    def __init__(self, coms, thread_name):
        self.__function_dict = {
            'test' : self.test,
            'test_args' : self.test_args
        }
        super().__init__(self.__function_dict)

        self.__coms = coms
        self.__thread_name = thread_name

        self.random_return = random.random()

        self.test_ran = 0
        self.test_args_ran = 0
        self.test_agrs_args = []

    def test(self):
        self.test_ran += 1
        return self.random_return
    
    def test_args(self, foo):
        self.test_args_ran += 1
        self.test_agrs_args.append(foo)
        return foo

@pytest.fixture(scope="session", autouse=True)
def start_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            """Read and validate the JSON data from POST requests"""
            if self.path == '/return_404':
                self.send_response(404)
                self.end_headers()
                return

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

    try:
        yield
    finally:
        server.shutdown()
        server_thread.join()

@pytest.mark.messageHandler_tests
def test__func_dict_all_callable():
    for _key, value in message_handler_local._messageHandler__func_dict.items():
        print(_key, value, callable(value))
        if not callable(value):
            assert False
        
    assert True

@pytest.mark.messageHandler_tests
def test_set_thread_handler():
    assert message_handler_local._messageHandler__thread_handler == threadpool_local

@pytest.mark.messageHandler_tests
def test_send_message_permanent():    
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

    assert_keys_checked_and_returned(message_handler_local._messageHandler__permanent_message_lock, message_handler_local.send_message_permanent, (message, 2))

@pytest.mark.messageHandler_tests
def test_print_message():
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

    assert_keys_checked_and_returned(message_handler_local._messageHandler__print_message_lock, message_handler_local.print_message, (message, 2))

@pytest.mark.messageHandler_tests
def test_report_thread():
    # test local
    message_handler_local.report_thread("Hello World")
    assert message_handler_local._messageHandler__graphics._graphicsHandler__threads_status == "Hello World"

    assert_keys_checked_and_returned(message_handler_local._messageHandler__report_thread_lock, message_handler_local.report_thread, ("Hello World",))

@pytest.mark.messageHandler_tests
def test_report_bytes():
    # define resources
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

    assert_keys_checked_and_returned(message_handler_local._messageHandler__report_bytes_lock, message_handler_local.report_bytes, (byte_report,))

@pytest.mark.messageHandler_tests
def test_report_additional_status(): 
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

    assert_keys_checked_and_returned(message_handler_local._messageHandler__status_lock, message_handler_local.report_additional_status, ("testing", "hello world"))

@pytest.mark.messageHandler_tests
def test_run():
    message_handler = messageHandler(destination='Local')

    threadpool = taskHandler(message_handler)
    message_handler.set_thread_handler(threadpool)

    try:
        # test status
        threadpool.add_thread(message_handler.run, "message handler tests", message_handler)
        threadpool.start()
        assert message_handler.get_status() == "STARTED"
        
        # test with arguments
        message_handler.make_request("send_message_permanent", [message])
        while True:
            try:
                temp = message_handler._messageHandler__graphics._graphicsHandler__messages_permanent[-1]
                assert temp == (2, [message])
                break
            except IndexError:
                time.sleep(0.01)
        
        # test without arguments
        taskID = message_handler.make_request("get_system_emuo")
        temp = message_handler.get_request(taskID)
        while temp is None:
            temp = message_handler.get_request(taskID)
            time.sleep(0.01)
        
        assert temp == message_handler._messageHandler__graphics
    finally:
        threadpool.kill_tasks()
    
@pytest.mark.messageHandler_tests
def test_send_request_and_get_return():
    mock_obj = Mock(message_handler_local, "mock_thread")
    threadpool_local.add_thread(mock_obj.run, "mock_thread", mock_obj)
    threadpool_local.start()

    try:
        # test send
        request_id = message_handler_local.send_request("mock_thread", ["test"])

        i = 0
        while mock_obj.test_ran == 0 and i < 5/0.01:
            time.sleep(0.01)
            i += 1
        assert mock_obj.test_ran == 1

        # test get return
        assert message_handler_local.get_return("mock_thread", request_id) == mock_obj.random_return
    finally:
        threadpool_local.kill_tasks()

@pytest.mark.messageHandler_tests
def test_get_host_name():
    assert message_handler_server.get_host_name() == '127.0.0.1'

    assert_keys_checked_and_returned(message_handler_server._messageHandler__hostName_lock, message_handler_server.get_host_name)

@pytest.mark.messageHandler_tests
def test_create_tap():
    def fake_function():
        pass

    message_handler_local.create_tap((fake_function, "test"))

    assert message_handler_local._messageHandler__tap_requests[-1] == fake_function
    assert message_handler_local._messageHandler__subscriber[-1] == "test"

@pytest.mark.messageHandler_tests
def test_set_host_url():
    message_handler_local.set_host_url(('127.0.0.1',))
    assert message_handler_local._messageHandler__host_url == '127.0.0.1'

    assert_keys_checked_and_returned(message_handler_local._messageHandler__host_url_lock, message_handler_local.set_host_url, ('127.0.0.1',))

@pytest.mark.messageHandler_tests
def test_send_post():
    # test no temp_url
    value = message_handler_local.send_post(({'foo': 'bar', 'answer': 42}, '/test'))
    assert value is None

    # test temp_url and request == "NA"
    message_handler_local.set_host_url(('127.0.0.1:5000',))
    value = message_handler_local.send_post(({'foo': 'bar', 'answer': 42},))
    assert value.status_code == 200

    # test temp_url and request != "NA"
    value = message_handler_local.send_post(({'foo': 'bar', 'answer': 42}, '/test'))
    assert value.status_code == 200

    # test responce code not 200
    value = message_handler_local.send_post(({'foo': 'bar', 'answer': 42},'/return_404'))
    assert value.status_code == 404

    assert_keys_checked_and_returned(message_handler_local._messageHandler__host_url_lock, message_handler_local.send_post, ("trash",))