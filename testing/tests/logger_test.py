'''
    This is a unit test for the logger
'''

import pytest
import os
import shutil
import re
from logging_system_display_python_api.logger import loggerCustom

logger_folder = "logging_system_display_python_api/testing/logs_test/"

@pytest.mark.logger_tests
def test_logger_init_logs_folder_not_exist():
    try:
        shutil.rmtree(logger_folder)
    except FileNotFoundError:
        pass

    loggerCustom(f"{logger_folder}test.txt", log_directory=logger_folder)

    assert os.path.isdir(logger_folder)

@pytest.mark.logger_tests
def test_logger_init_logs_folder_does_exist():
    try:
        os.mkdir(logger_folder)
    except FileExistsError:
        pass

    loggerCustom(f"{logger_folder}test.txt", log_directory=logger_folder)

    assert os.path.isdir(logger_folder)

@pytest.mark.logger_tests
def test_logger_send_log():
    test_logger = loggerCustom(f"{logger_folder}test.txt", log_directory=logger_folder)
    test_logger.send_log("this is a log test")

    with open(f"{logger_folder}test.txt", 'r') as file:
        assert re.match(r".*: this is a log test\n", file.read())

@pytest.mark.logger_tests
def test_logger_send_two_logs():
    test_logger = loggerCustom(f"{logger_folder}test.txt", log_directory=logger_folder)
    test_logger.send_log("this is a log test")
    test_logger.send_log("this is another log test")

    with open(f"{logger_folder}test.txt", 'r') as file:
        assert re.match(r".*: this is a log test\n.*: this is another log test\n", file.read())