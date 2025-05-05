'''
    This is a unit test for the logger
'''

import pytest
import os
import shutil
import re
from logging_system_display_python_api.logger import loggerCustom

logger_folder = "logging_system_display_python_api/testing/logs_test/"

@pytest.mark.loggerCustom_tests
def test_logger_init_logs_folder_not_exist(request):
    try:
        shutil.rmtree(logger_folder)
    except FileNotFoundError:
        pass

    loggerCustom(f"{logger_folder}test.txt", log_directory=logger_folder)

    assert os.path.isdir(logger_folder)

    request.addfinalizer(clean_up)

@pytest.mark.loggerCustom_tests
def test_logger_init_logs_folder_does_exist(request):
    try:
        os.mkdir(logger_folder)
    except FileExistsError:
        pass

    loggerCustom(f"{logger_folder}test.txt", log_directory=logger_folder)

    assert os.path.isdir(logger_folder)

    request.addfinalizer(clean_up)

@pytest.mark.loggerCustom_tests
def test_logger_send_log(request):
    test_logger = loggerCustom(f"{logger_folder}test.txt", log_directory=logger_folder)
    test_logger.send_log("this is a log test")

    with open(f"{logger_folder}test.txt", 'r') as file:
        assert re.match(r".*: this is a log test\n", file.read())
    
    request.addfinalizer(clean_up)

@pytest.mark.loggerCustom_tests
def test_logger_send_two_logs(request):
    test_logger = loggerCustom(f"{logger_folder}test.txt", log_directory=logger_folder)
    test_logger.send_log("this is a log test")
    test_logger.send_log("this is another log test")

    with open(f"{logger_folder}test.txt", 'r') as file:
        assert re.match(r".*: this is a log test\n.*: this is another log test\n", file.read())
    
    request.addfinalizer(clean_up)

def clean_up():
    try:
        shutil.rmtree(logger_folder)
    except FileNotFoundError:
        print("flag")
        pass